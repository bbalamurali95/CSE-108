from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, set_access_cookies, create_access_token, verify_jwt_in_request, get_jwt_identity, unset_jwt_cookies, jwt_required, get_jwt_identity

from dotenv import load_dotenv
import os
import random

app = Flask(__name__)

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
app.config['JWT_COOKIE_SECURE'] = False

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

tournament_participants = db.Tabletournament_participants = db.Table('tournament_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('tournament_id', db.Integer, db.ForeignKey('tournament.id'), primary_key=True)
)

def is_logged_in():
    try:
        verify_jwt_in_request(optional=True)
        return get_jwt_identity() is not None
    except:
        return False
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
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            user = User.query.get(int(user_id))  # convert back to int
            return render_template("home.html", username=user.username, logged_in=True)
    except Exception as e:
        print("JWT Error:", e)
    return render_template("home.html", logged_in=False)

@app.route("/login")
def login_page():
    return render_template("login.html", logged_in=is_logged_in())

@app.route("/signup")
def signup_page():
    return render_template("signup.html", logged_in=is_logged_in())

@app.route("/calendar")
def calendar_page():
    return render_template("calendar.html", logged_in=is_logged_in())

@app.route("/chat")
def chat_page():
    return render_template("chat.html", logged_in=is_logged_in())

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
    player_count = User.query.count()
    return render_template("leaderboard.html", logged_in=is_logged_in(), player_count=player_count)

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

@app.route("/logout", methods=['POST'])
def logout():
    response = jsonify({"message" : "Logout successful"})
    unset_jwt_cookies(response)
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
    
    return jsonify({"message": "Local tournament created! Waiting for players..."}), 403

def build_8_man(tourney_id, players):
    upper_slots = ['u-8-r1-m1', 'u-8-r1-m2', 'u-8-r1-m3', 'u-8-r1-m4', 'u-8-r2-m1', 'u-8-r2-m2', 'u-8-r3-m1', 'u-8-gf']
    lower_slots = ['l-8-r1-m1', 'l-8-r1-m2', 'l-8-r2-m1', 'l-8-r2-m2', 'l-8-r3-m1', 'l-8-r4-m1']

    for slot in upper_slots + lower_slots:
        db.session.add(Match(tournament_id=tourney_id, grid_class=slot))
    db.session.commit()

    r1_matches = Match.query.filter_by(tournament_id=tourney_id).filter(Match.grid_class.like('u-8-r1-m%')).order_by(Match.grid_class).all()
    seat_players(r1_matches, players)

def build_16_man(tourney_id, players):
    upper_slots = [
        'u-r1-m1', 'u-r1-m2', 'u-r1-m3', 'u-r1-m4', 'u-r1-m5', 'u-r1-m6', 'u-r1-m7', 'u-r1-m8',
        'u-r2-m1', 'u-r2-m2', 'u-r2-m3', 'u-r2-m4', 'u-r3-m1', 'u-r3-m2', 'u-r4-m1', 'u-gf'
    ]
    lower_slots = [
        'l-r1-m1', 'l-r1-m2', 'l-r1-m3', 'l-r1-m4', 'l-r2-m1', 'l-r2-m2', 'l-r2-m3', 'l-r2-m4',
        'l-r3-m1', 'l-r3-m2', 'l-r4-m1', 'l-r5-m1'
    ]
    for slot in upper_slots + lower_slots:
        db.session.add(Match(tournament_id=tourney_id, grid_class=slot))
    db.session.commit()

    r1_matches = Match.query.filter_by(tournament_id=tourney_id).filter(Match.grid_class.like('u-r1-m%')).order_by(Match.grid_class).all()
    seat_players(r1_matches, players)

