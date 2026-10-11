"""
Base scraper class — provides:
- Polite HTTP fetching with delay
- Retry logic
- User-agent identification
- HTML parsing entry point
"""
import time
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper:
    """All source scrapers inherit from this."""

    def __init__(self, source_name, base_url, delay=2, max_retries=2):
        self.source_name = source_name
        self.base_url = base_url
        self.delay = delay
        self.max_retries = max_retries
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }

    def fetch(self, url):
        """Fetch URL with retry + polite delay. Returns HTML or None."""
        for attempt in range(1, self.max_retries + 1):
            try:
                time.sleep(self.delay)
                resp = requests.get(url, headers=self.headers, timeout=15)
                resp.raise_for_status()
                logger.info(f"[{self.source_name}] Fetched {url} (attempt {attempt})")
                return resp.text
            except requests.exceptions.RequestException as e:
                logger.warning(f"[{self.source_name}] Attempt {attempt} failed: {e}")
                if attempt == self.max_retries:
                    logger.error(f"[{self.source_name}] Giving up on {url}")
                    return None
                time.sleep(self.delay * attempt)
        return None

    def soup(self, html):
        return BeautifulSoup(html, "html.parser")

    def parse(self, soup):
        """Override in subclass. Return list of raw dicts."""
        raise NotImplementedError

    def scrape(self):
        """Main entry — fetch base URL and parse."""
        html = self.fetch(self.base_url)
        if not html:
            return []
        return self.parse(self.soup(html))