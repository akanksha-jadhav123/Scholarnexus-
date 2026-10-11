from scraper.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class NSDLScholarshipScraper(BaseScraper):
    """NSDL e-Governance scholarship listings."""

    def __init__(self):
        super().__init__(
            source_name="nsdl.co.in",
            base_url="https://www.nsdl.co.in/scholarships.php",
            delay=2
        )

    def parse(self, soup):
        results = []
        seen = set()

        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]

            if not text or len(text) < 15 or text in seen:
                continue
            if not any(k in text.lower() for k in
                       ["scholarship", "fellowship", "award", "scheme"]):
                continue

            seen.add(text)

            if href.startswith("/"):
                href = "https://www.nsdl.co.in" + href
            elif not href.startswith("http"):
                continue

            results.append({
                "scholarship_name": text[:200],
                "provider": "NSDL",
                "source": "nsdl.co.in",
                "source_type": "Government",
                "source_trust_score": 9,
                "official_source": self.base_url,
                "application_url": href,
                "status": "Active"
            })

            if len(results) >= 30:
                break

        logger.info(f"[{self.source_name}] Found {len(results)} records")
        return results