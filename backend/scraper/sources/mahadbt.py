from scraper.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class MahaDBTScraper(BaseScraper):
    """Scraper for mahadbt.maharashtra.gov.in — Maharashtra state scholarships."""

    def __init__(self):
        super().__init__(
            source_name="mahadbt.maharashtra.gov.in",
            base_url="https://mahadbt.maharashtra.gov.in/SchemeData/SchemeData?str=All_Scheme",
            delay=2
        )

    def parse(self, soup):
        results = []
        seen = set()

        # MahaDBT uses tables
        rows = soup.select("table tr, .scheme-row, .scheme-card")

        for row in rows[:80]:
            try:
                name_el = row.select_one("td:nth-child(1), td:nth-child(2), h3, h4")
                if not name_el:
                    continue

                name = name_el.get_text(strip=True)
                if not name or len(name) < 10 or name in seen:
                    continue
                if "sr" in name.lower() or "scheme name" in name.lower():
                    continue

                seen.add(name)

                link_el = row.select_one("a[href]")
                href = link_el["href"] if link_el else self.base_url
                if href.startswith("/"):
                    href = "https://mahadbt.maharashtra.gov.in" + href
                elif not href.startswith("http"):
                    href = self.base_url

                results.append({
                    "scholarship_name": name[:200],
                    "provider": "Government of Maharashtra",
                    "state": "Maharashtra",
                    "official_source": self.base_url,
                    "application_url": href,
                    "status": "Active"
                })
            except Exception:
                continue

        logger.info(f"[{self.source_name}] Found {len(results)} records")
        return results