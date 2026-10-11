"""
One-shot full auto-scrape from all registered sources.
Usage: python scripts/auto_scrape.py
"""
import os
import sys
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from services.scholarship_sync import ScholarshipSync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def main():
    print("\n" + "=" * 70)
    print("  ScholarNexus — FULL AUTO SCRAPE (all registered sources)")
    print("=" * 70)
    print(f"  Started: {datetime.utcnow().isoformat()}")
    print(f"  Before:  {db.Scholarships.count_documents({})} scholarships")
    print("=" * 70 + "\n")

    sync = ScholarshipSync(db=db)
    stats = sync.run()

    print("\n" + "=" * 70)
    print("  RESULTS BY SOURCE")
    print("=" * 70)
    for src in stats.get("sources", []):
        status = "OK  " if src.get("records", 0) > 0 else "--  "
        print(f"  {status} {src['source']:40s} {src.get('records', 0):3d} records")

    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Crawled:    {stats.get('crawled', 0)}")
    print(f"  Validated:  {stats.get('validated', 0)}")
    print(f"  Duplicates: {stats.get('duplicates', 0)}")
    print(f"  Rejected:   {stats.get('rejected', 0)}")
    print(f"  Saved:      {stats.get('saved', 0)}")
    print(f"  DB total:   {stats.get('db_total', 0)}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
