import random
import string
from sqlalchemy.orm import Session

class Utils:
    @staticmethod
    def generate_random_user_id(session: Session, UserModel, length=6):
        while True:
            uid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            # SQLAlchemy query to check if user_id exists
            existing_user = session.query(UserModel).filter_by(user_id=uid).first()
            if existing_user is None:
                return uid

    @staticmethod
    def generate_random_event_id(session: Session, EventModel, length=6):
        while True:
            eid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            # SQLAlchemy query to check if event_id exists
            existing_event = session.query(EventModel).filter_by(event_id=eid).first()
            if existing_event is None:
                return eid
