import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "scholarnexus"   # ← changed to lowercase

def get_db():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db

def get_scholarship_collection():
    db = get_db()
    return db["scholarships"]