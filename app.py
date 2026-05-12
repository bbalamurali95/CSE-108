from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, set_access_cookies, create_access_token, jwt_required, get_jwt_identity

from dotenv import load_dotenv
import os
import random

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

tournament_participants = db.Table('tournament_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('tournament_id', db.Integer, db.ForeignKey('tournament.id'), primary_key=True)
)

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    game = db.Column(db.String, nullable=False)
    participants = db.relationship('User', secondary=tournament_participants, backref='tournaments')

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    
    grid_class = db.Column(db.String(20), nullable=False)
    
    player1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    player2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    winner_next_match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=True)
    loser_next_match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=True)
    
    player1 = db.relationship('User', foreign_keys=[player1_id])
    player2 = db.relationship('User', foreign_keys=[player2_id])

def initialize_bracket_slots(tournament_id):
    # Define the required slots based on your CSS grid classes
    upper_slots = [
        'u-r1-m1', 'u-r1-m2', 'u-r1-m3', 'u-r1-m4', 'u-r1-m5', 'u-r1-m6', 'u-r1-m7', 'u-r1-m8',
        'u-r2-m1', 'u-r2-m2', 'u-r2-m3', 'u-r2-m4',
        'u-r3-m1', 'u-r3-m2',
        'u-r4-m1', 'u-gf'
    ]
    
    lower_slots = [
        'l-r1-m1', 'l-r1-m2', 'l-r1-m3', 'l-r1-m4',
        'l-r2-m1', 'l-r2-m2', 'l-r2-m3', 'l-r2-m4',
        'l-r3-m1', 'l-r3-m2',
        'l-r4-m1', 'l-r5-m1'
    ]

    for slot in upper_slots + lower_slots:
        match = Match(tournament_id=tournament_id, grid_class=slot)
        db.session.add(match)
    
    db.session.commit()

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
    
    # Initialize empty lists
    upper_matches = []
    lower_matches = []

    if latest_tourney:
        # Fetch all matches for this tournament
        all_matches = Match.query.filter_by(tournament_id=latest_tourney.id).all()
        
        # Split them based on their grid class (e.g. 'u-r1-m1' vs 'l-r1-m1')
        for match in all_matches:
            if match.grid_class.startswith('u-'):
                upper_matches.append(match)
            elif match.grid_class.startswith('l-'):
                lower_matches.append(match)

    return render_template(
        "tournament.html", 
        active_tournament=latest_tourney, 
        is_admin=is_admin_flag,
        upper_matches=upper_matches,
        lower_matches=lower_matches
    )

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
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    new_tourney = Tournament(
        name=data.get("name"),
        game=data.get("game")
    )
    
    db.session.add(new_tourney)
    db.session.commit()
    
    # After creating the tournament, we need to initialize the match slots
    initialize_bracket_slots(new_tourney.id)
    
    return jsonify({"message": "Local tournament and bracket slots created!"}), 201

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
    
    # Add the user to the participant list if they aren't already in it
    if user not in tournament.participants:
        tournament.participants.append(user)
        db.session.commit()
        return jsonify({"message": f"Successfully joined {tournament.name}!"}), 200
    
    return jsonify({"message": "You are already in this tournament"}), 200

@app.route("/start_tournament", methods=['POST'])
@jwt_required()
def start_tournament():
    current_user_id = get_jwt_identity()
    admin = User.query.get(current_user_id)
    if not admin or not admin.is_admin:
        return jsonify({"error": "Admin only"}), 403

    data = request.get_json()
    tourney_id = data.get("tournament_id")
    tournament = Tournament.query.get(tourney_id)
    
    # 1. Get and shuffle participants
    players = tournament.participants
    random.shuffle(players)

    # 2. Find the 8 first-round matches (u-r1-m1 to u-r1-m8)
    r1_matches = Match.query.filter_by(tournament_id=tourney_id).filter(Match.grid_class.like('u-r1-m%')).order_by(Match.grid_class).all()

    # 3. Seat the players
    player_index = 0
    for match in r1_matches:
        if player_index < len(players):
            match.player1_id = players[player_index].id
            player_index += 1
        if player_index < len(players):
            match.player2_id = players[player_index].id
            player_index += 1
        
        # 4. Handle "Byes"
        # If player 2 is empty, player 1 automatically wins
        if match.player1_id and not match.player2_id:
            match.winner_id = match.player1_id
    
    db.session.commit()
    return jsonify({"message": "Tournament started and players seeded!"}), 200

