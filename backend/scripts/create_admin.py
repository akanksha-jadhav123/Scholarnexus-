"""
Secure admin creation.
Usage:
    set ADMIN_EMAIL=admin@scholarnexus.com
    set ADMIN_PASSWORD=YourStrongPassword
    python scripts/create_admin.py
"""
import os
import sys
import bcrypt
import getpass
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db


def main():
    email = os.getenv("ADMIN_EMAIL") or input("Admin email: ").strip()
    password = os.getenv("ADMIN_PASSWORD") or getpass.getpass("Admin password (min 8 chars): ")

    if not email or "@" not in email:
        print("❌ Invalid email")
        return
    if not password or len(password) < 8:
        print("❌ Password must be at least 8 characters")
        return

    existing = db.Users.find_one({"email": email})
    if existing:
        if existing.get("role") == "admin":
            print(f"ℹ️  Admin already exists: {email}")
            return
        # Upgrade existing user to admin
        db.Users.update_one(
            {"email": email},
            {"$set": {"role": "admin", "updated_at": datetime.utcnow()}}
        )
        print(f"✅ Upgraded {email} to admin")
        return

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    db.Users.insert_one({
        "name": "ScholarNexus Admin",
        "email": email,
        "password_hash": hashed,
        "role": "admin",
        "bookmarks": [],
        "created_at": datetime.utcnow()
    })
    print(f"✅ Admin created: {email}")


if __name__ == "__main__":
    main()