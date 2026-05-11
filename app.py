from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    hash = db.Column(db.String, nullable=False)

@app.route('/')
def index():
    return render_template("home.html")

bcrypt = Bcrypt(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)