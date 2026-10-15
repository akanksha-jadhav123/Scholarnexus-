"""
MongoDB connection + collection accessors.
All modules import from here.
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "scholarnexus")

# MongoDB client — used for admin ping / health checks
client = MongoClient(MONGO_URI)

# Database handle — used by all routes
db = client[DB_NAME]


def get_db():
    """Return the database handle."""
    return db


def get_users_collection():
    return db.Users


def get_scholarship_collection():
    return db.Scholarships


def get_profiles_collection():
    return db.StudentProfiles


def get_applications_collection():
    return db.Applications


def get_notifications_collection():
    return db.Notifications


def get_document_checklists_collection():
    return db.DocumentChecklists


# ---------- INDEXES (idempotent — safe to call on every boot) ----------
def ensure_indexes():
    try:
        db.Users.create_index("email", unique=True)
        db.Scholarships.create_index("scholarship_id", unique=True, sparse=True)
        db.Scholarships.create_index("status")
        db.Scholarships.create_index("source")
        db.Scholarships.create_index([("scholarship_name", "text"),
                                      ("provider", "text")])
        db.StudentProfiles.create_index("user_id", unique=True)
        db.Applications.create_index([("user_id", 1), ("scholarship_id", 1)],
                                     unique=True)
        db.Notifications.create_index([("user_id", 1), ("created_at", -1)])
        db.DocumentChecklists.create_index([("user_id", 1), ("scholarship_id", 1)],
                                           unique=True)
    except Exception:
        # Index creation may fail on first boot or under race; harmless.
        pass