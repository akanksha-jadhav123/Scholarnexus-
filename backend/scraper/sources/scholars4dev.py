from scraper.base_scraper import BaseScraper
import logging
logger = logging.getLogger(__name__)


class Scholars4DevScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            source_name="scholars4dev.com",
            base_url="https://www.scholars4dev.com/category/scholarships/",
            delay=2
        )

    def parse(self, soup):
        results, seen = [], set()
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            if not text or len(text) < 15 or text in seen:
                continue
            if not any(k in text.lower() for k in ["scholarship", "fellowship", "grant", "award"]):
                continue
            seen.add(text)
            if href.startswith("/"):
                href = "https://www.scholars4dev.com" + href
            elif not href.startswith("http"):
                continue
            results.append({
                "scholarship_name": text[:200],
                "provider": "Scholars4Dev",
                "source": "scholars4dev.com",
                "source_type": "International",
                "source_trust_score": 7,
                "official_source": self.base_url,
                "application_url": href,
                "status": "Active"
            })
            if len(results) >= 40:
                break
        logger.info(f"[{self.source_name}] Found {len(results)}")
        return results