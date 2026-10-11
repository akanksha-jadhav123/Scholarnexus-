from scraper.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class UGCScraper(BaseScraper):
    """Scraper for UGC scholarship schemes."""

    def __init__(self):
        super().__init__(
            source_name="ugc.gov.in",
            base_url="https://www.ugc.gov.in/scholarship",
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
                       ["scholarship", "fellowship", "scheme"]):
                continue

            seen.add(text)

            if href.startswith("/"):
                href = "https://www.ugc.gov.in" + href
            elif not href.startswith("http"):
                continue

            results.append({
                "scholarship_name": text[:200],
                "provider": "UGC",
                "source": "ugc.gov.in",
                "source_type": "Government",
                "source_trust_score": 10,
                "official_source": self.base_url,
                "application_url": href,
                "status": "Active"
            })

            if len(results) >= 30:
                break

        logger.info(f"[{self.source_name}] Found {len(results)} records")
        return results