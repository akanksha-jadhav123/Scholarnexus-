import csv
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env from backend folder (one level up from scripts/)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

load_dotenv(os.path.join(BACKEND_DIR, ".env"))

client = MongoClient(os.getenv("MONGO_URI"))
db = client["scholarnexus"]
col = db["Scholarships"]


def import_csv(path):
    if not os.path.exists(path):
        print(f"❌ CSV not found at: {path}")
        print(f"   Please place scholarships_initial.csv at that path.")
        return

    inserted, skipped = 0, 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if col.find_one({"scholarship_id": row["scholarship_id"]}):
                skipped += 1
                continue
            row["minimum_percentage"] = float(row.get("minimum_percentage") or 0)
            row["max_family_income"] = float(row.get("max_family_income") or 0)
            row["scholarship_amount"] = float(row.get("scholarship_amount") or 0)
            row["required_documents"] = [
                d.strip() for d in (row.get("required_documents") or "").split(";") if d.strip()
            ]
            row.setdefault("status", "Active")
            col.insert_one(row)
            inserted += 1
    print(f"[ScholarNexus] Inserted: {inserted}, Skipped (duplicates): {skipped}")


if __name__ == "__main__":
    csv_path = os.path.join(PROJECT_ROOT, "data", "scholarships_initial.csv")
    print(f"Looking for CSV at: {csv_path}")
    import_csv(csv_path)