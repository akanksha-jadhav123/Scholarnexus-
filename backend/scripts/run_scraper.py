import os
import sys
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from scraper.pipeline import ScraperPipeline
from scraper.source_manager import get_all_scrapers

# Log to file
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "scraper.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    print("\n" + "=" * 70)
    print("  ScholarNexus — Multi-Source Scraper (Priority 2)")
    print("=" * 70)
    print(f"  Started: {datetime.utcnow().isoformat()}")

    scrapers = get_all_scrapers()
    print(f"  Sources registered: {len(scrapers)}")
    print("=" * 70)

    pipeline = ScraperPipeline(
        db=db,
        scrapers=scrapers,
        validate_links=True   # Enable link validation
    )
    stats = pipeline.run()

    print("\n" + "=" * 70)
    print("  RESULTS BY SOURCE")
    print("=" * 70)

    for src in stats["sources"]:
        status = "✅" if src["saved"] > 0 else "⚠️ "
        print(f"\n  {status} {src['source']}")
        print(f"     Scraped:     {src['scraped']}")
        print(f"     Saved:       {src['saved']}")
        print(f"     Duplicates:  {src['duplicates']}")
        print(f"     Invalid:     {src['invalid']}")
        print(f"     Link broken: {src.get('link_broken', 0)}")
        print(f"     Duration:    {src['duration_sec']:.2f}s")
        if src["errors"]:
            print(f"     Errors:      {src['errors'][:2]}")

    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  ✅ Total saved:        {stats['total_saved']}")
    print(f"  ♻️  Total duplicates:   {stats['total_duplicates']}")
    print(f"  ❌ Invalid:             {stats['total_invalid']}")
    print(f"  🔗 Broken links:       {stats['total_link_broken']}")
    print(f"  🗄️  DB now has:         {stats['db_total']} scholarships")
    print("=" * 70 + "\n")

    logger.info(f"Run complete: {stats}")


if __name__ == "__main__":
    main()