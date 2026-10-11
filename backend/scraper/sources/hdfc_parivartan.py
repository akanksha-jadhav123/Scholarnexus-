from scraper.base_scraper import BaseScraper
import logging
logger = logging.getLogger(__name__)


class HDFCParivartanScraper(BaseScraper):
    """HDFC Bank Parivartan — educational support."""

    def __init__(self):
        super().__init__(
            source_name="hdfcbank.com",
            base_url="https://www.hdfcbank.com/personal/about-us/csr/parivartan",
            delay=2
        )

    def parse(self, soup):
        results, seen = [], set()
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            if not text or len(text) < 12 or text in seen:
                continue
            if not any(k in text.lower() for k in
                       ["scholarship", "education", "parivartan", "ecss", "program"]):
                continue
            seen.add(text)
            if href.startswith("/"):
                href = "https://www.hdfcbank.com" + href
            elif not href.startswith("http"):
                continue
            results.append({
                "scholarship_name": text[:200],
                "provider": "HDFC Bank Parivartan",
                "source": "hdfcbank.com",
                "source_type": "Corporate",
                "source_trust_score": 8,
                "official_source": self.base_url,
                "application_url": href,
                "status": "Active"
            })
            if len(results) >= 30:
                break
        logger.info(f"[{self.source_name}] Found {len(results)}")
        return results