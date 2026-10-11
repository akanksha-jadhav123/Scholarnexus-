from scraper.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class AICTEScraper(BaseScraper):
    """Scraper for AICTE scholarship pages."""

    def __init__(self):
        super().__init__(
            source_name="aicte-india.org",
            base_url="https://www.aicte-india.org/schemes/students-development-schemes",
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
                       ["scholarship", "scheme", "pragati", "saksham"]):
                continue

            seen.add(text)

            if href.startswith("/"):
                href = "https://www.aicte-india.org" + href
            elif not href.startswith("http"):
                continue

            results.append({
                "scholarship_name": text[:200],
                "provider": "AICTE",
                "source": "aicte-india.org",
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