#User Authentication
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import secrets
from datetime import datetime, timedelta, timezone 


app = Flask(__name__)
CORS(app) 

#Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

#User Defining
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    token = db.Column(db.String(200), unique=True, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)

#User Register (using JSON)
@app.route("/app/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
       return jsonify({"error": "Data not received"}), 400

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if User.query.filter_by(username=username).first():
       return jsonify({"error": "Username already exists"}), 409

    hashed_pw = generate_password_hash(password, method ='pbkdf2:sha256')
    new_user = User(username=username, password_hash=hashed_pw, email=email)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"Status": "Success", "message": "User registered successfully!"}), 201

#User Login (using JSON) with Token Generation
@app.route("/app/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        new_token = secrets.token_hex(16)
        user.token = new_token
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        return jsonify({"Status": "Success",
                        "token": new_token,
                        "username": user.username}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

#Session timeout and Logout
@app.route("/app/motor/control", methods=["POST"])
def motor_control():
    data = request.get_json()
    token = data.get("token")

    user = User.query.filter_by(token=token).first()

    if not user:
        return jsonify({"error": "Invalid token"}), 401
    
    if datetime.now(timezone.utc) - user.last_login >  timedelta(minutes=30):
        user.token = None
        db.session.commit()
        return jsonify({"error": "Session expired. Please login again"}), 401
    
    else:
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"Status": "Success", "message": "Motor controlled"}), 200
    
@app.route("/app/logout", methods=["POST"])
def logout():
    data = request.get_json()
    token = data.get("token")

    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({"error": "Invalid token"}), 401

    user.token = None
    db.session.commit()
    return jsonify({"Status": "Success", "message": "Logged out"}), 200

#Emergency Stop
@app.route("/app/emergency/stop", methods=["POST"])
def emergency_stop():
    print("Emergency Stop Activated!")

    

    return jsonify({"Status": "Success", "message": "Emergency stop activated"}), 200

#Motor Control
@app.route("/app/motor/set_rpm", methods=["POST"])
def set_rpm():


 if __name__ == "__main__":
     with app.app_context():
        db.create_all()
app.run(host="0.0.0.0", port=5000, debug=True)