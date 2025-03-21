from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import pickle
import os
import time

# Import functions from your recommendation pipeline.
from recommendation import process_events_for_user, get_full_data
from model import Model

app = Flask(__name__)
# Configure SQLAlchemy with a database URI. Here, we use SQLite for simplicity.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recommendation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

######################################
# SQLAlchemy ORM Models
######################################

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    birth = db.Column(db.String(10))
    gender = db.Column(db.String(10))
    location = db.Column(db.String(100), nullable=True)  # store as stringified JSON or comma-separated lat,lng
    age = db.Column(db.Integer, nullable=True)
    # You can add more fields as needed.

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.String(50), primary_key=True)
    location = db.Column(db.String(100), nullable=True)  # store as stringified list: "lat,lng"
    words = db.Column(db.Text, nullable=True)  # store as JSON or comma separated string
    # You can add additional event details as needed.

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.String(50), db.ForeignKey('events.id'))
    yes = db.Column(db.Boolean, default=False)
    maybe = db.Column(db.Boolean, default=False)
    invited = db.Column(db.Boolean, default=False)
    no = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.Float, nullable=True)

class Friend(db.Model):
    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    friend_id = db.Column(db.Integer, nullable=False)

######################################
# Database Initialization Utility
######################################
@app.before_first_request
def create_tables():
    db.create_all()
    # Optionally, you could load initial data from CSVs into the database here.
    # For instance, using get_full_data() from your pipeline, then iterating over the dictionaries.
    # For brevity, we assume the database is already populated.

######################################
# Global Variables for Cache and Model
######################################
DATA_CACHE = {}
MODEL = None

def load_data_from_db():
    """
    Loads all required data from the database and stores it in a global cache.
    This data includes users, events, attendance, and friends.
    """
    global DATA_CACHE
    # Load users into a dictionary.
    users = {user.id: {
                "id": user.id,
                "birth": user.birth,
                "gender": user.gender,
                "location": None if user.location is None else [float(x) for x in user.location.split(',')],
                "age": user.age
             } for user in User.query.all()}

    # Load events into a dictionary.
    events = {}
    for event in Event.query.all():
        loc = None
        if event.location:
            try:
                loc = [float(x) for x in event.location.split(',')]
            except Exception:
                loc = None
        # Here we assume event.words is stored as a comma-separated string.
        words = event.words.split(',') if event.words else []
        events[event.id] = {
            "id": event.id,
            "location": loc,
            "words": words
        }
    
    # Load attendance and create indices.
    attendance_by_uid = {}
    attendance_by_eid = {}
    for rec in Attendance.query.all():
        record = {
            "uid": rec.user_id,
            "eid": rec.event_id,
            "yes": rec.yes,
            "maybe": rec.maybe,
            "invited": rec.invited,
            "no": rec.no,
            "timestamp": rec.timestamp
        }
        attendance_by_uid.setdefault(rec.user_id, []).append(record)
        attendance_by_eid.setdefault(rec.event_id, []).append(record)
    
    # Load friends.
    friends = {}
    for rec in Friend.query.all():
        friends.setdefault(rec.user_id, []).append(rec.friend_id)
    
    # Cache the data.
    DATA_CACHE = {
        "user_info": users,
        "event_info": events,
        "attendance_by_uid": attendance_by_uid,
        "attendance_by_eid": attendance_by_eid,
        "friends": friends
    }
    print("Data loaded from database and cached.")

def load_model():
    """
    Loads a pre-trained model from a pickle file.
    """
    global MODEL
    model_filename = "model.pkl"
    if os.path.exists(model_filename):
        with open(model_filename, "rb") as f:
            MODEL = pickle.load(f)
        print("Pre-trained model loaded.")
    else:
        MODEL = Model()
        print("No pre-trained model found; new model instance created.")

# Initialize data and model at startup.
with app.app_context():
    load_data_from_db()
load_model()

######################################
# API Endpoints
######################################

@app.route("/")
def index():
    return "<h1>Live Recommendation API with SQLAlchemy is running!</h1>"

