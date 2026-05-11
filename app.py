from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    salt = db.Column(db.String, nullable=False)
    passwordHash = db.Column(db.String, nullable=False)

@app.route('/')
def index():
    return render_template("home.html")

bcrypt = Bcrypt(app)