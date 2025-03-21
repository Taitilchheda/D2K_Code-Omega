import random, string

class Utils:
    @staticmethod
    def generate_random_user_id(user_collection, length=6):
        while True:
            uid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if user_collection.find_one({"user_id": uid}) is None:
                return uid

    @staticmethod
    def generate_random_event_id(event_collection, length=6):
        while True:
            eid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if event_collection.find_one({"event_id": eid}) is None:
                return eid
