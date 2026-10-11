from scraper.base_scraper import BaseScraper
import logging
logger = logging.getLogger(__name__)


class ScholarshipRoarScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            source_name="scholarshiproar.com",
            base_url="https://scholarshiproar.com/scholarships/",
            delay=2
        )

    def parse(self, soup):
        results, seen = [], set()
        for card in soup.select("article, div.post, div.card, li.post")[:80]:
            try:
                name_el = card.select_one("h2, h3, h4, .entry-title")
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)
                if not name or len(name) < 10 or name in seen:
                    continue
                seen.add(name)
                link_el = card.select_one("a[href]")
                href = link_el["href"] if link_el else self.base_url
                if href.startswith("/"):
                    href = "https://scholarshiproar.com" + href
                results.append({
                    "scholarship_name": name[:200],
                    "provider": "ScholarshipRoar",
                    "source": "scholarshiproar.com",
                    "source_type": "Aggregator",
                    "source_trust_score": 6,
                    "official_source": self.base_url,
                    "application_url": href,
                    "status": "Active"
                })
            except Exception:
                continue
        logger.info(f"[{self.source_name}] Found {len(results)}")
        return results