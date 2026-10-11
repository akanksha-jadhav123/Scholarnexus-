from scraper.base_scraper import BaseScraper
import logging
logger = logging.getLogger(__name__)


class FFEScraper(BaseScraper):
    """Foundation for Excellence — professional course scholarships."""

    def __init__(self):
        super().__init__(
            source_name="ffe.org",
            base_url="https://ffe.org/scholarships/",
            delay=2
        )

    def parse(self, soup):
        results, seen = [], set()
        for card in soup.select("article, div.card, section, div.scholarship")[:60]:
            try:
                name_el = card.select_one("h1, h2, h3, h4, .title")
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)
                if not name or len(name) < 10 or name in seen:
                    continue
                if not any(k in name.lower() for k in
                           ["scholarship", "grant", "fellowship", "program"]):
                    continue
                seen.add(name)
                link_el = card.select_one("a[href]")
                href = link_el["href"] if link_el else self.base_url
                if href.startswith("/"):
                    href = "https://ffe.org" + href
                results.append({
                    "scholarship_name": name[:200],
                    "provider": "Foundation for Excellence",
                    "source": "ffe.org",
                    "source_type": "NGO",
                    "source_trust_score": 8,
                    "official_source": self.base_url,
                    "application_url": href,
                    "status": "Active"
                })
            except Exception:
                continue
        logger.info(f"[{self.source_name}] Found {len(results)}")
        return results