from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, set_access_cookies, create_access_token

from dotenv import load_dotenv
import os
import requests

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
    gg_wins = db.Column(db.Integer, default=0, nullable=False)
    sf6_wins = db.Column(db.Integer, default=0, nullable=False)
    t8_wins = db.Column(db.Integer, default=0, nullable=False)

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    challonge_url = db.Column(db.String, nullable=False)

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
    user = User(username = username, hash = hashed_pw);
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

@app.route("/create_tournament", methods=['POST'])
def create_tournament():
    data = request.get_json()
    tourney_name = data.get("name")
    tourney_url = data.get("url")

    api_key = "4b8f7c8d9794364afdeb014adb305c3392cad7a108cc1d44"

    payload = {
        "api_key" : api_key,
        "tournament" : {
            "name" : tourney_name,
            "tournament_type" : "double elimination",
            "url" : tourney_url
        }
    }

    response = requests.post("http://api.challonge.com/v1/tournaments.json", json=payload)

    if response.status_code == 200:
        data = response.json()
        full_url = data['tournament']['full_challonge_url']
        new_tourney = Tournament(name=tourney_name, challonge_url=full_url)
        db.session.add(new_tourney)
        db.session.commit()
        return jsonify({"message": "Tournament created!", "url": full_url}), 201
    else:
        return jsonify({"error": "Failed to create tournament"}), 400

if __name__ == '__main__':
    app.run(debug = True, port = 5000)