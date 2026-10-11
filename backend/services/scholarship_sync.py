"""
Coordinates the full scraping pipeline:
Crawl → Normalize → Validate → Dedupe → Save
"""
import logging
from datetime import datetime
from scraper.crawler import Crawler
from scraper.normalizer import Normalizer
from scraper.validator import Validator
from scraper.deduplicator import Deduplicator

logger = logging.getLogger(__name__)


class ScholarshipSync:
    def __init__(self, db):
        self.db = db

    def run(self):
        stats = {
            "started_at": datetime.utcnow().isoformat(),
            "crawled": 0,
            "validated": 0,
            "duplicates": 0,
            "rejected": 0,
            "saved": 0,
            "sources": [],
            "errors": []
        }

        try:
            crawler = Crawler(max_workers=5)
            result = crawler.crawl()

            # Handle both tuple return and list return
            if isinstance(result, tuple):
                raw_records, source_stats = result
            else:
                raw_records = result
                source_stats = []

            stats["crawled"] = len(raw_records)
            stats["sources"] = source_stats
            logger.info(f"[Sync] Crawled {len(raw_records)} records")

        except Exception as e:
            logger.error(f"[Sync] Fatal: {e}")
            stats["errors"].append(str(e))
            return stats

        for raw in raw_records:
            try:
                norm = Normalizer.normalize(raw)

                is_valid, errors = Validator.validate(norm)
                if not is_valid:
                    stats["rejected"] += 1
                    continue
                stats["validated"] += 1

                if Deduplicator.is_duplicate(self.db, norm):
                    stats["duplicates"] += 1
                    continue

                self.db.Scholarships.insert_one(norm)
                stats["saved"] += 1

            except Exception as e:
                stats["errors"].append(str(e)[:200])

        stats["ended_at"] = datetime.utcnow().isoformat()
        stats["db_total"] = self.db.Scholarships.count_documents({})
        logger.info(f"[Sync] Done: saved={stats['saved']}, db_total={stats['db_total']}")
        return stats