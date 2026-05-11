from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    hash = db.Column(db.String, nullable=False)

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/register", methods=['POST'])
def register():
    new_data = request.get_json()
    username = new_data.get("username")
    password = new_data.get("password")

    hashed_pw  = bcrypt.generate_password_hash(\
        password
    ).decode("utf-8")

    if User.query.filter_by(username = username).first():
        if username and password:
            return jsonify({"error" : "User already exists"}), 400
        user = User(username = username, hash = hashed_pw)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message" : f"User {username} created successfully"}), 201
    else:
        return jsonify({"error" : "Missing username or password"}), 400