def seat_players(r1_matches, players):
    player_index = 0
    for match in r1_matches:
        if player_index < len(players):
            match.player1_id = players[player_index].id
            player_index += 1
        if player_index < len(players):
            match.player2_id = players[player_index].id
            player_index += 1
    db.session.commit()

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
    tournament = Tournament.query.get(data.get("tournament_id"))

    players = tournament.pariticipants
    random.shuffle(players)
    num_players = len(players)

    if num_players <= 8:
        build_8_man(tournament.id, players)
    elif num_players <= 16:
        build_16_man(tournament.id, players)
    else:
        return jsonify({"error": "Max 16 players supported currently!"}), 400

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
    
    match.winner_id = winner_id
    loser_id = match.player2_id if winner_id == match.player1_id else match.player1_id

    routing = {
        # --- 8-MAN MAPPINGS ---
        'u-8-r1-m1': ('u-8-r2-m1', 'p1', 'l-8-r1-m1', 'p1'),
        'u-8-r1-m2': ('u-8-r2-m1', 'p2', 'l-8-r1-m1', 'p2'),
        'u-8-r1-m3': ('u-8-r2-m2', 'p1', 'l-8-r1-m2', 'p1'),
        'u-8-r1-m4': ('u-8-r2-m2', 'p2', 'l-8-r1-m2', 'p2'),
        'u-8-r2-m1': ('u-8-r3-m1', 'p1', 'l-8-r2-m1', 'p1'),
        'u-8-r2-m2': ('u-8-r3-m1', 'p2', 'l-8-r2-m2', 'p1'),
        'u-8-r3-m1': ('u-8-gf', 'p1', 'l-8-r4-m1', 'p2'),
        'l-8-r1-m1': ('l-8-r2-m1', 'p2', None, None),
        'l-8-r1-m2': ('l-8-r2-m2', 'p2', None, None),
        'l-8-r2-m1': ('l-8-r3-m1', 'p1', None, None),
        'l-8-r2-m2': ('l-8-r3-m1', 'p2', None, None),
        'l-8-r3-m1': ('l-8-r4-m1', 'p1', None, None),
        'l-8-r4-m1': ('u-8-gf', 'p2', None, None),

        # --- 16-MAN MAPPINGS ---
        'u-r1-m1': ('u-r2-m1', 'p1', 'l-r1-m1', 'p1'),
        'u-r1-m2': ('u-r2-m1', 'p2', 'l-r1-m1', 'p2'),
        'u-r1-m3': ('u-r2-m2', 'p1', 'l-r1-m2', 'p1'),
        'u-r1-m4': ('u-r2-m2', 'p2', 'l-r1-m2', 'p2'),
        'u-r1-m5': ('u-r2-m3', 'p1', 'l-r1-m3', 'p1'),
        'u-r1-m6': ('u-r2-m3', 'p2', 'l-r1-m3', 'p2'),
        'u-r1-m7': ('u-r2-m4', 'p1', 'l-r1-m4', 'p1'),
        'u-r1-m8': ('u-r2-m4', 'p2', 'l-r1-m4', 'p2'),
        'u-r2-m1': ('u-r3-m1', 'p1', 'l-r2-m1', 'p1'),
        'u-r2-m2': ('u-r3-m1', 'p2', 'l-r2-m2', 'p1'),
        'u-r2-m3': ('u-r3-m2', 'p1', 'l-r2-m3', 'p1'),
        'u-r2-m4': ('u-r3-m2', 'p2', 'l-r2-m4', 'p1'),
        'u-r3-m1': ('u-r4-m1', 'p1', 'l-r4-m1', 'p1'),
        'u-r3-m2': ('u-r4-m1', 'p2', 'l-r5-m1', 'p1'), 
        'u-r4-m1': ('u-gf', 'p1', 'l-r5-m1', 'p2'), 
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
        'l-r5-m1': ('u-gf', 'p2', None, None)
    }

    route = routing.get(match.grid_class)
    if route:
        w_class, w_slot, l_class, l_slot = route
        
        w_next = Match.query.filter_by(tournament_id=match.tournament_id, grid_class=w_class).first()
        if w_next:
            if w_slot == 'p1': w_next.player1_id = winner_id
            else: w_next.player2_id = winner_id

        if l_class:
            l_next = Match.query.filter_by(tournament_id=match.tournament_id, grid_class=l_class).first()
            if l_next:
                if l_slot == 'p1': l_next.player1_id = loser_id
                else: l_next.player2_id = loser_id

    db.session.commit()
    return jsonify({"message": "Bracket updated!"}), 200

@app.route("/api/leaderboard")
def leaderboard_api():
    game = request.args.get("game", "Overall")
    
    if game == "Street Fighter":
        users = User.query.order_by(User.sf6_wins.desc()).all()
    elif game == "Tekken":
        users = User.query.order_by(User.t8_wins.desc()).all()
    elif game == "Guilty Gear":
        users = User.query.order_by(User.gg_wins.desc()).all()
    else:  # Overall
        users = User.query.all()
        users.sort(key=lambda u: u.sf6_wins + u.t8_wins + u.gg_wins, reverse=True)

    result = []
    for user in users:
        total = user.sf6_wins + user.t8_wins + user.gg_wins
        if game == "Street Fighter":
            wins = user.sf6_wins
        elif game == "Tekken":
            wins = user.t8_wins
        elif game == "Guilty Gear":
            wins = user.gg_wins
        else:
            wins = total
        result.append({"name": user.username, "wins": wins, "game": game})

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug = True, port = 5000)