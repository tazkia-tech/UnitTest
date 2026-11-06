import re


def validate_username(username):
    return isinstance(username, str) and 3 <= len(username) <= 20


def validate_email(email):
    if not isinstance(email, str):
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def validate_password(password):
    return isinstance(password, str) and len(password) >= 6
