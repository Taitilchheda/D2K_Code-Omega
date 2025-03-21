
from flask import Flask, request, jsonify, g
import pickle
import os

MODEL_FILENAME = "trained_model.pkl"
if os.path.exists(MODEL_FILENAME):
    with open(MODEL_FILENAME, "rb") as f:
        ml_model = pickle.load(f)
    print(f"Loaded ml_model from {MODEL_FILENAME}")
else:
    ml_model = None
    print("Trained ml_model not found.")
    
import random
import string
import numpy as np
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv, find_dotenv
from dateutil.parser import parse
from utils import Utils 

# -------------------------------
# MongoDB Connection Setup
# -------------------------------
load_dotenv(find_dotenv())
password = quote_plus(os.getenv("MONGO_PASS"))
uri = f"mongodb+srv://kakashiforwork:{password}@cluster0.emman.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client["D2K"]

# Collections
user_info_db = db.user_info
event_info_db = db.event_info
attendance_db = db.attendance
friends_db = db.friends

# -------------------------------
# Import Recommendation Logic
# -------------------------------
from models.recommendation import process_events_for_user



# -------------------------------
# Helper: Load full data from MongoDB
# -------------------------------
def load_full_data_mongo():
    users = {}
    for doc in user_info_db.find():
        uid = doc.get("user_id")
        if uid is not None:
            users[uid] = doc

    events = {}
    for doc in event_info_db.find():
        eid = doc.get("event_id")
        if eid is not None:
            if doc.get("lat") is not None and doc.get("lng") is not None:
                doc["location"] = [doc["lat"], doc["lng"]]
            else:
                doc["location"] = None
            if "words" not in doc:
                doc["words"] = []
            events[eid] = doc

    att_by_uid = {}
    att_by_eid = {}
    for doc in attendance_db.find():
        uid = doc.get("user")
        eid = doc.get("event")
        if uid is None or eid is None:
            continue
        att_by_uid.setdefault(uid, []).append(doc)
        att_by_eid.setdefault(eid, []).append(doc)

    friends_dict = {}
    for doc in friends_db.find():
        uid = doc.get("user")
        if uid is not None:
            friends_dict[uid] = doc.get("friends", [])

    return users, events, att_by_uid, att_by_eid, friends_dict

# -------------------------------
# Flask Application Setup
# -------------------------------
app = Flask(__name__)

@app.before_request
def before_request():
    g.user_info, g.event_info, g.attendance_by_uid, g.attendance_by_eid, g.friends = load_full_data_mongo()

# -------------------------------
# Route: User Registration
# -------------------------------
@app.route('/register', methods=['POST'])
def register():
    """
    Registers a new user.
    
    Expected JSON input:
    {
        "username": "user1",         // Optional, for login purposes
        "password": "pass1",         // In production, ensure secure storage (hashing)
        "birthyear": 1985,
        "gender": "male",
        "location": {                // Optional
            "country": "USA",
            "state": "CA",
            "city": "San Francisco"
        }
    }
    
    If 'user_id' is not provided, a random unique user_id will be generated.
    
    Response:
    - On success: { "status": "success", "user": <user document> }
    - On failure: { "status": "fail", "message": "Error message" }
    """
    data = request.get_json()

    # Ensure required fields are provided
    required_fields = ["birthyear", "gender"]
    for field in required_fields:
        if field not in data:
            return jsonify({"status": "fail", "message": f"Missing field: {field}"}), 400

    # Check if username already exists
    if "username" in data:
        existing_user = user_info_db.find_one({"username": data["username"]})
        if existing_user:
            return jsonify({"status": "fail", "message": "Username already exists"}), 400

    if "user_id" not in data or not data["user_id"]:
        data["user_id"] = Utils.generate_random_user_id(user_info_db)

    try:
        user_info_db.insert_one(data)
        g.user_info[data["user_id"]] = data
        return jsonify({"status": "success", "user": data}), 201
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 500

# -------------------------------
# Route: Register Event
# -------------------------------
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
    
    If 'event_id' is not provided, a random unique event_id will be generated.
    
    Response:
    - On success: { "status": "success", "event": <event document> }
    - On failure: { "status": "fail", "message": "Error message" }
    """
    data = request.get_json()

    # Generate a random event_id if not provided
    if "event_id" not in data or not data["event_id"]:
        data["event_id"] = Utils.generate_random_event_id(event_info_db)

    try:
        event_info_db.insert_one(data)
        if data.get("lat") is not None and data.get("lng") is not None:
            data["location"] = [data["lat"], data["lng"]]
        else:
            data["location"] = None
        if "words" not in data:
            data["words"] = []
        g.event_info[data["event_id"]] = data
        return jsonify({"status": "success", "event": data}), 201
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 500

# -------------------------------
# Route: Update Friends
# -------------------------------
@app.route('/update_friends', methods=['POST'])
def update_friends():
    """
    Updates a user's friend list.
    
    Expected JSON input:
    {
        "user": <user_id>,              // user_id
        "friends": [user_id1, user_id2]   // list of friend user_ids
    }
    
    Response:
    - On success: { "status": "success", "data": <updated document> }
    - On failure: { "status": "fail", "message": "Error message" }
    """
    data = request.get_json()
    if "user" not in data or "friends" not in data:
        return jsonify({"status": "fail", "message": "Missing user or friends field"}), 400

    try:
        friends_db.update_one({"user": data["user"]},
                              {"$set": {"friends": data["friends"]}},
                              upsert=True)
        g.friends[data["user"]] = data["friends"]
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 500

# -------------------------------
# Route: Capture User Interaction
# -------------------------------
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
    
    The interaction is inserted into the attendance collection.
    
    Response:
    - On success: { "status": "success", "interaction": <document> }
    - On failure: { "status": "fail", "message": "Error message" }
    """
    data = request.get_json()
    required = ["user", "event", "response", "timestamp"]
    for field in required:
        if field not in data:
            return jsonify({"status": "fail", "message": f"Missing field: {field}"}), 400

    try:
        attendance_db.insert_one(data)
        uid = data["user"]
        eid = data["event"]
        g.attendance_by_uid.setdefault(uid, []).append(data)
        g.attendance_by_eid.setdefault(eid, []).append(data)
        return jsonify({"status": "success", "interaction": data}), 201
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 500

# -------------------------------
# Route: Recommendations
# -------------------------------
@app.route('/recommendations', methods=['POST'])
def recommendations():
    """
    Returns event recommendations for a given user using the pre-trained ml_model.
    
    Expected JSON input:
    {
        "user_id": <user_id>
    }
    
    Process:
    - Uses data loaded into g (user_info, event_info, attendance, friends) to build a candidate event dictionary.
    - Calls the recommendation logic (process_events_for_user) to compute feature vectors.
    - Replaces None values in feature vectors with 0.
    - Uses the pre-trained ml_model to predict scores for each event and sorts them in descending order.
    
    Response:
    {
        "status": "success",
        "user_id": <user_id>,
        "recommendations": [list of event IDs sorted by predicted score]
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

# -------------------------------
# Main: Run the Flask Application
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