@app.route("/register", methods=["POST"])
def register():
    """
    Registers a new user. Expected JSON payload:
      {
        "birth": "1985",
        "gender": "male",
        "location": "lat,lng"   # optional string, e.g., "40.7128,-74.0060"
      }
    Returns the new user_id.
    """
    data = request.get_json()
    required_fields = ["birth", "gender"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    new_user = User(
        birth=data["birth"],
        gender=data["gender"],
        location=data.get("location"),  # should be a string "lat,lng"
        age=None  # You could compute this if needed (e.g., 2013 - birthyear)
    )
    db.session.add(new_user)
    db.session.commit()

    # Update in-memory cache.
    DATA_CACHE["user_info"][new_user.id] = {
        "id": new_user.id,
        "birth": new_user.birth,
        "gender": new_user.gender,
        "location": None if new_user.location is None else [float(x) for x in new_user.location.split(',')],
        "age": new_user.age
    }
    DATA_CACHE["attendance_by_uid"][new_user.id] = []

    return jsonify({"message": "User registered successfully.", "user_id": new_user.id})

@app.route("/update_interaction", methods=["POST"])
def update_interaction():
    """
    Records a user's interaction with an event.
    Expected JSON payload:
      {
        "user_id": 123,
        "event_id": "e456",
        "interaction": "interested"    // could be "interested" or "not_interested"
      }
    """
    data = request.get_json()
    for field in ["user_id", "event_id", "interaction"]:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        user_id = int(data["user_id"])
    except ValueError:
        return jsonify({"error": "Invalid user_id; must be integer."}), 400

    event_id = data["event_id"]
    interaction = data["interaction"]

    # Validate existence.
    if user_id not in DATA_CACHE["user_info"]:
        return jsonify({"error": f"User {user_id} not found."}), 404
    if event_id not in DATA_CACHE["event_info"]:
        return jsonify({"error": f"Event {event_id} not found."}), 404

    # Create a new attendance record.
    record = Attendance(
        user_id=user_id,
        event_id=event_id,
        yes=True if interaction == "interested" else False,
        maybe=False,
        invited=False,
        no=True if interaction == "not_interested" else False,
        timestamp=time.time()
    )
    db.session.add(record)
    db.session.commit()

    # Update in-memory cache.
    rec = {
        "uid": user_id,
        "eid": event_id,
        "yes": record.yes,
        "maybe": record.maybe,
        "invited": record.invited,
        "no": record.no,
        "timestamp": record.timestamp
    }
    DATA_CACHE["attendance_by_uid"].setdefault(user_id, []).append(rec)
    DATA_CACHE["attendance_by_eid"].setdefault(event_id, []).append(rec)

    return jsonify({"message": "Interaction recorded."})

@app.route("/recommend", methods=["GET"])
def recommend():
    """
    Returns a list of recommended event IDs for a given user.
    Expects a query parameter 'user_id'.
    The recommendations are generated by recomputing event features for the user.
    """
    user_id_param = request.args.get("user_id")
    if not user_id_param:
        return jsonify({"error": "Missing user_id parameter."}), 400

    try:
        user_id = int(user_id_param)
    except ValueError:
        return jsonify({"error": "user_id must be an integer."}), 400

    if user_id not in DATA_CACHE["user_info"]:
        return jsonify({"error": f"User {user_id} not found."}), 404

    # Build a dummy event dictionary.
    # In a production system, you might filter events by location, date, etc.
    e_dict = {}
    for eid, event in DATA_CACHE["event_info"].items():
        e_dict[eid] = (0, 0)  # Dummy invited flag and timestamp.

    # Compute features for each event for the given user.
    try:
        features_dict = process_events_for_user(user_id, e_dict)
    except Exception as e:
        return jsonify({"error": f"Error processing events: {str(e)}"}), 500

    X = []
    event_ids = []
    for eid, features in features_dict.items():
        if features is None or not any(f is not None for f in features):
            continue
        event_ids.append(eid)
        X.append(features)

    if not X:
        return jsonify({"error": "No valid event features found for this user."}), 404

    X = np.array(X)
    predictions = MODEL.test(X)
    # Pair each event ID with its prediction score.
    recommended = sorted(list(zip(event_ids, predictions)), key=lambda x: -x[1])
    recommended_ids = [eid for eid, score in recommended]

    return jsonify({
        "user_id": user_id,
        "recommended_events": recommended_ids
    })

if __name__ == "__main__":
    app.run(debug=True)
