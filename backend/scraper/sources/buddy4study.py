from scraper.base_scraper import BaseScraper
import logging
import requests

logger = logging.getLogger(__name__)


class Buddy4StudyScraper(BaseScraper):
    """Buddy4Study scraper — tries JSON APIs first."""

    def __init__(self):
        super().__init__(
            source_name="buddy4study.com",
            base_url="https://www.buddy4study.com/scholarships",
            delay=2
        )
        # Public API endpoints Buddy4Study's own frontend uses
        self.api_urls = [
            "https://www.buddy4study.com/api/scholarships?page=1&size=50",
            "https://www.buddy4study.com/api/v1/scholarships",
            "https://www.buddy4study.com/api/scholarships/listing",
        ]

    def scrape(self):
        # 1. Try JSON APIs
        for url in self.api_urls:
            try:
                resp = requests.get(url, headers=self.headers, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    records = self._parse_json(data)
                    if records:
                        logger.info(f"[{self.source_name}] JSON API {url} → {len(records)}")
                        return records
            except Exception as e:
                logger.debug(f"[{self.source_name}] API {url} failed: {e}")

        # 2. Fallback to HTML
        logger.info(f"[{self.source_name}] APIs failed, using HTML")
        return super().scrape()

    def _parse_json(self, data):
        records = []
        items = data if isinstance(data, list) else (
            data.get("data") or data.get("scholarships") or data.get("results") or []
        )
        for item in items[:50]:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("title") or item.get("scholarshipName")
            if not name:
                continue
            records.append({
                "scholarship_name": name,
                "provider": item.get("provider") or "Buddy4Study",
                "scholarship_amount": item.get("amount") or item.get("award"),
                "application_deadline": item.get("deadline") or item.get("lastDate"),
                "eligibility_description": item.get("description") or item.get("eligibility"),
                "official_source": self.base_url,
                "application_url": item.get("url") or item.get("link") or self.base_url,
                "status": "Active"
            })
        return records

    def parse(self, soup):
        # Keep HTML fallback
        results = []
        seen = set()
        for card in soup.select("a[href*='/scholarship/']")[:50]:
            name = card.get_text(strip=True)
            href = card.get("href", "")
            if not name or len(name) < 8 or name in seen:
                continue
            seen.add(name)
            if not href.startswith("http"):
                href = "https://www.buddy4study.com" + href
            results.append({
                "scholarship_name": name[:200],
                "provider": "Buddy4Study",
                "official_source": self.base_url,
                "application_url": href,
                "status": "Active"
            })
        return results