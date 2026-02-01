from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///skating.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

HELLO