@app.route("/report_winner", methods=['POST'])
@jwt_required()
def report_winner():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    match = Match.query.get(data.get("match_id"))
    winner_id = data.get("winner_id")
    
    if not match:
        return jsonify({"error": "Match not found"}), 404

    # 1. Set the winner of the current match
    match.winner_id = winner_id
    loser_id = match.player2_id if winner_id == match.player1_id else match.player1_id

    # 2. Define the Routing Map
    # format: 'current_grid_class': (winner_next_class, winner_slot, loser_next_class, loser_slot)
    routing = {
        # Winners Round 1
        'u-r1-m1': ('u-r2-m1', 'p1', 'l-r1-m1', 'p1'),
        'u-r1-m2': ('u-r2-m1', 'p2', 'l-r1-m1', 'p2'),
        'u-r1-m3': ('u-r2-m2', 'p1', 'l-r1-m2', 'p1'),
        'u-r1-m4': ('u-r2-m2', 'p2', 'l-r1-m2', 'p2'),
        'u-r1-m5': ('u-r2-m3', 'p1', 'l-r1-m3', 'p1'),
        'u-r1-m6': ('u-r2-m3', 'p2', 'l-r1-m3', 'p2'),
        'u-r1-m7': ('u-r2-m4', 'p1', 'l-r1-m4', 'p1'),
        'u-r1-m8': ('u-r2-m4', 'p2', 'l-r1-m4', 'p2'),

        # Winners Round 2 (Quarter-Finals)
        'u-r2-m1': ('u-r3-m1', 'p1', 'l-r2-m1', 'p1'),
        'u-r2-m2': ('u-r3-m1', 'p2', 'l-r2-m2', 'p1'),
        'u-r2-m3': ('u-r3-m2', 'p1', 'l-r2-m3', 'p1'),
        'u-r2-m4': ('u-r3-m2', 'p2', 'l-r2-m4', 'p1'),

        # Winners Round 3 (Semi-Finals)
        'u-r3-m1': ('u-r4-m1', 'p1', 'l-r4-m1', 'p1'),
        'u-r3-m2': ('u-r4-m1', 'p2', 'l-r5-m1', 'p1'), 

        # Winners Final
        'u-r4-m1': ('u-gf', 'p1', 'l-r5-m1', 'p2'), 

        # LOWER BRACKET (Losers are eliminated, so they get "None")
        'l-r1-m1': ('l-r2-m1', 'p2', None, None),
        'l-r1-m2': ('l-r2-m2', 'p2', None, None),
        'l-r1-m3': ('l-r2-m3', 'p2', None, None),
        'l-r1-m4': ('l-r2-m4', 'p2', None, None),

        'l-r2-m1': ('l-r3-m1', 'p1', None, None),
        'l-r2-m2': ('l-r3-m1', 'p2', None, None),
        'l-r2-m3': ('l-r3-m2', 'p1', None, None),
        'l-r2-m4': ('l-r3-m2', 'p2', None, None),

        'l-r3-m1': ('l-r4-m1', 'p2', None, None),
        'l-r3-m2': ('l-r5-m1', 'p1', None, None),

        'l-r4-m1': ('l-r5-m1', 'p2', None, None),
        
        # Losers Final feeds back into Grand Final
        'l-r5-m1': ('u-gf', 'p2', None, None)
    }

    route = routing.get(match.grid_class)
    if route:
        w_class, w_slot, l_class, l_slot = route
        
        # Advance Winner
        w_next = Match.query.filter_by(tournament_id=match.tournament_id, grid_class=w_class).first()
        if w_next:
            if w_slot == 'p1': w_next.player1_id = winner_id
            else: w_next.player2_id = winner_id

        # Drop Loser to Losers Bracket
        if l_class:
            l_next = Match.query.filter_by(tournament_id=match.tournament_id, grid_class=l_class).first()
            if l_next:
                if l_slot == 'p1': l_next.player1_id = loser_id
                else: l_next.player2_id = loser_id

    db.session.commit()
    return jsonify({"message": "Bracket updated!"}), 200

if __name__ == '__main__':
    app.run(debug = True, port = 5000)