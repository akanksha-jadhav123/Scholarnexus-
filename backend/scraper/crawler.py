"""
Crawler — discovers scholarships from all registered sources in parallel.
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Government sources
from scraper.sources.scholarships_gov import ScholarshipsGovScraper
from scraper.sources.mahadbt import MahaDBTScraper
from scraper.sources.aicte import AICTEScraper
from scraper.sources.ugc import UGCScraper
from scraper.sources.moe import MinistryOfEducationScraper
from scraper.sources.social_justice import SocialJusticeScraper
from scraper.sources.tribal_affairs import TribalAffairsScraper
from scraper.sources.india_services import IndiaServicesScraper

# Private / Corporate / NGO sources
from scraper.sources.buddy4study import Buddy4StudyScraper
from scraper.sources.vidyasaarathi import VidyasaarathiScraper
from scraper.sources.ffe import FFEScraper
from scraper.sources.sitaram_jindal import SitaramJindalScraper
from scraper.sources.reliance_foundation import RelianceFoundationScraper
from scraper.sources.hdfc_parivartan import HDFCParivartanScraper
from scraper.sources.tata_trusts import TataTrustsScraper

from scraper.sources.scholarshipsads import ScholarshipsAdsScraper
from scraper.sources.scholarshiproar import ScholarshipRoarScraper
from scraper.sources.scholars4dev import Scholars4DevScraper
from scraper.sources.internationalscholarships import InternationalScholarshipsScraper
from scraper.sources.buddy4study_alt import Buddy4StudySitemapScraper
from scraper.sources.vidyasaarathi_api import VidyasaarathiAPIScraper

logger = logging.getLogger(__name__)

SCRAPER_CLASSES = [
    # Government
    ScholarshipsGovScraper,
    MahaDBTScraper,
    AICTEScraper,
    UGCScraper,
    MinistryOfEducationScraper,
    SocialJusticeScraper,
    TribalAffairsScraper,
    IndiaServicesScraper,

    # Private / Corporate
    Buddy4StudyScraper,
    VidyasaarathiScraper,
    FFEScraper,
    SitaramJindalScraper,
    RelianceFoundationScraper,
    HDFCParivartanScraper,
    TataTrustsScraper,

    # Aggregators (NEW)
    ScholarshipsAdsScraper,
    ScholarshipRoarScraper,
    Scholars4DevScraper,
    InternationalScholarshipsScraper,

    # Sitemap-based fallbacks (NEW)
    Buddy4StudySitemapScraper,
    VidyasaarathiAPIScraper,
]


class Crawler:
    """Parallel crawler — accepts max_workers."""

    def __init__(self, max_workers=5):
        self.max_workers = max_workers

    def _scrape_one(self, scraper_cls):
        try:
            scraper = scraper_cls()
            records = scraper.scrape()
            logger.info(f"[{scraper.source_name}] {len(records)} records")
            return (scraper.source_name, records, None)
        except Exception as e:
            name = getattr(scraper_cls, "__name__", str(scraper_cls))
            logger.error(f"[{name}] {e}")
            return (name, [], str(e))

    def crawl(self):
        all_records = []
        stats = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = [ex.submit(self._scrape_one, cls) for cls in SCRAPER_CLASSES]
            for future in as_completed(futures):
                source, records, error = future.result()
                stats.append({
                    "source": source,
                    "records": len(records),
                    "error": error
                })
                all_records.extend(records)

        logger.info(f"[Crawler] Total: {len(all_records)} from {len(SCRAPER_CLASSES)} sources")
        return all_records, stats


def crawl_all():
    return Crawler().crawl()