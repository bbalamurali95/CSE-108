from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, set_access_cookies, create_access_token

from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    hash = db.Column(db.String, nullable=False)
    gg_wins = db.Column(db.Integer, nullable=False)
    sf6_wins = db.Column(db.Integer, nullable=False)
    t8_wins = db.Column(db.Integer, nullable=False)

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/calendar")
def calendar_page():
    return render_template("calendar.html")

@app.route("/chat")
def chat_page():
    return render_template("chat.html")

@app.route("/tournament")
def tournament_page():
    return render_template("tournament.html")

@app.route("/leaderboard")
def leaderboard_page():
    return render_template("leaderboard.html")

@app.route("/t_register")
def t_register():
    return render_template("register.html")

@app.route("/register", methods=['POST'])
def register():
    new_data = request.get_json()
    username = new_data.get("username")
    password = new_data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    if User.query.filter_by(username = username).first():
        return jsonify({"error": "User already exists"}), 400

    hashed_pw  = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")
    user = User(username = username, hash = hashed_pw, gg_wins = 0, sf6_wins = 0, t8_wins = 0)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": f"User {username} created successfully"}), 201
    
@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username = data.get("username")).first()

    if not user or bcrypt.check_password_hash(user.hash, data.get("password")) == False:
        return jsonify({"error" : "Invalid username or password"}), 401
    
    access_token = create_access_token(identity = user.id)

    response = jsonify({"message" : "Login successful"})
    set_access_cookies(response, access_token)
    return response, 200

if __name__ == '__main__':
    app.run(debug = True, port = 5000)