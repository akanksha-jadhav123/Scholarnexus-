"""
Background scheduler — runs scraper every N hours.
Run as a separate process: python scripts/scheduler_daemon.py

Stops with Ctrl+C.
"""
import os
import sys
import time
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from scraper.pipeline import ScraperPipeline
from scraper.source_manager import get_all_scrapers

INTERVAL_HOURS = 24

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "scheduler.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_once():
    logger.info("=" * 60)
    logger.info(f"Scheduler tick at {datetime.utcnow().isoformat()}")
    logger.info("=" * 60)

    try:
        scrapers = get_all_scrapers()
        pipeline = ScraperPipeline(db=db, scrapers=scrapers, validate_links=True)
        stats = pipeline.run()
        logger.info(f"Scrape complete: saved={stats['total_saved']}, "
                    f"dupes={stats['total_duplicates']}, db_total={stats['db_total']}")
    except Exception as e:
        logger.error(f"Scheduler run failed: {e}")


def main():
    logger.info(f"ScholarNexus Scheduler starting (interval = {INTERVAL_HOURS}h)")

    # Run once on startup
    run_once()

    while True:
        logger.info(f"Sleeping for {INTERVAL_HOURS} hours...")
        try:
            time.sleep(INTERVAL_HOURS * 3600)
            run_once()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break


if __name__ == "__main__":
    main()