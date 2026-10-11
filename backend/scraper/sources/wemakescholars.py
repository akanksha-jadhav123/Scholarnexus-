from scraper.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class WeMakeScholarsScraper(BaseScraper):
    """WeMakeScholars — scholarship and education loan portal."""

    def __init__(self):
        super().__init__(
            source_name="wemakescholars.com",
            base_url="https://www.wemakescholars.com/scholarship",
            delay=2
        )

    def parse(self, soup):
        results = []
        seen = set()

        cards = soup.select("div.scholarship-card, article, div.card, a[href*='/scholarship/']")

        for card in cards[:60]:
            try:
                name_el = card.select_one("h2, h3, h4, .title") or card
                if not name_el:
                    continue

                name = name_el.get_text(strip=True)
                if not name or len(name) < 10 or name in seen:
                    continue
                seen.add(name)

                link_el = card if card.name == "a" else card.select_one("a[href]")
                href = link_el["href"] if link_el else ""
                if href and not href.startswith("http"):
                    href = "https://www.wemakescholars.com" + href

                results.append({
                    "scholarship_name": name[:200],
                    "provider": "WeMakeScholars",
                    "source": "wemakescholars.com",
                    "source_type": "Aggregator",
                    "source_trust_score": 7,
                    "official_source": self.base_url,
                    "application_url": href or self.base_url,
                    "status": "Active"
                })
            except Exception:
                continue

        logger.info(f"[{self.source_name}] Found {len(results)} records")
        return results