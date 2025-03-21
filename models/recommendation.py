import random
import time
from math import sqrt
import numpy as np
import pandas as pd
from dateutil.parser import parse
import simplejson as json
import ast
from model import Model
import pickle
import os
from data_processing import process_users, process_events, process_friends, process_attendance, fill_missing_location, process_and_update_ages

# --- Caching Functions ---
def cache_data(filename, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)
    print(f"[CACHE] Data cached to {filename}")  # Prints: Data has been saved to filename

def load_cached_data(filename):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        print(f"[CACHE] Loaded cached data from {filename}")  # Prints: Data loaded from filename
        return data
    return None

def get_user_info():
    filename = 'cache_user_info.pkl'
    user_info = load_cached_data(filename)
    if user_info is None:
        user_info = process_users()
        cache_data(filename, user_info)
    return user_info

def get_event_info():
    filename = 'cache_event_info.pkl'
    event_info = load_cached_data(filename)
    if event_info is None:
        event_info = process_events()
        cache_data(filename, event_info)
    return event_info

def get_friends():
    filename = 'cache_friends.pkl'
    friends = load_cached_data(filename)
    if friends is None:
        friends = process_friends()
        cache_data(filename, friends)
    return friends

def get_attendance():
    filename_uid = 'cache_attendance_by_uid.pkl'
    filename_eid = 'cache_attendance_by_eid.pkl'
    attendance_by_uid = load_cached_data(filename_uid)
    attendance_by_eid = load_cached_data(filename_eid)
    if attendance_by_uid is None or attendance_by_eid is None:
        attendance_by_uid, attendance_by_eid = process_attendance()
        cache_data(filename_uid, attendance_by_uid)
        cache_data(filename_eid, attendance_by_eid)
    return attendance_by_uid, attendance_by_eid

def get_full_data():
    # Load or compute individual parts
    user_info = get_user_info()
    event_info = get_event_info()
    friends = get_friends()
    attendance_by_uid, attendance_by_eid = get_attendance()
    # If none of the users have a location, update missing locations and ages.
    if not any(user.get('location') for user in user_info.values()):
        fill_missing_location(user_info, event_info, attendance_by_uid, attendance_by_eid)
        process_and_update_ages(user_info)
        cache_data('cache_user_info.pkl', user_info)
    return user_info, event_info, attendance_by_uid, attendance_by_eid, friends

user_info, event_info, attendance_by_uid, attendance_by_eid, friends = get_full_data()
print("[INFO] All data loaded successfully.")  # Indicates data processing and caching completed

# --- Helper Functions ---
def memoize(function):
    memo = {}
    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper

def get_event_sim_by_users(id1, id2, exclude):
    attend1 = attendance_by_eid.get(id1, [])
    attend2 = attendance_by_eid.get(id2, [])
    set1 = set()
    set2 = set()
    for a in attend1:
        if a.get('yes') or a.get('maybe'):
            set1.add(a['uid'])
    for a in attend2:
        if a.get('yes') or a.get('maybe'):
            set2.add(a['uid'])
    intersection = set1.intersection(set2)
    s = float(len(intersection))
    if exclude in intersection:
        s -= 1
    if min(len(set1), len(set2)) > 0:
        s /= min(len(set1), len(set2))
    else:
        s = 0
    return s

def get_event_sim_by_cluster(user, event):
    f = []
    for key in ['user_taste', 'friends_taste', 'user_hates', 'friends_hate', 'user_invited']:
        if key in user:
            s = 0
            taste = user[key]
            s += taste['cl0'][event['cl0']] * 8
            s += taste['cl1'][event['cl1']] * 20
            s += taste['cl2'][event['cl2']] * 40
            f.append(s)
        else:
            f.append(None)
    return f

@memoize
def get_user_attendance(uid):
    return attendance_by_uid.get(uid, [])

def get_event_attendance(eid):
    return attendance_by_eid.get(eid, [])

