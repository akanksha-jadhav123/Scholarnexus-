from scraper.base_scraper import BaseScraper
import logging
logger = logging.getLogger(__name__)


class Buddy4StudySitemapScraper(BaseScraper):
    """Scrapes Buddy4Study via sitemap (avoids JS)."""

    def __init__(self):
        super().__init__(
            source_name="buddy4study-sitemap",
            base_url="https://www.buddy4study.com/sitemap.xml",
            delay=1
        )

    def scrape(self):
        """Parse sitemap XML directly."""
        import requests
        try:
            resp = requests.get(self.base_url, headers=self.headers, timeout=15, verify=False)
            if resp.status_code != 200:
                return []

            import re
            # Extract scholarship URLs from sitemap
            urls = re.findall(r"<loc>([^<]+scholarship[^<]*)</loc>", resp.text, re.I)

            results = []
            seen = set()
            for url in urls[:50]:
                if url in seen:
                    continue
                seen.add(url)
                # Derive name from URL
                slug = url.rstrip("/").split("/")[-1]
                name = slug.replace("-", " ").title()
                if len(name) < 15:
                    continue
                results.append({
                    "scholarship_name": name[:200],
                    "provider": "Buddy4Study",
                    "source": "buddy4study.com",
                    "source_type": "Aggregator",
                    "source_trust_score": 7,
                    "official_source": "https://www.buddy4study.com",
                    "application_url": url,
                    "status": "Active"
                })

            logger.info(f"[{self.source_name}] Found {len(results)} from sitemap")
            return results
        except Exception as e:
            logger.error(f"[{self.source_name}] {e}")
            return []