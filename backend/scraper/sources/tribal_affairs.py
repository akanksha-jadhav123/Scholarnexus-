from scraper.base_scraper import BaseScraper
import logging
logger = logging.getLogger(__name__)


class TribalAffairsScraper(BaseScraper):
    """Ministry of Tribal Affairs — ST scholarships."""

    def __init__(self):
        super().__init__(
            source_name="tribal.nic.in",
            base_url="https://tribal.nic.in/ScholarshiP.aspx",
            delay=2
        )

    def parse(self, soup):
        results, seen = [], set()

        # Tribal.nic.in uses tables
        rows = soup.select("table tr, li, div.scheme")
        for row in rows[:80]:
            try:
                a = row.select_one("a[href]")
                if not a:
                    continue
                text = a.get_text(strip=True)
                href = a["href"]
                if not text or len(text) < 10 or text in seen:
                    continue
                if not any(k in text.lower() for k in
                           ["scholarship", "scheme", "fellowship", "grant"]):
                    continue
                seen.add(text)
                if href.startswith("/"):
                    href = "https://tribal.nic.in" + href
                elif not href.startswith("http"):
                    continue
                results.append({
                    "scholarship_name": text[:200],
                    "provider": "Ministry of Tribal Affairs",
                    "category": "ST",
                    "source": "tribal.nic.in",
                    "source_type": "Government",
                    "source_trust_score": 10,
                    "official_source": self.base_url,
                    "application_url": href,
                    "status": "Active"
                })
            except Exception:
                continue
        logger.info(f"[{self.source_name}] Found {len(results)}")
        return results