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
    
    # New fields:
    event_name = Column(String)       # e.g., "Music Festival 2025"
    description = Column(Text)        # Detailed description of the event
    location = Column(String)         # Location as a string, e.g. "San Francisco"
    start_date = Column(String)       # Start date (could use Date type if desired)
    start_time = Column(String)       # Start time (could use Time type if desired)

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "description": self.description,
            "location": self.location,
            "start_date": self.start_date,
            "start_time": self.start_time
        }
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
    # Get data from request
    if request.is_json:
        json_data = request.get_json()
        
        # Extract nested location data
        if 'location' in json_data:
            location = json_data.pop('location', {})
            json_data['country'] = location.get('country')
            json_data['state'] = location.get('state')
            json_data['city'] = location.get('city')
            
        data = json_data
    else:
        data = request.form.to_dict()

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

        return jsonify({"status": "success", "user": new_user.to_dict()}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"status": "fail", "message": str(e)}), 500
    finally:
        db.close()
        
@app.route('/login', methods=['POST'])
def login():
    """
    Login a user by validating username and password.
    
    Expected JSON input:
    {
        "username": "john_doe",
        "password": "pass123"
    }
    """
    # Check if the request contains JSON data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form  # Fallback to form data if not JSON
    
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
    Registers a new event using new fields.

    Expected form-data or JSON input:
    {
        "eventName": "Concert in the Park",
        "description": "An open-air concert featuring local bands.",
        "location": "San Francisco",
        "startDate": "2025-06-15",      // Expected date format (e.g., YYYY-MM-DD)
        "startTime": "18:00"            // Expected time format (e.g., HH:MM)
        // Optionally, an event_id can be provided. Otherwise, one will be generated.
    }
    """
    # Support both JSON and form-data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    required_fields = ["eventName", "description", "location", "startDate", "startTime"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"status": "fail", "message": f"Missing field: {field}"}), 400

    db = SessionLocal()
    try:
        # Generate a unique event_id if not provided
        if "event_id" not in data or not data["event_id"]:
            data["event_id"] = Utils.generate_random_event_id(db, Event)
        
        new_event = Event(
            event_id=data["event_id"],
            event_name=data["eventName"],
            description=data["description"],
            location=data["location"],
            start_date=data["startDate"],
            start_time=data["startTime"]
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



@app.route('/recommendations-new', methods=['POST'])
def recommendations_new():
    """
    Generates event recommendations for a user by gathering the following information:
    
    - User Demographics: (birthyear, gender, location from city/state/country, preferred genre)
    - User Past Interactions: events the user responded to (yes, no, interested, etc.)
    - Event Information: event id, event name, description, location, start date, and start time
    - Friends Attending: for each event, which of the user's friends are attending
    - Recommendation Criteria:
        1. Location Proximity
        2. Preference Matching
        3. Past Interactions
        4. Social Influence (Friends Attending)
        
    The LLM is expected to return a JSON response with a list of recommended event IDs.
    
    Expected JSON input:
    {
      "user_id": "<username>"
    }
    """
    # Get user_id from JSON payload
    data = request.get_json()
    username = data.get("user_id")
    if not username:
        return jsonify({"status": "fail", "message": "Missing user_id"}), 400

    # Retrieve session data; reload from the database if missing.
    user_info = flask_session.get("user_info")
    event_info = flask_session.get("event_info")
    attendance_by_username = flask_session.get("attendance_by_username")
    attendance_by_event = flask_session.get("attendance_by_event")
    friends = flask_session.get("friends")

    if not user_info or username not in user_info:
        db = SessionLocal()
        try:
            user_info, event_info, attendance_by_username, attendance_by_event, friends = load_full_data_sql(db)
            flask_session["user_info"] = user_info
            flask_session["event_info"] = event_info
            flask_session["attendance_by_username"] = attendance_by_username
            flask_session["attendance_by_event"] = attendance_by_event
            flask_session["friends"] = friends
        finally:
            db.close()

    if username not in user_info:
        return jsonify({"status": "fail", "message": "User not found"}), 404

    # Extract user demographics from user_info.
    user_demographics = user_info[username]  # Contains birthyear, gender, country, state, city, genre

    # Get user's past event interactions.
    user_interactions = attendance_by_username.get(username, [])

    # Get user's friend list.
    user_friends = friends.get(username, [])

    # For each event, check which of the user's friends are attending.
    friend_attendance = {}
    for event_id, attend_list in attendance_by_event.items():
        friend_users = [record["user"] for record in attend_list if record["user"] in user_friends]
        if friend_users:
            friend_attendance[event_id] = friend_users

    # Compose the prompt for the LLM.
    prompt = f"""
You are an expert event recommendation agent for an events discovery platform. Your goal is to recommend the most relevant events to a user given the following information.

User Demographics:
  - Username: {username}
  - Birthyear: {user_demographics.get('birthyear')}
  - Gender: {user_demographics.get('gender')}
  - Location: {user_demographics.get('city')}, {user_demographics.get('state')}, {user_demographics.get('country')}
  - Preferred Genre: {user_demographics.get('genre')}

User Past Interactions (Event responses):
{json.dumps(user_interactions, indent=2)}

Event Information:
"""
    # Append details for each event.
    for event_id, event in event_info.items():
        prompt += f"""
Event ID: {event_id}
  - Name: {event.get('event_name')}
  - Description: {event.get('description')}
  - Location: {event.get('location')}
  - Start Date: {event.get('start_date')}
  - Start Time: {event.get('start_time')}
"""
        if event_id in friend_attendance:
            prompt += f"  - Friends Attending: {', '.join(friend_attendance[event_id])}\n"
        else:
            prompt += "  - Friends Attending: None\n"

    prompt += """
Recommendation Criteria (Prioritize in this order):
1. Location Proximity: Prioritize events that are geographically closer to the user.
2. Preference Matching: Strongly consider the user's preferences (categories, keywords, etc.) and recommend events that align with them.
3. Past Interactions: Learn from the user's past interactions. Recommend events similar to those they liked, saved, or attended. Avoid recommending events similar to those they ignored.
4. Social Influence (Friends Attending): Give a boost to events that friends are attending.

Please provide a JSON response with a list of recommended event IDs in the following format:
{
  "events": ["recommended_event_id1", "recommended_event_id2", "recommended_event_id3"]
}
"""

    # Call the Gemini provider with the composed prompt.
    print("PROMPT", prompt)
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
