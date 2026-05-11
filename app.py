from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    salt = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

@app.route('/')
def index():
    return render_template("home.html")

bcrypt = Bcrypt(app)