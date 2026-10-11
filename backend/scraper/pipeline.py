"""
Orchestrates: scrape → normalize → validate link → dedupe → save.
"""
import logging
from datetime import datetime
from scraper.normalizer import Normalizer
from scraper.deduplicator import Deduplicator
from scraper.link_validator import LinkValidator

logger = logging.getLogger(__name__)


class ScraperPipeline:

    def __init__(self, db, scrapers=None, validate_links=True):
        self.db = db
        self.scrapers = scrapers or []
        self.validate_links = validate_links
        self.validator = LinkValidator() if validate_links else None

    def run(self):
        stats = {
            "started_at": datetime.utcnow().isoformat(),
            "sources": [],
            "total_scraped": 0,
            "total_saved": 0,
            "total_duplicates": 0,
            "total_invalid": 0,
            "total_link_broken": 0
        }

        for scraper in self.scrapers:
            source_stat = self._run_one(scraper)
            stats["sources"].append(source_stat)
            stats["total_scraped"] += source_stat["scraped"]
            stats["total_saved"] += source_stat["saved"]
            stats["total_duplicates"] += source_stat["duplicates"]
            stats["total_invalid"] += source_stat["invalid"]
            stats["total_link_broken"] += source_stat.get("link_broken", 0)

        stats["ended_at"] = datetime.utcnow().isoformat()
        stats["db_total"] = self.db.Scholarships.count_documents({})
        logger.info(f"[Pipeline] {stats}")
        return stats

    def _run_one(self, scraper):
        stat = {
            "source": scraper.source_name,
            "scraped": 0,
            "saved": 0,
            "duplicates": 0,
            "invalid": 0,
            "link_broken": 0,
            "errors": [],
            "duration_sec": 0
        }
        started = datetime.utcnow()

        try:
            raw = scraper.scrape()
            stat["scraped"] = len(raw)

            for r in raw:
                try:
                    # Add source tracking fields
                    r.setdefault("source", scraper.source_name)
                    r.setdefault("source_url", scraper.base_url)

                    norm = Normalizer.normalize(r)

                    # Validation
                    if not norm["scholarship_name"] or len(norm["scholarship_name"]) < 5:
                        stat["invalid"] += 1
                        continue
                    if not norm["application_url"]:
                        stat["invalid"] += 1
                        continue

                    # Dedup
                    if Deduplicator.is_duplicate(self.db, norm):
                        stat["duplicates"] += 1
                        continue

                    # Link validation
                    if self.validator:
                        v = self.validator.validate(norm["application_url"])
                        norm["link_status"] = v["status"]
                        norm["link_http_code"] = v["http_code"]
                        norm["last_verified"] = datetime.utcnow().isoformat()

                        if v["status"] == "broken":
                            stat["link_broken"] += 1
                            # Still save — but mark as broken
                            # (admin can fix later)
                        elif v["status"] == "pending":
                            stat["link_broken"] += 1
                    else:
                        norm["link_status"] = "pending"

                    # Save
                    self.db.Scholarships.insert_one(norm)
                    stat["saved"] += 1

                except Exception as e:
                    stat["invalid"] += 1
                    stat["errors"].append(str(e)[:100])

        except Exception as e:
            logger.error(f"[{scraper.source_name}] Fatal: {e}")
            stat["errors"].append(str(e)[:200])

        stat["duration_sec"] = (datetime.utcnow() - started).total_seconds()
        logger.info(f"[{scraper.source_name}] {stat}")
        return stat