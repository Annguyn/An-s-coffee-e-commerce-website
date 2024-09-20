from models.user import User
from flask import session

def get_logged_in_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None