@memoize
def get_event_similarity_by_user_big(uid, eid):
    yes_sim = []
    attend_list_u = get_user_attendance(uid)
    for e2 in attend_list_u:
        if (e2.get('yes') or e2.get('maybe')) and e2['eid'] != eid:
            yes_sim.append(get_event_sim_by_users(eid, e2['eid'], uid))
    if yes_sim:
        return sum(yes_sim) / len(yes_sim)
    return None

def get_location_distance(l1, l2):
    if not l1 or not l2:
        return None
    if isinstance(l1[0], float):
        l1 = [l1]
    if isinstance(l2[0], float):
        l2 = [l2]
    minimum = float('inf')
    for a in l1:
        for b in l2:
            d = sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
            if d < minimum:
                minimum = d
    return minimum

def get_event_distance(w1, w2):
    if not w1 or not w2:
        return None
    w1 = np.array(w1)
    w2 = np.array(w2)
    w1 = np.log(w1 + 1)
    w2 = np.log(w2 + 1)
    denom = (np.sqrt(np.sum(w1 * w1)) * np.sqrt(np.sum(w2 * w2)))
    if denom == 0:
        return None
    s = np.sum(w1 * w2) / denom
    return s

def compare_location_string(s1, s2):
    if not s1 or not s2:
        return 0
    s1 = s1.lower()
    s2 = s2.lower()
    jog = ['yogyakarta', 'jogjakarta']
    if s1 in jog and s2 in jog:
        return 1
    return int(s1 == s2)

def process_locations(elocs, ulocs):
    same_country = 0
    same_state = 0
    same_city = 0
    for el in elocs:
        for ul in ulocs:
            same_country = max(same_country, compare_location_string(el.get('country'), ul.get('country')))
            same_state = max(same_state, compare_location_string(el.get('state'), ul.get('state')))
            same_city = max(same_city, compare_location_string(el.get('city'), ul.get('city')))
            if compare_location_string(el.get('country'), ul.get('country')) and same_city == 0:
                if 'city' in el and 'city' in ul:
                    same_city = 0.5
                elif 'city' in el:
                    same_city = 0.25
    return [same_country + same_state + same_city * 2.0]

ATTR = ['yes', 'no', 'maybe', 'invited']

