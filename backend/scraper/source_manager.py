"""
Central registry of all scholarship sources.
Add new sources here and they auto-run in the pipeline.
"""
from scraper.sources.scholarships_gov import ScholarshipsGovScraper
from scraper.sources.buddy4study import Buddy4StudyScraper
from scraper.sources.ngoscholarship import NGOScholarshipScraper
from scraper.sources.mahadbt import MahaDBTScraper
from scraper.sources.vidyasaarathi import VidyasaarathiScraper
from scraper.sources.wemakescholars import WeMakeScholarsScraper
from scraper.sources.scholarshipportal import ScholarshipPortalScraper
from scraper.sources.nsdl import NSDLScholarshipScraper
from scraper.sources.sitaram_jindal import SitaramJindalScraper
from scraper.sources.reliance_foundation import RelianceFoundationScraper


SOURCE_REGISTRY = [
    # National
    ScholarshipsGovScraper(),
    NSDLScholarshipScraper(),

    # State
    MahaDBTScraper(),

    # Aggregators
    Buddy4StudyScraper(),
    NGOScholarshipScraper(),
    VidyasaarathiScraper(),
    WeMakeScholarsScraper(),
    ScholarshipPortalScraper(),

    # NGO / Corporate
    SitaramJindalScraper(),
    RelianceFoundationScraper(),
]


def get_all_scrapers():
    return SOURCE_REGISTRY


def get_source_metadata():
    """Return metadata for each source — used by API."""
    return [
        {
            "name": s.source_name,
            "url": s.base_url,
            "delay_seconds": s.delay
        }
        for s in SOURCE_REGISTRY
    ]