# auth.py
from models import User

users = [
    User("john_seeker", "pass123", "Seeker"),
    User("mary_volunteer", "pass123", "Volunteer")
]

def authenticate(username, password):
    for user in users:
        if user.username == username and user.password == password:
            return user
    return None

def register(username, password, role):
    users.append(User(username, password, role))