# --- Process events for a given user ---
def process_events_for_user(uid, e_dict):
    # e_dict maps event id to a tuple (invited_flag, timestamp)
    attend_list_u = get_user_attendance(uid)
    e_list = [event_info[eid] for eid in e_dict.keys() if eid in event_info]
    user = user_info.get(uid)
    attend_dict = {record['eid']: record for record in attend_list_u}
    
    friend_entry = friends.get(uid, [])
    friend_ids = set(friend_entry)
    
    features_dict = {}
    for e in e_list:
        attend_list_e = get_event_attendance(e['id'])
        features = [0, 0, 0, 0]
        for att in attend_list_e:
            if att.get('yes'):
                features[0] += 1
            if att.get('no'):
                features[1] += 1
            if att.get('maybe'):
                features[2] += 1
            if att.get('invited'):
                features[3] += 1
        features.extend([
            features[1] * 1.0 / (features[0] + 1),
            features[2] * 1.0 / (features[0] + 1),
            features[3] * 1.0 / (features[0] + 1),
        ])
        
        features2 = [0, 0, 0, 0]
        for att in attend_list_e:
            if att['uid'] not in friend_ids:
                continue
            if att.get('yes'):
                features2[0] += 1
            if att.get('no'):
                features2[1] += 1
            if att.get('maybe'):
                features2[2] += 1
            if att.get('invited'):
                features2[3] += 1
        features2.extend([
            features2[1] * 1.0 / (features2[0] + 1),
            features2[2] * 1.0 / (features2[0] + 1),
            features2[3] * 1.0 / (features2[0] + 1),
        ])
        features2.extend([
            features2[0] / (len(friend_ids) + 1.0),
            features2[1] / (len(friend_ids) + 1.0),
            features2[2] / (len(friend_ids) + 1.0),
            features2[3] / (len(friend_ids) + 1.0),
        ])
        features.extend(features2)
        
        # Add location difference features (if newloc2 is available)
        features.extend(
            process_locations(
                e.get('newloc2', []),
                user.get('newloc2', [])
            )
        )
        
        # Add age profile difference if available
        if user.get('birth') and isinstance(user.get('birth'), (str, int)) and 'ages' in e:
            try:
                d = abs(2013 - int(user['birth']) - e['ages']['mean'])
            except:
                d = None
            features.append(d + int(random.random() * 6) if d is not None else None)
        else:
            features.append(None)
        
        # Add gender profile
        if user.get('gender') and isinstance(user.get('gender'), str) and 'genders' in e:
            features.append((e['genders'][user['gender']] + 1.0) / (e['genders'].get('male', 0) + e['genders'].get('female', 0) + 2.0))
        else:
            features.append(None)
        
        # Add event similarity by user attendance
        features.append(get_event_similarity_by_user_big(uid, e['id']))
        
        # Add event similarity by clusters
        features.extend(get_event_sim_by_cluster(user, e))
        
        # Add time difference: (event start time - train timestamp)
        if 'start' in e and e_dict.get(e['id']):
            features.append(e['start'] - e_dict[e['id']][1])
        else:
            features.append(None)
        
        # Add flag if event creator is a friend
        features.append(e.get('creator') in friend_ids)
        
        # Add prototype (word model) similarity features if available
        if 'prototype' in user:
            features.append(get_event_distance(user['prototype'], e['words']))
        else:
            features.append(None)
        
        if 'prototype' in user and 'prototype_invite' in user:
            v1 = get_event_distance(user['prototype'], e['words'])
            v2 = get_event_distance(user['prototype_invite'], e['words'])
            if v1 is not None and v2 is not None:
                features.append(v1 - v2)
            else:
                features.append(None)
        else:
            features.append(None)
        if 'prototype_hate' in user and 'prototype_invite' in user:
            v1 = get_event_distance(user['prototype_hate'], e['words'])
            v2 = get_event_distance(user['prototype_invite'], e['words'])
            if v1 is not None and v2 is not None:
                features.append(v1 - v2)
            else:
                features.append(None)
        else:
            features.append(None)
        if 'prototype_hate' in user and 'prototype' in user:
            v1 = get_event_distance(user['prototype_hate'], e['words'])
            v2 = get_event_distance(user['prototype'], e['words'])
            if v1 is not None and v2 is not None:
                features.append(v1 - v2)
            else:
                features.append(None)
        else:
            features.append(None)
        
        # Add the invited flag from the training data (if present)
        if e_dict.get(e['id']):
            features.append(e_dict[e['id']][0])
        else:
            features.append(None)
        
        # Add old location distance (event vs. user)
        features.append(get_location_distance(e.get('location'), user.get('location')))
            
        features_dict[e['id']] = features
        
    return features_dict

def write_submission(submission_name, user_events_dict):
    users = sorted(user_events_dict)
    events = [' '.join([str(s) for s in user_events_dict[u]]) for u in users]
    submission = pd.DataFrame({"User": users, "Events": events})
    submission[["User", "Events"]].to_csv(submission_name, index=False)
    print(f"[SUBMISSION] Saved submission to {submission_name}")  # Informs that the submission CSV is saved

# --- Data splitting and evaluation functions ---

