from scraper.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class RelianceFoundationScraper(BaseScraper):
    """Reliance Foundation Scholarships."""

    def __init__(self):
        super().__init__(
            source_name="reliancefoundation.org",
            base_url="https://www.reliancefoundation.org/",
            delay=2
        )

    def parse(self, soup):
        results = []
        seen = set()

        for card in soup.select("div, article, section")[:60]:
            try:
                name_el = card.select_one("h2, h3, h4, .title")
                if not name_el:
                    continue

                name = name_el.get_text(strip=True)
                if not name or len(name) < 10 or name in seen:
                    continue
                if not any(k in name.lower() for k in ["scholarship", "fellowship", "undergraduate", "postgraduate"]):
                    continue

                seen.add(name)

                link_el = card.select_one("a[href]")
                href = link_el["href"] if link_el else self.base_url
                if href.startswith("/"):
                    href = "https://www.reliancefoundation.org" + href
                elif not href.startswith("http"):
                    href = self.base_url

                results.append({
                    "scholarship_name": name[:200],
                    "provider": "Reliance Foundation",
                    "source": "reliancefoundation.org",
                    "source_type": "Corporate",
                    "source_trust_score": 9,
                    "official_source": self.base_url,
                    "application_url": href,
                    "status": "Active"
                })
            except Exception:
                continue

        logger.info(f"[{self.source_name}] Found {len(results)} records")
        return results