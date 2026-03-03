import os
from dotenv import load_dotenv
from flask import send_from_directory
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, redirect, url_for, flash, session, jsonify
from b2sdk.v2 import InMemoryAccountInfo, B2Api

load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["MYSQL_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ["FLASK_SECRET_KEY"]

db = SQLAlchemy(app)

# For safely storing private assets

# Initialize B2 API
info = InMemoryAccountInfo()
b2_api = B2Api(info)

# Authorize with keys from environment variables
b2_api.authorize_account(
    "production",
    os.environ["B2_KEY_ID"],
    os.environ["B2_APP_KEY"]
)

# Connect to your bucket
bucket = b2_api.get_bucket_by_name("skating-assets")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.Text, nullable=False)
    admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'id: {self.id}, name: {self.first_name} {self.last_name}, email: {self.email}, phone: {self.phone}'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)    
    day = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'id: {self.id}, name: {self.name}, day: {self.day}, time: {self.time}'

class Officer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    major = db.Column(db.String(100), nullable=False)
    photo_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'id: {self.id}, name: {self.name}, role: {self.role}, major: {self.major}'

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'id: {self.id}, file_name: {self.file_name}'

class DateException(db.Model):
    __tablename__ = 'date_exception'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

def load_events():
    return Event.query.all()
    	
def load_officers():
    return Officer.query.all()

def load_images():
    return Image.query.all()

@app.route("/")
def home():
    return render_template("home.html", images=load_images())

@app.route("/schedule")
def schedule():
    days = ['S', 'M', 'T', 'W', 'T', 'F', 'S']
    return render_template("schedule.html", events=load_events(), days=days)

@app.route("/officers")
def officers():
    """
    officers = Officer.query.all()

    # Generate signed URLs for display only
    for officer in officers:
        if officer.photo_url:  # this should be the file name, e.g., 'caleb_elder.jpg'
            officer.photo_url = bucket.get_download_url(officer.photo_url)

    return render_template("officers.html", officers=officers)
    """
    officers = Officer.query.all()

    for officer in officers:
        if officer.photo_url:
            token = bucket.get_download_authorization(
                file_name_prefix=officer.photo_url,
                valid_duration_in_seconds=3600
            )
            base_url = bucket.get_download_url(officer.photo_url)
            officer.photo_url = f"{base_url}?Authorization={token}"
            
    return render_template("officers.html", officers=officers)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("first-name")
        last_name = request.form.get("last-name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
        elif User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
        else:
            new_user = User(first_name=first_name, last_name=last_name, email=email, phone=phone)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user is None:
            flash("No account found with that email.", "error")
        elif not user.check_password(password):
            flash("Incorrect password.", "error")
        else:
            session['user_id'] = user.id
            session['first_name'] = user.first_name
            session['last_name'] = user.last_name
            session['admin'] = user.admin
            return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/update_calendar", methods=["POST"])
def update_calendar():
    data = request.get_json()
    day = data['day']
    month = data['month']
    year = data['year']

    if data['add'] == True:
        db.session.add(DateException(day=day, month=month, year=year))
        db.session.commit()
    else:
        date = DateException.query.filter_by(day=day, month=month, year=year).first()
        db.session.delete(date)
        db.session.commit()

    return {"status": "success"}, 200

@app.route("/update_month", methods=["POST"])
def update_month():
    data = request.get_json()
    month = data['month']
    year = data['year']

    dates = DateException.query.filter_by(month=month, year=year)
    
    days = [d.day for d in dates]

    return jsonify({
        "days": days
    })

@app.route("/is_admin")
def is_admin():
    admin = session.get("admin", False)
    return jsonify({"admin": admin})

@app.route('/private_assets/<path:filename>')
def private_assets(filename):
    folder_path = os.path.join(app.root_path, 'private_assets')
    return send_from_directory(folder_path, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # default to 5000 locally
    app.run(host="0.0.0.0", port=port)

