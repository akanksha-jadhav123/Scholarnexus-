"""
Per-source health check — runs each scraper INDIVIDUALLY.
Reports which sources work, fail, or return 0 records.

Usage: python scripts/scraper_health_check.py
"""
import os
import sys
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.crawler import SCRAPER_CLASSES


def main():
    print("\n" + "=" * 70)
    print(f"  Scraper Health Check — {datetime.utcnow().isoformat()}")
    print(f"  Sources: {len(SCRAPER_CLASSES)}")
    print("=" * 70 + "\n")

    working = []
    broken = []
    empty = []

    for cls in SCRAPER_CLASSES:
        try:
            scraper = cls()
            t0 = time.time()
            try:
                records = scraper.scrape()
                duration = round(time.time() - t0, 2)

                if len(records) > 0:
                    print(f"  ✅ {scraper.source_name:40s} {len(records):3d} records ({duration}s)")
                    working.append((scraper.source_name, len(records)))
                else:
                    print(f"  ⚠️  {scraper.source_name:40s}   0 records ({duration}s)")
                    empty.append(scraper.source_name)
            except Exception as e:
                print(f"  ❌ {scraper.source_name:40s} ERROR: {str(e)[:60]}")
                broken.append((scraper.source_name, str(e)[:100]))
        except Exception as e:
            print(f"  ❌ {cls.__name__:40s} INIT ERROR: {str(e)[:60]}")
            broken.append((cls.__name__, str(e)[:100]))

    print("\n" + "=" * 70)
    print(f"  WORKING: {len(working)} | EMPTY: {len(empty)} | BROKEN: {len(broken)}")
    print("=" * 70)
    print(f"\n✅ Working sources (yield records):")
    for name, n in working:
        print(f"   • {name} ({n} records)")

    print(f"\n⚠️  Empty sources (0 records):")
    for name in empty:
        print(f"   • {name}")

    print(f"\n❌ Broken sources (errors):")
    for name, err in broken:
        print(f"   • {name} — {err}")


if __name__ == "__main__":
    main()