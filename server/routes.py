from flask import Flask, request, jsonify, session as flask_session
from flask_session import Session
import os
import random
import string
import pickle
import numpy as np
import json
from api.gemini_client import GeminiProvider
from urllib.parse import quote_plus
from dotenv import load_dotenv, find_dotenv
from dateutil.parser import parse

# Import your model and recommendation modules as needed
from models.model import Model
# from models.recommendation import process_events_for_user
from server.utils import Utils

from sqlalchemy import create_engine, Column, String, Integer, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# --------------------------------
# Environment & SQLAlchemy Setup
# --------------------------------
load_dotenv(find_dotenv())
DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///example.db")
gemini_provider = GeminiProvider()
engine = create_engine(DATABASE_URI, echo=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

# --------------------------------
# SQLAlchemy ORM Models
# --------------------------------
class User(Base):
    __tablename__ = "user_info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # New field: storing password (consider hashing in production)
    birthyear = Column(Integer)
    gender = Column(String)
    country = Column(String)  # New field: country
    state = Column(String)    # New field: state
    city = Column(String)     # New field: city
    genre = Column(String)    # New field: genre preferences

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "birthyear": self.birthyear,
            "gender": self.gender,
            "country": self.country,
            "state": self.state,
            "city": self.city,
            "genre": self.genre
        }


class Event(Base):
    __tablename__ = "event_info"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    lat = Column(Float)
    lng = Column(Float)
    words = Column(Text)  # stored as a JSON string
    start = Column(Integer)  # event start timestamp

    def to_dict(self):
        data = {
            "event_id": self.event_id,
            "lat": self.lat,
            "lng": self.lng,
            "words": json.loads(self.words) if self.words else [],
            "start": self.start,
        }
        # Add a location field similar to the original code
        if self.lat is not None and self.lng is not None:
            data["location"] = [self.lat, self.lng]
        else:
            data["location"] = None
        return data

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String)  # username of the user
    event = Column(String)  # event_id
    response = Column(String)
    timestamp = Column(Integer)

    def to_dict(self):
        return {
            "user": self.user,
            "event": self.event,
            "response": self.response,
            "timestamp": self.timestamp
        }

class Friend(Base):
    __tablename__ = "friends"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, unique=True, index=True)
    friends = Column(Text)  # stored as a JSON string (list of friend usernames)

    def to_dict(self):
        return {
            "user": self.user,
            "friends": json.loads(self.friends) if self.friends else []
        }

# Create all tables if they don’t exist yet
Base.metadata.create_all(bind=engine)

# --------------------------------
# Load ML Model
# --------------------------------
MODEL_FILENAME = "rf_model_25.pkl"
if os.path.exists(MODEL_FILENAME):
    with open(MODEL_FILENAME, "rb") as f:
        ml_model = pickle.load(f)
    print(f"Loaded ml_model from {MODEL_FILENAME}")
else:
    ml_model = None
    print("Trained ml_model not found.")

# --------------------------------
# Helper: Load Full Data from SQL Database
# --------------------------------
def load_full_data_sql(db_session):
    # Users dictionary: key is username, value is its dictionary representation
    users = {u.username: u.to_dict() for u in db_session.query(User).all()}
    
    # Events dictionary: key is event_id
    events = {e.event_id: e.to_dict() for e in db_session.query(Event).all()}
    
    # Attendance dictionaries (by username and by event_id)
    att_by_username = {}
    att_by_event = {}
    for att in db_session.query(Attendance).all():
        uname = att.user
        eid = att.event
        att_by_username.setdefault(uname, []).append(att.to_dict())
        att_by_event.setdefault(eid, []).append(att.to_dict())
    
    # Friends dictionary: key is username, value is the list of friend usernames
    friends_dict = {}
    for fr in db_session.query(Friend).all():
        friends_dict[fr.user] = fr.to_dict().get("friends", [])
    
    return users, events, att_by_username, att_by_event, friends_dict

# --------------------------------
# Flask Application Setup with Flask-Session
# --------------------------------
app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"  # or another session type you prefer
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-key")
Session(app)

