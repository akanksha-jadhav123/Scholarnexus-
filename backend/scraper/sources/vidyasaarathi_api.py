from scraper.base_scraper import BaseScraper
import logging
import requests
logger = logging.getLogger(__name__)


class VidyasaarathiAPIScraper(BaseScraper):
    """Vidyasaarathi — tries JSON API."""

    def __init__(self):
        super().__init__(
            source_name="vidyasaarathi-api",
            base_url="https://www.vidyasaarathi.co.in",
            delay=1
        )

    def scrape(self):
        apis = [
            "https://www.vidyasaarathi.co.in/api/scholarships",
            "https://www.vidyasaarathi.co.in/Vidyasaarathi/api/scholarships",
        ]
        for url in apis:
            try:
                resp = requests.get(url, headers=self.headers, timeout=15, verify=False)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data if isinstance(data, list) else data.get("data", [])
                    results = []
                    for item in items[:50]:
                        name = item.get("name") or item.get("title")
                        if not name:
                            continue
                        results.append({
                            "scholarship_name": name[:200],
                            "provider": item.get("provider") or "Vidyasaarathi",
                            "scholarship_amount": item.get("amount"),
                            "application_deadline": item.get("deadline"),
                            "source": "vidyasaarathi.co.in",
                            "source_type": "Aggregator",
                            "source_trust_score": 8,
                            "official_source": self.base_url,
                            "application_url": item.get("url") or self.base_url,
                            "status": "Active"
                        })
                    if results:
                        logger.info(f"[{self.source_name}] JSON API {url} → {len(results)}")
                        return results
            except Exception as e:
                logger.debug(f"{url} failed: {e}")
        return []