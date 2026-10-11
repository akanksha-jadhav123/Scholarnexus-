from scraper.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class SitaramJindalScraper(BaseScraper):
    """Sitaram Jindal Foundation — NGO scholarships."""

    def __init__(self):
        super().__init__(
            source_name="sitaramjindalfoundation.org",
            base_url="https://www.sitaramjindalfoundation.org/",
            delay=2
        )

    def parse(self, soup):
        results = []
        seen = set()

        for card in soup.select("div, article, li, tr")[:80]:
            try:
                name_el = card.select_one("h2, h3, h4, .title, strong")
                if not name_el:
                    continue

                name = name_el.get_text(strip=True)
                if not name or len(name) < 10 or name in seen:
                    continue
                if not any(k in name.lower() for k in ["scholarship", "scheme", "grant"]):
                    continue

                seen.add(name)

                link_el = card.select_one("a[href]")
                href = link_el["href"] if link_el else self.base_url
                if href.startswith("/"):
                    href = "https://www.sitaramjindalfoundation.org" + href
                elif not href.startswith("http"):
                    href = self.base_url

                results.append({
                    "scholarship_name": name[:200],
                    "provider": "Sitaram Jindal Foundation",
                    "source": "sitaramjindalfoundation.org",
                    "source_type": "NGO",
                    "source_trust_score": 8,
                    "official_source": self.base_url,
                    "application_url": href,
                    "status": "Active"
                })
            except Exception:
                continue

        logger.info(f"[{self.source_name}] Found {len(results)} records")
        return results