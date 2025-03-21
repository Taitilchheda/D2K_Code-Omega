import pandas as pd
import numpy as np
from math import isnan
from dateutil.parser import parse
from collections import defaultdict

def process_users():
    users_df = pd.read_csv("data/event_recommendation/users.csv")
    user_info = {}
    for _, row in users_df.iterrows():
        uid = int(row['user_id'])
        user_info[uid] = {
            'id': uid,
            'birth': row['birthyear'],
            'gender': row['gender'],
            'location': None  # will be filled later via inference
            # add any additional fields if needed
        }
    return user_info

def process_events():
    events_df = pd.read_csv("data/event_recommendation/events.csv")
    event_info = {}
    for _, row in events_df.iterrows():
        eid = row['event_id']
        location = None
        if not pd.isna(row['lat']) and not pd.isna(row['lng']):
            location = [row['lat'], row['lng']]
        # Extract feature words from columns 9 to 110 (if available)
        words = row.iloc[9:110].tolist() if len(row) >= 110 else []
        event = row.to_dict()
        event['location'] = location
        event['words'] = words
        event['id'] = eid  # Add this line to ensure 'id' is present
        event_info[eid] = event
    return event_info


def process_friends():
    friends_df = pd.read_csv("data/event_recommendation/user_friends.csv")
    friends = {}
    for _, row in friends_df.iterrows():
        uid = row['user']
        if pd.isna(row['friends']):
            continue
        friend_list = [int(u) for u in str(row['friends']).split()]
        friends[uid] = friend_list
    return friends

def update_attendance(uid, eid, att_type, attendance_dict):
    key = (uid, eid)
    if key not in attendance_dict:
        attendance_dict[key] = {'uid': uid, 'eid': eid}
    attendance_dict[key][att_type] = True

def process_attendance():
    attendance_dict = {}
    # Process event_attendees.csv
    event_attendees_df = pd.read_csv("data/event_recommendation/event_attendees.csv")
    for _, row in event_attendees_df.iterrows():
        eid = row['event']
        for attr in ['yes', 'maybe', 'invited', 'no']:
            val = row[attr]
            if pd.isna(val):
                continue
            users = [int(u) for u in str(val).split()]
            for uid in users:
                update_attendance(uid, eid, attr, attendance_dict)
    # Process train.csv (which adds extra attendance info)
    train_df = pd.read_csv("data/event_recommendation/train.csv", converters={"timestamp": parse})
    for _, row in train_df.iterrows():
        uid = row['user']
        eid = row['event']
        for attr in ['invited', 'interested', 'not_interested']:
            if row[attr]:
                update_attendance(uid, eid, attr, attendance_dict)
    # Build indices: attendance_by_uid and attendance_by_eid
    attendance_by_uid = {}
    attendance_by_eid = {}
    for record in attendance_dict.values():
        uid = record['uid']
        eid = record['eid']
        attendance_by_uid.setdefault(uid, []).append(record)
        attendance_by_eid.setdefault(eid, []).append(record)
    return attendance_by_uid, attendance_by_eid

def fill_missing_location(user_info, event_info, attendance_by_uid, attendance_by_eid):
    # Get users and events that already have a location.
    user_sure = {uid: user['location'] for uid, user in user_info.items() if user.get('location')}
    event_sure = {eid: event['location'] for eid, event in event_info.items() if event.get('location')}
    # Infer event location from attendance votes
    for eid, event in event_info.items():
        if event.get('location'):
            continue
        votes = {}
        if eid in attendance_by_eid:
            for att in attendance_by_eid[eid]:
                if 'yes' not in att:
                    continue
                user_loc = user_sure.get(att['uid'])
                if user_loc:
                    key = tuple(user_loc)
                    votes[key] = votes.get(key, 0) + 1
        if votes:
            best_loc = max(votes.items(), key=lambda x: x[1])[0]
            event_info[eid]['location'] = list(best_loc)
    # Infer user location from events attended
    for uid, user in user_info.items():
        if user.get('location'):
            continue
        votes = {}
        if uid in attendance_by_uid:
            for att in attendance_by_uid[uid]:
                event_loc = event_sure.get(att['eid'])
                if event_loc:
                    key = tuple(event_loc)
                    votes[key] = votes.get(key, 0) + 1
        if votes:
            best_loc = max(votes.items(), key=lambda x: x[1])[0]
            user_info[uid]['location'] = list(best_loc)

def process_and_update_ages(user_info):
    for uid, user in user_info.items():
        birthyear = user.get('birth')
        try:
            year = int(birthyear)
            if year < 1940 or year > 2005:
                age = None
            else:
                age = 2013 - year
        except:
            age = None
        user_info[uid]['age'] = age

def process_data():
    user_info = process_users()
    event_info = process_events()
    friends = process_friends()
    attendance_by_uid, attendance_by_eid = process_attendance()
    fill_missing_location(user_info, event_info, attendance_by_uid, attendance_by_eid)
    process_and_update_ages(user_info)
    return user_info, event_info, attendance_by_uid, attendance_by_eid, friends

if __name__ == "__main__":
    ui, ei, at_uid, at_eid, fr = process_data()
    print("Data processing complete!")