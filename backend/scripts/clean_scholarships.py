"""
Data cleaning:
- Mark expired scholarships
- Fill unknown fields with null (not 0)
- Flag incomplete records

Usage: python scripts/clean_scholarships.py
"""
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db


def main():
    today = datetime.utcnow().date().isoformat()
    stats = {
        "expired_marked": 0,
        "unknown_cleared": 0,
        "quality_flagged": 0
    }

    print("\n" + "=" * 60)
    print("  Data Cleaning — Scholarships")
    print("=" * 60)

    # 1. Mark expired
    expired = db.Scholarships.update_many(
        {"application_deadline": {"$lt": today}, "status": "Active"},
        {"$set": {"status": "Expired", "expired_at": datetime.utcnow().isoformat()}}
    )
    stats["expired_marked"] = expired.modified_count
    print(f"  ✅ Marked {stats['expired_marked']} expired")

    # 2. Clear misleading zeros
    cleared = db.Scholarships.update_many(
        {"$or": [
            {"minimum_percentage": 0},
            {"scholarship_amount": 0},
            {"max_family_income": 999999999}
        ]},
        {"$set": {
            "minimum_percentage": None,
            "scholarship_amount": None,
            "max_family_income": None,
        }}
    )
    stats["unknown_cleared"] = cleared.modified_count
    print(f"  ✅ Cleared {stats['unknown_cleared']} misleading zeros")

    # 3. Flag incomplete records
    incomplete = db.Scholarships.update_many(
        {"$or": [
            {"scholarship_name": None},
            {"scholarship_name": ""},
            {"application_url": None},
            {"application_url": ""}
        ]},
        {"$set": {"data_quality": {"complete": False, "reason": "missing critical fields"}}}
    )
    stats["quality_flagged"] = incomplete.modified_count
    print(f"  ✅ Flagged {stats['quality_flagged']} incomplete records")

    print("\n" + "=" * 60)
    print(f"  DONE — Total records: {db.Scholarships.count_documents({})}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()