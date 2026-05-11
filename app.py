from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("frontpage.html")

bcrypt = Bcrypt(app)