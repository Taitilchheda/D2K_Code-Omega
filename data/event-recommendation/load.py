import pandas as pd
import numpy as np
from pymongo import MongoClient, ASCENDING
from dateutil.parser import parse
from urllib.parse import quote_plus
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
password = quote_plus(os.getenv("MONGO_PASS"))
uri = f"mongodb+srv://kakashiforwork:{password}@cluster0.emman.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client["D2K"]

user_info = db.user_info
event_info = db.event_info
attendance = db.attendance
friends_db = db.friends

def reset_indexes():
    user_info.drop()
    event_info.drop()
    attendance.drop()
    friends_db.drop()

    user_info.create_index('id', unique=True)
    event_info.create_index('id', unique=True)
    attendance.create_index('uid')
    attendance.create_index('eid')
    attendance.create_index([('uid', ASCENDING), ('eid', ASCENDING)])
    friends_db.create_index('uid')


def process_users(path):
    df = pd.read_csv(path)
    for _, user in df.iterrows():
        user_info_dict = {
            'id': int(user['user_id']),
            'birth': user['birthyear'],
            'gender': user['gender'],
            'location': None
        }
        user_info.insert_one(user_info_dict)
    print("Users processed")


def update_attendance(uid, eid, att_type):
    attendance.update_one(
        {'uid': uid, 'eid': eid},
        {'$set': {'uid': uid, 'eid': eid, att_type: True}},
        upsert=True)


def process_attendance(attendance_path, train_path):
    df = pd.read_csv(attendance_path)
    for _, event in df.iterrows():
        eid = event['event']
        for attr in ['yes', 'maybe', 'invited', 'no']:
            users = event[attr]
            if isinstance(users, float):  # handle NaN
                continue
            users = [int(u) for u in users.split()]
            for uid in users:
                update_attendance(uid, eid, attr)

    train = pd.read_csv(train_path, converters={"timestamp": parse})
    for _, pair in train.iterrows():
        uid = pair['user']
        eid = pair['event']
        for attr in ['invited', 'interested', 'not_interested']:
            if pair[attr]:
                update_attendance(uid, eid, attr)
    print("Attendance processed")


def process_events(events_path):
    chunks = pd.read_csv(events_path, iterator=True, chunksize=1000)
    for chunk in chunks:
        for _, e in chunk.iterrows():
            eid = e['event_id']
            location = None
            if not np.isnan(e['lat']) and not np.isnan(e['lng']):
                location = [e['lat'], e['lng']]
            words = list(e[9:110])  # custom feature words
            event_info.insert_one({'id': eid, 'location': location, 'words': words})
    print("Events processed")


def process_friends(friends_path):
    df = pd.read_csv(friends_path)
    for _, record in df.iterrows():
        uid1 = record['user']
        if isinstance(record['friends'], float):
            continue
        friends = [int(u) for u in record['friends'].split()]
        friends_db.insert_one({'uid': uid1, 'friends': friends})
    print("Friends processed")


def infer_missing_locations():
    user_known_locs = {u['id']: u['location'] for u in user_info.find() if u['location']}
    event_known_locs = {e['id']: e['location'] for e in event_info.find() if e['location']}

    for event in event_info.find({'location': None}):
        votes = {}
        for a in attendance.find({'eid': event['id']}):
            if 'yes' not in a:
                continue
            user_loc = user_known_locs.get(a['uid'])
            if user_loc:
                votes[tuple(user_loc)] = votes.get(tuple(user_loc), 0) + 1
        if votes:
            best_loc = max(votes.items(), key=lambda x: x[1])[0]
            event_info.update_one({'id': event['id']}, {'$set': {'location': list(best_loc)}})

    for user in user_info.find({'location': None}):
        votes = {}
        for a in attendance.find({'uid': user['id']}):
            event_loc = event_known_locs.get(a['eid'])
            if event_loc:
                votes[tuple(event_loc)] = votes.get(tuple(event_loc), 0) + 1
        if votes:
            best_loc = max(votes.items(), key=lambda x: x[1])[0]
            user_info.update_one({'id': user['id']}, {'$set': {'location': list(best_loc)}})


def update_user_ages():
    for user in user_info.find():
        birthyear = user.get('birth')
        try:
            age = int(birthyear)
            if age < 1940 or age > 2005:
                age = None
            else:
                age = 2013 - age
        except:
            age = None
        user_info.update_one({'id': user['id']}, {'$set': {'age': age}})


def main():
    reset_indexes()
    process_users("data/event-recommendation/users.csv")
    process_attendance("data/event-recommendation/event_attendees.csv", "data/event-recommendation/train.csv")
    process_friends("data/event-recommendation/user_friends.csv")
    # process_events("data/event-recommendation/events.csv")
    infer_missing_locations()
    update_user_ages()
    print("ETL pipeline completed successfully!")


if __name__ == "__main__":
    main()
