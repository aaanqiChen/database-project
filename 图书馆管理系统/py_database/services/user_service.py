from models.user import User

def add_user(username, password, contact):
    User.add_user(username, password, contact)