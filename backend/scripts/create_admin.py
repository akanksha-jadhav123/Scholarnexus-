import os
import sys
import bcrypt
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["scholarnexus"]

email = "admin@scholarnexus.com"
password = "admin123"

if db.Users.find_one({"email": email}):
    print("Admin already exists.")
else:
    db.Users.insert_one({
        "name": "ScholarNexus Admin",
        "email": email,
        "password_hash": bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
        "role": "admin",
        "bookmarks": [],
        "created_at": datetime.utcnow()
    })
    print(f"[ScholarNexus] Admin created: {email} / {password}")