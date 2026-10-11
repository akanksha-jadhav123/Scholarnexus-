from scraper.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class ScholarshipPortalScraper(BaseScraper):
    """ScholarshipPortal.com — international + India scholarships."""

    def __init__(self):
        super().__init__(
            source_name="scholarshipportal.com",
            base_url="https://www.scholarshipportal.com/scholarships/india",
            delay=2
        )

    def parse(self, soup):
        results = []
        seen = set()

        for card in soup.select("div.scholarship, article, div.card, li.scholarship")[:60]:
            try:
                name_el = card.select_one("h2, h3, h4, .title, .scholarship-title")
                if not name_el:
                    continue

                name = name_el.get_text(strip=True)
                if not name or len(name) < 8 or name in seen:
                    continue
                seen.add(name)

                link_el = card.select_one("a[href]")
                href = link_el["href"] if link_el else ""
                if href and not href.startswith("http"):
                    href = "https://www.scholarshipportal.com" + href

                deadline_el = card.select_one(".deadline, time, .date")
                deadline = deadline_el.get_text(strip=True) if deadline_el else None

                results.append({
                    "scholarship_name": name[:200],
                    "provider": "ScholarshipPortal",
                    "source": "scholarshipportal.com",
                    "source_type": "International",
                    "source_trust_score": 7,
                    "application_deadline": deadline,
                    "official_source": self.base_url,
                    "application_url": href or self.base_url,
                    "status": "Active"
                })
            except Exception:
                continue

        logger.info(f"[{self.source_name}] Found {len(results)} records")
        return results