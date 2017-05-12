from sqlalchemy import and_, or_, desc, text, exc
from models import Users
from primers import message

def get_users(s):
    """
    gets all users
    :param s: database session
    :return: sql alchemy generator object
    """
    users = s.query(Users).order_by(Users.username).values(Users.id,Users.username,Users.admin)
    return users


def get_username_by_user_id(s, user_id):
    username = s.query(Users).filter_by(id=user_id).values(Users.username)
    for i in username:
        return i.username


def get_user_by_username(s, username):
    user = s.query(Users).filter_by(username=username)
    return user