import re


def is_valid_email(email):
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email or ""))


def is_valid_password(pw):
    return bool(pw and len(pw) >= 6)