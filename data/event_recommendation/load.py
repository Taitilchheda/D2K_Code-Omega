from flask import Flask, request, jsonify
import pickle
import os
import numpy as np
from pymongo import MongoClient, ASCENDING
from urllib.parse import quote_plus
from dotenv import load_dotenv, find_dotenv
from dateutil.parser import parse
import time

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
from recommendation import process_events_for_user

MODEL_FILENAME = "trained_model.pkl"
if os.path.exists(MODEL_FILENAME):
    with open(MODEL_FILENAME, "rb") as f:
        model = pickle.load(f)
    print(f"Loaded model from {MODEL_FILENAME}")
else:
    model = None
    print("Trained model not found.")

# -------------------------------
# Helper: Load full data from MongoDB
# -------------------------------
def load_full_data_mongo():
    users = {}
    for doc in user_info_db.find():
        uid = doc.get("user_id")
        if uid is not None:
            users[uid] = doc

    # Load event_info from MongoDB into a dictionary keyed by event_id.
    events = {}
    for doc in event_info_db.find():
        eid = doc.get("event_id")
        if eid is not None:
            # Infer location from lat and lng fields if available
            if doc.get("lat") is not None and doc.get("lng") is not None:
                doc["location"] = [doc["lat"], doc["lng"]]
            else:
                doc["location"] = None
            # Ensure words field exists (should be a list)
            if "words" not in doc:
                doc["words"] = []
            events[eid] = doc

    # Build attendance indices
    att_by_uid = {}
    att_by_eid = {}
    for doc in attendance_db.find():
        uid = doc.get("user")
        eid = doc.get("event")
        if uid is None or eid is None:
            continue
        att_by_uid.setdefault(uid, []).append(doc)
        att_by_eid.setdefault(eid, []).append(doc)

    # Build friends dictionary: each document should have a "user" field and a "friends" list.
    friends_dict = {}
    for doc in friends_db.find():
        uid = doc.get("user")
        if uid is not None:
            friends_dict[uid] = doc.get("friends", [])
    
    return users, events, att_by_uid, att_by_eid, friends_dict

user_info, event_info, attendance_by_uid, attendance_by_eid, friends = load_full_data_mongo()
app = Flask(__name__)

# -------------------------------
# Route: User Registration
# -------------------------------
@app.route('/register', methods=['POST'])
def register():
    """
    Expected JSON input:
    {
        "user_id": 1,                // Unique identifier for the user
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
    
    Response:
    - On success: { "status": "success", "user": <user document> }
    - On failure: { "status": "fail", "message": "Error message" }
    """
    data = request.get_json()
    required_fields = ["user_id", "birthyear", "gender"]
    for field in required_fields:
        if field not in data:
            return jsonify({"status": "fail", "message": f"Missing field: {field}"}), 400

    try:
        user_info_db.insert_one(data)
        # Update the global variable
        global user_info
        user_info[data["user_id"]] = data
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
        "event_id": "E123",     // Unique identifier for the event
        "lat": 37.7749,
        "lng": -122.4194,
        "words": ["music", "festival", "live"],
        "start": 1370000000     // (Optional) timestamp for event start time
        // ... any additional event information
    }
    
    Response:
    - On success: { "status": "success", "event": <event document> }
    - On failure: { "status": "fail", "message": "Error message" }
    """
    data = request.get_json()
    if "event_id" not in data:
        return jsonify({"status": "fail", "message": "Missing event_id"}), 400

    try:
        event_info_db.insert_one(data)
        # Update global event_info: compute location if lat/lng provided.
        global event_info
        if data.get("lat") is not None and data.get("lng") is not None:
            data["location"] = [data["lat"], data["lng"]]
        else:
            data["location"] = None
        if "words" not in data:
            data["words"] = []
        event_info[data["event_id"]] = data
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
        "user": 1,              // user_id
        "friends": [2, 3, 4]      // list of friend user_ids
    }
    
    Response:
    - On success: { "status": "success", "data": <updated document> }
    - On failure: { "status": "fail", "message": "Error message" }
    """
    data = request.get_json()
    if "user" not in data or "friends" not in data:
        return jsonify({"status": "fail", "message": "Missing user or friends field"}), 400

    try:
        # Upsert document in friends collection
        result = friends_db.update_one({"user": data["user"]},
                                       {"$set": {"friends": data["friends"]}},
                                       upsert=True)
        # Update the global friends variable
        global friends
        friends[data["user"]] = data["friends"]
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
        "user": 1,
        "event": "E123",
        "response": "yes",   // Options can be: "yes", "maybe", "no", "invited"
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
        # Insert the interaction as a new attendance record.
        attendance_db.insert_one(data)
        # Optionally, update the global attendance indices.
        global attendance_by_uid, attendance_by_eid
        uid = data["user"]
        eid = data["event"]
        attendance_by_uid.setdefault(uid, []).append(data)
        attendance_by_eid.setdefault(eid, []).append(data)
        return jsonify({"status": "success", "interaction": data}), 201
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 500

# -------------------------------
# Route: Recommendations
# -------------------------------
@app.route('/recommendations', methods=['POST'])
def recommendations():
    """
    Returns event recommendations for a given user using the pre-trained model.
    
    Expected JSON input:
    {
        "user_id": 1
    }
    
    Process:
    - Loads the full data from MongoDB (users, events, attendance, friends) and updates the global variables.
    - Builds a candidate event dictionary for the user.
      Here, for each event in the event_info collection, we assume a default tuple (invited_flag, timestamp)
      for simplicity.
    - Calls the existing recommendation logic (process_events_for_user) which computes feature vectors for each event.
    - Replaces None values in the feature vector with 0.
    - Uses the pre-trained model to predict scores for each event and sorts them in descending order.
    
    Response:
    {
        "status": "success",
        "user_id": 1,
        "recommendations": [list of event IDs sorted by predicted score]
    }
    """
    data = request.get_json()
    user_id = data.get("user_id")
    if user_id is None:
        return jsonify({"status": "fail", "message": "Missing user_id"}), 400

    if user_id not in user_info:
        return jsonify({"status": "fail", "message": "User not found"}), 404

    # Reload full data from MongoDB (in case there were updates)
    global user_info, event_info, attendance_by_uid, attendance_by_eid, friends
    user_info, event_info, attendance_by_uid, attendance_by_eid, friends = load_full_data_mongo()

    # Build candidate event dictionary for the recommendation logic.
    # For each event, we use a default tuple: (invited_flag=0, timestamp=0).
    e_dict = {}
    for eid in event_info:
        e_dict[eid] = (0, 0)

    # Compute feature vectors for each candidate event using your existing logic.
    features_dict = process_events_for_user(user_id, e_dict)

    # Build the feature matrix (replace None with 0 for model compatibility)
    event_ids = list(features_dict.keys())
    X = []
    for eid in event_ids:
        features = [0 if f is None else f for f in features_dict[eid]]
        X.append(features)
    X = np.array(X)

    if model is None:
        return jsonify({"status": "fail", "message": "Model not loaded"}), 500

    # Get prediction scores and rank the events.
    predictions = model.test(X)
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
