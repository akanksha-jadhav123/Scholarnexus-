"""
Bulk import scholarships from CSV files in data/ folder.
Handles deduplication, normalization, and validation.

Usage:
    python scripts/bulk_import.py
"""
import csv
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from scraper.normalizer import Normalizer
from scraper.validator import Validator
from scraper.deduplicator import Deduplicator

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data"
)


def import_csv_file(path):
    """Import a single CSV file."""
    if not os.path.exists(path):
        print(f"  ⚠️  Not found: {path}")
        return {"inserted": 0, "duplicates": 0, "invalid": 0}

    stats = {"inserted": 0, "duplicates": 0, "invalid": 0}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Add source tracking
                row.setdefault("source", "manual_csv")
                row.setdefault("source_type", "Manual")
                row.setdefault("source_trust_score", 9)
                row.setdefault("status", "Active")

                norm = Normalizer.normalize(row)

                # Validate
                is_valid, errors = Validator.validate(norm)
                if not is_valid:
                    stats["invalid"] += 1
                    continue

                # Dedupe
                if Deduplicator.is_duplicate(db, norm):
                    stats["duplicates"] += 1
                    continue

                # Save
                db.Scholarships.insert_one(norm)
                stats["inserted"] += 1

            except Exception as e:
                stats["invalid"] += 1

    return stats


def main():
    print("\n" + "=" * 70)
    print("  ScholarNexus — Bulk CSV Import")
    print("=" * 70)

    if not os.path.isdir(DATA_DIR):
        print(f"❌ Data directory missing: {DATA_DIR}")
        return

    csv_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")])
    if not csv_files:
        print(f"❌ No CSV files found in {DATA_DIR}")
        return

    print(f"\n  📁 Data folder: {DATA_DIR}")
    print(f"  📄 CSV files found: {len(csv_files)}\n")

    total = {"inserted": 0, "duplicates": 0, "invalid": 0}

    for csv_file in csv_files:
        path = os.path.join(DATA_DIR, csv_file)
        print(f"  📥 Importing: {csv_file}")
        stats = import_csv_file(path)
        print(f"     Inserted: {stats['inserted']}, "
              f"Duplicates: {stats['duplicates']}, "
              f"Invalid: {stats['invalid']}")

        for k in total:
            total[k] += stats[k]

    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  ✅ Total inserted:   {total['inserted']}")
    print(f"  ♻️  Total duplicates: {total['duplicates']}")
    print(f"  ❌ Total invalid:    {total['invalid']}")
    print(f"  🗄️  DB now has:       {db.Scholarships.count_documents({})} scholarships")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()