import random
import string

class Utils:
    @staticmethod
    def generate_random_user_id(user_collection, length=6):
        while True:
            course_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if user_collection.find_one({"course_code": course_code}) is None:
                return course_code