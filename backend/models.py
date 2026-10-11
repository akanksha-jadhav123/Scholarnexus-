import bcrypt
from datetime import datetime
from database import get_db
from bson import ObjectId


def get_users_collection():
    return get_db()["users"]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_user(name, email, password):
    users = get_users_collection()
    if users.find_one({"email": email.lower()}):
        return None, "Email already registered"
    user_doc = {
        "name": name,
        "email": email.lower(),
        "password": hash_password(password),
        "created_at": datetime.now()
    }
    result = users.insert_one(user_doc)
    return str(result.inserted_id), None


def find_user_by_email(email):
    return get_users_collection().find_one({"email": email.lower()})


def find_user_by_id(user_id):
    try:
        return get_users_collection().find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None