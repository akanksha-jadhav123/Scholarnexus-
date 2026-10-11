from scraper.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class IndiaScholarshipScraper(BaseScraper):
    """Scraper for indiascholarship.com."""

    def __init__(self):
        super().__init__(
            source_name="indiascholarship.com",
            base_url="https://www.indiascholarship.com/",
            delay=2
        )

    def parse(self, soup):
        results = []
        seen = set()

        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]

            if not text or len(text) < 12 or text in seen:
                continue
            if not any(k in text.lower() for k in
                       ["scholarship", "fellowship", "grant", "award"]):
                continue

            seen.add(text)

            if href.startswith("/"):
                href = "https://www.indiascholarship.com" + href
            elif not href.startswith("http"):
                continue

            results.append({
                "scholarship_name": text[:200],
                "provider": "IndiaScholarship",
                "source": "indiascholarship.com",
                "source_type": "Aggregator",
                "source_trust_score": 6,
                "official_source": self.base_url,
                "application_url": href,
                "status": "Active"
            })

            if len(results) >= 40:
                break

        logger.info(f"[{self.source_name}] Found {len(results)} records")
        return results