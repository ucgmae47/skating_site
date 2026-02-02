from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, redirect, url_for, flash, session

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///skating.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "ucgmae47"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)

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

def load_events():
    return Event.query.all()
    	
def load_officers():
    return Officer.query.all()

@app.route("/home")
def home():
    return render_template("home.html", events=load_events())

@app.route("/schedule")
def schedule():
    return render_template("schedule.html", events=load_events())

@app.route("/officers")
def officers():
    return render_template("officers.html", officers=load_officers())

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
            return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

