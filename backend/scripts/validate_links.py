"""
Re-validates all existing application_url links in the DB.
Updates link_status and last_verified fields.

Usage: python scripts/validate_links.py
"""
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from scraper.link_validator import LinkValidator


def main():
    validator = LinkValidator(delay=0.5)
    total = db.Scholarships.count_documents({})
    print(f"\nValidating {total} scholarship links...\n")

    stats = {"active": 0, "broken": 0, "pending": 0}

    for i, sc in enumerate(db.Scholarships.find({}), 1):
        url = sc.get("application_url")
        if not url:
            continue

        result = validator.validate(url)
        stats[result["status"]] = stats.get(result["status"], 0) + 1

        db.Scholarships.update_one(
            {"_id": sc["_id"]},
            {"$set": {
                "link_status": result["status"],
                "link_http_code": result["http_code"],
                "last_verified": datetime.utcnow().isoformat()
            }}
        )

        emoji = {"active": "✅", "broken": "❌", "pending": "⏳", "invalid": "⚠️"}.get(result["status"], "?")
        print(f"  {emoji} [{i}/{total}] {sc['scholarship_name'][:50]}...")

    print(f"\n=== RESULTS ===")
    print(f"  ✅ Active:  {stats.get('active', 0)}")
    print(f"  ❌ Broken:  {stats.get('broken', 0)}")
    print(f"  ⏳ Pending: {stats.get('pending', 0)}")
    print(f"  ⚠️  Invalid: {stats.get('invalid', 0)}")


if __name__ == "__main__":
    main()