def get_crossval_data():
    train = pd.read_csv("models/data/train.csv")
    train_dict = {}
    duplicates = set()
    for _, row in train.iterrows():
        uid = row['user']
        key = (uid, row['event'])
        if key in duplicates:
            continue
        duplicates.add(key)
        if uid not in train_dict:
            train_dict[uid] = []
        train_dict[uid].append({
            'eid': row['event'],
            'invited': row['invited'],
            'interested': row['interested'],
            'not_interested': row['not_interested'],
            'timestamp': time.mktime(parse(row['timestamp']).timetuple())
        })
    splits = []
    keys_list = list(train_dict.keys())
    n = len(keys_list)
    split_indices = [0, n // 2, n]
    for i in range(2):
        X = []
        Y1 = []
        Y2 = []
        results = {}
        keys_out = []
        count = train['user'].count()
        for uid in keys_list[split_indices[i]:split_indices[i + 1]]:
            events = train_dict[uid]
            e_dict = {e['eid']: (e['invited'], e['timestamp']) for e in events}
            features_dict = process_events_for_user(uid, e_dict)
            # Print progress: percent of X built for this split
            if random.random() < 0.1:
                progress = len(X) * 100.0 / count
                print(f"[CROSSVAL] Processed features: {progress:.2f}% complete for split {i+1}")
            results[uid] = []
            for e in events:
                eid = e['eid']
                if eid not in features_dict:
                    continue  # Skip event if not processed
                X.append(features_dict[eid])
                Y1.append(e['interested'])
                Y2.append(e['not_interested'])
                keys_out.append((uid, e['eid']))
                if e['interested']:
                    results.setdefault(uid, []).append(e['eid'])
        splits.append((X, Y1, Y2, results, keys_out))
    return splits

def get_test_data():
    solutions_df = pd.read_csv("models/data/public_leaderboard_solution.csv")
    solutions_dict = {}
    for _, row in solutions_df.iterrows():
        uid = int(row['User'])
        eid = int(row['Events'])
        solutions_dict[uid] = [eid]
    test = pd.read_csv("models/data/test.csv")
    test_dict = {}
    for _, row in test.iterrows():
        uid = row['user']
        if uid not in solutions_dict:
            continue
        if uid not in test_dict:
            test_dict[uid] = []
        test_dict[uid].append({
            'eid': row['event'],
            'invited': row['invited'],
            'timestamp': time.mktime(parse(row['timestamp']).timetuple())
        })
    count = len(test_dict)
    test_data = {}
    for uid, events in test_dict.items():
        e_dict = {e['eid']: (e['invited'], e['timestamp']) for e in events}
        count -= 1
        print(f"[TEST DATA] Processing test data for user {uid}; remaining users: {count}")
        features_dict = process_events_for_user(uid, e_dict)
        X = []
        for e in events:
            eid = e['eid']
            if eid not in features_dict:
                continue
            X.append(features_dict[eid])
        test_data[uid] = {'X': X, 'events': events}
    return test_data

def get_final_data():
    final_df = pd.read_csv("models/data/event_popularity_benchmark_private_test_only.csv")
    final_dict = {}
    for _, row in final_df.iterrows():
        uid = int(row['User'])
        # Remove trailing "L" characters and safely evaluate to a Python list
        events_str = row['Events'].replace("L", "")
        eid = ast.literal_eval(events_str)
        if uid in final_dict:
            raise Exception("Duplicate user in final data!")
        final_dict[uid] = eid
    return final_dict

def run_model(m1, m2, test_data, is_final=True):
    final_dict = get_final_data()
    results = {}
    for uid, record in test_data.items():
        if is_final and uid not in final_dict:
            continue

        X = np.array(record['X'])
        print(f"[RUN MODEL] User {uid}: Feature matrix shape = {X.shape}")  # Prints the shape of X for each user
        
        if X.size == 0 or len(X.shape) < 2:
            print(f"[RUN MODEL] User {uid} has no event features; skipping.")  # Warning for empty features
            continue

        events = record['events']
        Y1 = m1.test(X)  # Expecting one prediction per event
        
        if len(Y1) != len(events):
            print(f"[RUN MODEL] Warning: For user {uid}, number of predictions ({len(Y1)}) does not match number of events ({len(events)}).")
        
        sorted_events = []
        for i, e in enumerate(events):
            score = Y1[i] if i < len(Y1) else 0
            sorted_events.append((e['eid'], score))
        sorted_events.sort(key=lambda x: -x[1])
        sorted_events = [e[0] for e in sorted_events]
        results[uid] = sorted_events
        print(f"[RUN MODEL] User {uid}: Final sorted event IDs: {results[uid]}")  # Print final recommendations per user
    return results

def run_crossval():
    splits = get_crossval_data()
    results_list = []
    for i in range(2):
        s = splits[i]
        other_s = splits[1 - i]
        z = [True] * len(s[0][0])
        w = [True] * len(s[0][0])
        remove_features_rfc = [19, 20]
        remove_features_lr = [19, 20, 21, 22, 23, 24, 25, 26, 29, 30, 31, 32]
        for idx in remove_features_rfc:
            z[idx] = False
        for idx in remove_features_lr:
            w[idx] = False
        from model import Model  # ensure model.py is available
        m1 = Model(compress=z, has_none=w)
        m1.fit(s[0], s[1])
        X = other_s[0]
        predictions = m1.test(X)
        keys = other_s[4]
        pred_dict = {}
        for j in range(len(keys)):
            uid, eid = keys[j]
            pred_dict.setdefault(uid, []).append((eid, predictions[j]))
        for uid, l in pred_dict.items():
            l.sort(key=lambda x: -x[1])
            l = [e[0] for e in l]
            results_list.append(apk(other_s[3][uid], l))
    average_apk = sum(results_list) / len(results_list)
    print(f"[CROSSVAL] Average APK score across splits: {average_apk:.4f}")
    
def get_test_solutions():
    solutions_df = pd.read_csv("models/data/public_leaderboard_solution.csv")
    solutions_dict = {}
    for _, row in solutions_df.iterrows():
        uid = int(row['User'])
        eid = int(row['Events'])
        solutions_dict[uid] = [eid]
    return solutions_dict

def evaluate_test_results(my_results):
    solutions_dict = get_test_solutions()
    scores = []
    for uid, l in my_results.items():
        score = apk(solutions_dict[uid], l)
        scores.append(score)
    average_score = sum(scores) / len(scores)
    print(f"[EVALUATE] Average test score: {average_score:.4f}")
    return average_score

def run_full():
    splits = get_crossval_data()
    X = splits[0][0] + splits[1][0]
    Y1 = splits[0][1] + splits[1][1]
    Y2 = splits[0][2] + splits[1][2]
    test_data = get_test_data()
    remove_features_rfc = [19, 20, 34]
    remove_features_lr = [19, 20, 21, 22, 23, 24, 25, 26, 29, 30, 31, 32, 34]
    not_useful_rfc = [8, 11, 22, 24, 28, 33, 30, 31, 32]
    remove_features_rfc.extend(not_useful_rfc)
    not_useful_lr = [3, 4, 9, 11, 14, 15, 16, 17, 27, 28, 30, 31, 32]
    remove_features_lr.extend(not_useful_lr)
    z = [True] * len(X[0])
    w = [True] * len(X[0])
    for idx in remove_features_rfc:
        z[idx] = False
    for idx in remove_features_lr:
        w[idx] = False
    from model import Model  # ensure model.py is available
    C = 0.03
    m1 = Model(compress=z, has_none=w, C=C)
    m1.fit(X, Y1)
    # Save the trained model to a file
    model_filename = "trained_model.pkl"
    with open(model_filename, "wb") as f:
        pickle.dump(m1, f)
    print(f"[MODEL SAVE] Model saved to {model_filename}")
    
    final = False
    results = run_model(m1, None, test_data, is_final=final)
    if not final:
        evaluate_test_results(results)
    write_submission('output.csv', results)

# apk (average precision at k) is assumed to be defined in eval.py
from eval import apk

if __name__ == "__main__":
    run_full()