# --------------------------------
# Route: User Registration
# --------------------------------
@app.route('/register', methods=['POST'])
def register():
    required_fields = ["username", "password", "birthyear", "gender", "country", "state", "city", "genre"]
    data = {}
    for field in required_fields:
        value = request.form.get(field)
        if not value:
            return jsonify({"status": "fail", "message": f"Missing field: {field}"}), 400
        data[field] = value

    db = SessionLocal()
    try:
        if db.query(User).filter_by(username=data["username"]).first():
            return jsonify({"status": "fail", "message": "Username already exists"}), 400

        new_user = User(
            username=data["username"],
            password=data["password"],
            birthyear=int(data.get("birthyear")),
            gender=data.get("gender"),
            country=data.get("country"),
            state=data.get("state"),
            city=data.get("city"),
            genre=data.get("genre")
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        users, events, att_by_username, att_by_event, friends_dict = load_full_data_sql(db)
        flask_session["user_info"] = users
        flask_session["event_info"] = events
        flask_session["attendance_by_username"] = att_by_username
        flask_session["attendance_by_event"] = att_by_event
        flask_session["friends"] = friends_dict

        return jsonify({"status": "success", "user": new_user.to_dict()}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"status": "fail", "message": str(e)}), 500
    finally:
        db.close()

@app.route('/login', methods=['POST'])
def login():
    """
    Login a user by validating username and password.

    Expected form input:
    {
        "username": "john_doe",
        "password": "pass123"
    }
    """
    data = request.form  # If sent as form-data, use .form; if JSON, use .get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"status": "fail", "message": "Missing username or password"}), 400

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()
        if user is None:
            return jsonify({"status": "fail", "message": "User not found"}), 404

        if user.password != password:
            return jsonify({"status": "fail", "message": "Incorrect password"}), 401

        # Success! Populate session
        flask_session["user"] = user.to_dict()
        
        return jsonify({"status": "success", "message": "Logged in successfully", "user": user.to_dict()}), 200

    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 500
    finally:
        db.close()


# --------------------------------
# Route: Register Event
# --------------------------------
@app.route('/register_event', methods=['POST'])
def register_event():
    """
    Registers a new event.

    Expected JSON input:
    {
        "lat": 37.7749,
        "lng": -122.4194,
        "words": ["music", "festival", "live"],
        "start": 1370000000   // (Optional) timestamp for event start time
        // ... any additional event information
    }
    """
    data = request.get_json()
    db = SessionLocal()
    try:
        if "event_id" not in data or not data["event_id"]:
            data["event_id"] = Utils.generate_random_event_id(db, Event)  # Ensure Utils generates a unique event_id

        words_json = json.dumps(data.get("words", []))
        new_event = Event(
            event_id=data["event_id"],
            lat=data.get("lat"),
            lng=data.get("lng"),
            words=words_json,
            start=data.get("start")
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)

        # Update session data with the new event
        users, events, att_by_username, att_by_event, friends_dict = load_full_data_sql(db)
        flask_session["event_info"] = events

        return jsonify({"status": "success", "event": new_event.to_dict()}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"status": "fail", "message": str(e)}), 500
    finally:
        db.close()

# --------------------------------
# Route: Update Friends
# --------------------------------
@app.route('/update_friends', methods=['POST'])
def update_friends():
    """
    Updates a user's friend list.

    Expected JSON input:
    {
        "user": <username>,
        "friends": [username1, username2]
    }
    """
    data = request.get_json()
    if "user" not in data or "friends" not in data:
        return jsonify({"status": "fail", "message": "Missing user or friends field"}), 400

    db = SessionLocal()
    try:
        friend_obj = db.query(Friend).filter(Friend.user == data["user"]).first()
        friends_json = json.dumps(data["friends"])
        if friend_obj:
            friend_obj.friends = friends_json
        else:
            friend_obj = Friend(user=data["user"], friends=friends_json)
            db.add(friend_obj)
        db.commit()

        # Update friends info in the Flask session
        users, events, att_by_username, att_by_event, friends_dict = load_full_data_sql(db)
        flask_session["friends"] = friends_dict

        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"status": "fail", "message": str(e)}), 500
    finally:
        db.close()

