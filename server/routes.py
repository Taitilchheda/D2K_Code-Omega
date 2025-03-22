from flask import Flask, request, jsonify, g
import pickle
import os
import random
import string
import numpy as np
import json
from urllib.parse import quote_plus
from dotenv import load_dotenv, find_dotenv
from dateutil.parser import parse
from models.model import Model
from models.recommendation import process_events_for_user
from server.utils import Utils

from sqlalchemy import create_engine, Column, String, Integer, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# --------------------------------
# Environment & SQLAlchemy Setup
# --------------------------------
load_dotenv(find_dotenv())
# Use your SQLAlchemy database URI here (for example, a PostgreSQL URI or SQLite)
DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///example.db")
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
    birthyear = Column(Integer)
    gender = Column(String)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "birthyear": self.birthyear,
            "gender": self.gender
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
    user = Column(String)  # user_id
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
    friends = Column(Text)  # stored as a JSON string (list of friend user_ids)

    def to_dict(self):
        return {
            "user": self.user,
            "friends": json.loads(self.friends) if self.friends else []
        }

# Create all tables (if they don’t exist yet)
Base.metadata.create_all(bind=engine)

# --------------------------------
# Load ML Model
# --------------------------------
MODEL_FILENAME = "rf_model.pkl"
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
def load_full_data_sql():
    session = g.db_session
    # Users dictionary: key is user_id, value is a dict representation
    users = {u.user_id: u.to_dict() for u in session.query(User).all()}
    
    # Events dictionary
    events = {e.event_id: e.to_dict() for e in session.query(Event).all()}
    
    # Attendance dictionaries (by user and by event)
    att_by_uid = {}
    att_by_eid = {}
    for att in session.query(Attendance).all():
        uid = att.user
        eid = att.event
        att_by_uid.setdefault(uid, []).append(att.to_dict())
        att_by_eid.setdefault(eid, []).append(att.to_dict())
    
    # Friends dictionary: key is user and value is the list of friend user_ids
    friends_dict = {}
    for fr in session.query(Friend).all():
        friends_dict[fr.user] = fr.to_dict().get("friends", [])
    
    return users, events, att_by_uid, att_by_eid, friends_dict

# --------------------------------
# Flask Application Setup
# --------------------------------
app = Flask(__name__)

@app.before_request
def before_request():
    g.db_session = SessionLocal()
    g.user_info, g.event_info, g.attendance_by_uid, g.attendance_by_eid, g.friends = load_full_data_sql()

@app.teardown_request
def teardown_request(exception):
    db_session = g.get("db_session")
    if db_session:
        db_session.close()

# --------------------------------
# Route: User Registration
# --------------------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ["username", "birthyear", "gender"]
    for field in required_fields:
        if field not in data:
            return jsonify({"status": "fail", "message": f"Missing field: {field}"}), 400

    session = g.db_session
    # Check if the username already exists
    existing_user = session.query(User).filter_by(username=data["username"]).first()
    if existing_user:
        return jsonify({"status": "fail", "message": "Username already exists"}), 400

    try:
        new_user = User(
            username=data["username"],
            birthyear=data.get("birthyear"),
            gender=data.get("gender")
        )
        session.add(new_user)
        session.commit()
        # Refresh the session object to load the auto-generated id
        session.refresh(new_user)
        g.user_info[new_user.username] = new_user.to_dict()
        return jsonify({"status": "success", "user": new_user.to_dict()}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"status": "fail", "message": str(e)}), 500

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
        "start": 1370000000     // (Optional) timestamp for event start time
        // ... any additional event information
    }
    """
    data = request.get_json()
    session = g.db_session
    if "event_id" not in data or not data["event_id"]:
        data["event_id"] = Utils.generate_random_event_id(session, Event)  # Adjust Utils accordingly

    try:
        # Convert words list to JSON string if present
        words_json = json.dumps(data.get("words", []))
        new_event = Event(
            event_id=data["event_id"],
            lat=data.get("lat"),
            lng=data.get("lng"),
            words=words_json,
            start=data.get("start")
        )
        session.add(new_event)
        session.commit()
        event_dict = new_event.to_dict()
        g.event_info[data["event_id"]] = event_dict
        return jsonify({"status": "success", "event": event_dict}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"status": "fail", "message": str(e)}), 500

# --------------------------------
# Route: Update Friends
# --------------------------------
@app.route('/update_friends', methods=['POST'])
def update_friends():
    """
    Updates a user's friend list.
    
    Expected JSON input:
    {
        "user": <user_id>,
        "friends": [user_id1, user_id2]
    }
    """
    data = request.get_json()
    if "user" not in data or "friends" not in data:
        return jsonify({"status": "fail", "message": "Missing user or friends field"}), 400

    session = g.db_session
    try:
        friend_obj = session.query(Friend).filter(Friend.user == data["user"]).first()
        friends_json = json.dumps(data["friends"])
        if friend_obj:
            friend_obj.friends = friends_json
        else:
            friend_obj = Friend(user=data["user"], friends=friends_json)
            session.add(friend_obj)
        session.commit()
        g.friends[data["user"]] = json.loads(friends_json)
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"status": "fail", "message": str(e)}), 500

# --------------------------------
# Route: Capture User Interaction
# --------------------------------
@app.route('/interaction', methods=['POST'])
def interaction():
    """
    Captures a user's interaction with an event.
    
    Expected JSON input:
    {
        "user": <user_id>,
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

    session = g.db_session
    try:
        new_attendance = Attendance(
            user=data["user"],
            event=data["event"],
            response=data["response"],
            timestamp=data["timestamp"]
        )
        session.add(new_attendance)
        session.commit()
        uid = data["user"]
        eid = data["event"]
        g.attendance_by_uid.setdefault(uid, []).append(new_attendance.to_dict())
        g.attendance_by_eid.setdefault(eid, []).append(new_attendance.to_dict())
        return jsonify({"status": "success", "interaction": new_attendance.to_dict()}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"status": "fail", "message": str(e)}), 500

# --------------------------------
# Route: Recommendations
# --------------------------------
@app.route('/recommendations', methods=['POST'])
def recommendations():
    """
    Returns event recommendations for a given user using the pre-trained ml_model.
    
    Expected JSON input:
    {
        "user_id": <user_id>
    }
    """
    data = request.get_json()
    user_id = data.get("user_id")
    if user_id is None:
        return jsonify({"status": "fail", "message": "Missing user_id"}), 400

    if user_id not in g.user_info:
        return jsonify({"status": "fail", "message": "User not found"}), 404

    # Build candidate event dictionary with default (invited_flag, timestamp) = (0, 0)
    e_dict = {eid: (0, 0) for eid in g.event_info}

    features_dict = process_events_for_user(user_id, e_dict)

    event_ids = list(features_dict.keys())
    X = []
    for eid in event_ids:
        features = [0 if f is None else f for f in features_dict[eid]]
        X.append(features)
    X = np.array(X)

    if ml_model is None:
        return jsonify({"status": "fail", "message": "Model not loaded"}), 500

    predictions = ml_model.test(X)
    event_scores = list(zip(event_ids, predictions))
    event_scores.sort(key=lambda x: -x[1])
    recommended_events = [eid for eid, score in event_scores]

    return jsonify({
        "status": "success",
        "user_id": user_id,
        "recommendations": recommended_events
    }), 200

# --------------------------------
# Main: Run the Flask Application
# --------------------------------
if __name__ == '__main__':
    app.run(debug=True)
