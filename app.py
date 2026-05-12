from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, set_access_cookies, create_access_token, jwt_required, get_jwt_identity

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
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    game = db.Column(db.String, nullable=False)
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
@jwt_required(optional=True)
def tournament_page():
    is_admin_flag = False
    current_user_id = get_jwt_identity()
    
    if current_user_id:
        user = User.query.get(current_user_id)
        if user and user.is_admin:
            is_admin_flag = True

    latest_tourney = Tournament.query.order_by(Tournament.id.desc()).first()

    return render_template("tournament.html", active_tournament=latest_tourney, is_admin=is_admin_flag)

@app.route("/leaderboard")
def leaderboard_page():
    return render_template("leaderboard.html")

@app.route("/t_register")
def t_register():
    active_tournaments = Tournament.query.all()
    return render_template("register.html", tournaments = active_tournaments)

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
    
    access_token = create_access_token(identity = str(user.id))

    response = jsonify({"message" : "Login successful"})
    set_access_cookies(response, access_token)
    return response, 200

@app.route("/create_tournament", methods=['POST'])
@jwt_required()
def create_tournament():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_admin:
        return jsonify({"error": "Unauthorized. Admins only"}), 403

    data = request.get_json()
    tourney_name = data.get("name")
    tourney_url = data.get("url")
    tourney_game = data.get("game")

    api_key = os.getenv("CHALLONGE_API_KEY")
    
    if not api_key:
        return jsonify({"error": "API Key is missing. Restart your Flask server!"}), 500

    payload = {
        "api_key": api_key,
        "tournament[name]": tourney_name,
        "tournament[tournament_type]": "double elimination",
        "tournament[url]": tourney_url
    }

    headers = {
        "User-Agent": "FGC-Web-App/1.0"
    }

    response = requests.post("https://api.challonge.com/v1/tournaments.json", data=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        full_url = data['tournament']['full_challonge_url']
        new_tourney = Tournament(name=tourney_name, game=tourney_game, challonge_url=full_url)
        db.session.add(new_tourney)
        db.session.commit()
        return jsonify({"message": "Tournament created!", "url": full_url}), 201
    else:
        print("CHALLONGE API REJECT REQUEST: ", response.text)
        return jsonify({"error": f"Creation failed: {response.text}"}), 400
    
@app.route("/join_tournament", methods=['POST'])
@jwt_required()
def join_tournament():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    data = request.get_json()
    tourney_id = data.get("tournament_id")

    tournament = Tournament.query.get(tourney_id)
    if not tournament:
        return jsonify({"error": "Tournament not found"}), 404
    
    challonge_url_id = tournament.challonge_url.split('/')[-1]
    api_key = os.getenv("CHALLONGE_API_KEY")

    if not api_key:
        return jsonify({"error": "API Key is missing. Restart your Flask server!"}), 500

    payload = {
        "api_key" : api_key,
        "participant[name]" : user.username
    }
    
    headers = {
        "User-Agent": "FGC-Web-App/1.0"
    }

    url = f"https://api.challonge.com/v1/tournaments/{challonge_url_id}/participants.json"
    
    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        return jsonify({"message": f"Successfully joined {tournament.name}"}), 200
    else:
        print("JOIN FAILED: ", response.text)
        return jsonify({"error": f"Failed to join bracket: {response.text}"}), 400

if __name__ == '__main__':
    app.run(debug = True, port = 5000)