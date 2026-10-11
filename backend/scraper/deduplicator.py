"""
Detects duplicate scholarships by multiple strategies.
"""
import re


class Deduplicator:

    @staticmethod
    def is_duplicate(db, record):
        # 1. Exact scholarship_id
        if record.get("scholarship_id"):
            if db.Scholarships.find_one({"scholarship_id": record["scholarship_id"]}):
                return True

        # 2. Same name + provider (case-insensitive)
        if record.get("scholarship_name") and record.get("provider"):
            if db.Scholarships.find_one({
                "scholarship_name": {
                    "$regex": f"^{re.escape(record['scholarship_name'])}$",
                    "$options": "i"
                },
                "provider": {
                    "$regex": f"^{re.escape(record['provider'])}$",
                    "$options": "i"
                }
            }):
                return True

        # 3. Same application URL
        if record.get("application_url"):
            if db.Scholarships.find_one({"application_url": record["application_url"]}):
                return True

        # 4. Fuzzy name prefix match (first 6 words)
        name = (record.get("scholarship_name") or "").lower()
        if name:
            prefix = " ".join(name.split()[:6])
            if len(prefix) > 15:
                if db.Scholarships.find_one({
                    "scholarship_name": {
                        "$regex": f"^{re.escape(prefix)}",
                        "$options": "i"
                    }
                }):
                    return True

        return False