# --------------------------------
# Route: Capture User Interaction
# --------------------------------
@app.route('/interaction', methods=['POST'])
def interaction():
    """
    Captures a user's interaction with an event.

    Expected JSON input:
    {
        "user": <username>,
        "event": <event_id>,
        "response": "yes",   // Options: "yes", "maybe", "no", "invited"
        "timestamp": 1370001234   // Unix timestamp of interaction
    }
    """
    data = request.get_json()
    required = ["user", "event", "response", "timestamp"]
    for field in required:
        if field not in data:
            return jsonify({"status": "fail", "message": f"Missing field: {field}"}), 400

    db = SessionLocal()
    try:
        new_attendance = Attendance(
            user=data["user"],
            event=data["event"],
            response=data["response"],
            timestamp=data["timestamp"]
        )
        db.add(new_attendance)
        db.commit()
        db.refresh(new_attendance)

        # Update attendance info in the Flask session
        users, events, att_by_username, att_by_event, friends_dict = load_full_data_sql(db)
        flask_session["attendance_by_username"] = att_by_username
        flask_session["attendance_by_event"] = att_by_event

        return jsonify({"status": "success", "interaction": new_attendance.to_dict()}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"status": "fail", "message": str(e)}), 500
    finally:
        db.close()

# --------------------------------
# Route: Recommendations
# --------------------------------
# @app.route('/recommendations', methods=['POST'])
# def recommendations():
#     data = request.get_json()
#     username = data.get("user_id")
#     if username is None:
#         return jsonify({"status": "fail", "message": "Missing user_id"}), 400

#     # Retrieve user_info and event_info from the session; reload if missing.
#     user_info = flask_session.get("user_info")
#     event_info = flask_session.get("event_info")
#     if not user_info or username not in user_info:
#         db = SessionLocal()
#         try:
#             user_info, event_info, att_by_username, att_by_event, friends_dict = load_full_data_sql(db)
#             flask_session["user_info"] = user_info
#             flask_session["event_info"] = event_info
#         finally:
#             db.close()

#     if username not in flask_session["user_info"]:
#         return jsonify({"status": "fail", "message": "User not found"}), 404

#     # Convert the username-based user_info to the expected numeric ID:
#     user_obj = flask_session["user_info"][username]
#     uid = user_obj["id"]

#     # Ensure each event has an "id" field; use event_id as its "id"
#     for eid, event in event_info.items():
#         if "id" not in event:
#             event["id"] = eid  # or event["event_id"] if they differ

#     # Build candidate event dictionary with default values
#     e_dict = {eid: (0, 0) for eid in event_info}

#     # Compute features for recommendation using the numeric uid
#     features_dict = process_events_for_user(uid, e_dict)
#     event_ids = list(features_dict.keys())
#     X = []
#     for eid in event_ids:
#         # Replace None values with 0 for every feature
#         features = [0 if f is None else f for f in features_dict[eid]]
#         X.append(features)
#     X = np.array(X)
#     X = np.atleast_2d(X)  # Ensure X is 2D

#     if ml_model is None:
#         return jsonify({"status": "fail", "message": "Model not loaded"}), 500

#     predictions = ml_model.test(X)
#     event_scores = list(zip(event_ids, predictions))
#     event_scores.sort(key=lambda x: -x[1])
#     recommended_events = [eid for eid, score in event_scores]

#     return jsonify({
#         "status": "success",
#         "user_id": username,
#         "recommendations": recommended_events
#     }), 200

@app.route('/recommendations-new', methods=['POST'])
def recommendations_new():
    data = request.get_json()
    username = data.get("user_id")
    if username is None:
        return jsonify({"status": "fail", "message": "Missing user_id"}), 400

    # Retrieve user_info and event_info from the session; reload if missing.
    user_info = flask_session.get("user_info")
    event_info = flask_session.get("event_info")
    if not user_info or username not in user_info:
        db = SessionLocal()
        try:
            user_info, event_info, att_by_username, att_by_event, friends_dict = load_full_data_sql(db)
            flask_session["user_info"] = user_info
            flask_session["event_info"] = event_info
        finally:
            db.close()

    if username not in flask_session["user_info"]:
        return jsonify({"status": "fail", "message": "User not found"}), 404

    # Convert the username-based user_info to the expected numeric ID:
    user_obj = flask_session["user_info"][username]
    uid = user_obj["id"]

    # Ensure each event has an "id" field; use event_id as its "id"
    for eid, event in event_info.items():
        if "id" not in event:
            event["id"] = eid  # or event["event_id"] if they differ

    # Build candidate event dictionary with default values
    e_dict = {eid: (0, 0) for eid in event_info}

    
    prompt = """"""
    recommended_events = gemini_provider.generate_json_response(prompt)

    return jsonify({
        "status": "success",
        "user_id": username,
        "recommendations": recommended_events
    }), 200

# --------------------------------
# Main: Run the Flask Application
# --------------------------------
if __name__ == '__main__':
    app.run(debug=True)
