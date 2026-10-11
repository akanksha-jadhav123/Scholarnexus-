from scraper.base_scraper import BaseScraper
import logging
logger = logging.getLogger(__name__)


class MinistryOfEducationScraper(BaseScraper):
    """Ministry of Education — scholarships & education loans page."""

    def __init__(self):
        super().__init__(
            source_name="education.gov.in",
            base_url="https://www.education.gov.in/scholarships-education-loan-0",
            delay=2
        )

    def parse(self, soup):
        results, seen = [], set()
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            if not text or len(text) < 12 or text in seen:
                continue
            if text.lower() in ["home", "about", "contact", "login"]:
                continue
            if not any(k in text.lower() for k in
                       ["scholarship", "scheme", "fellowship", "loan", "grant"]):
                continue
            seen.add(text)
            if href.startswith("/"):
                href = "https://www.education.gov.in" + href
            elif not href.startswith("http"):
                continue
            results.append({
                "scholarship_name": text[:200],
                "provider": "Ministry of Education",
                "source": "education.gov.in",
                "source_type": "Government",
                "source_trust_score": 10,
                "official_source": self.base_url,
                "application_url": href,
                "status": "Active"
            })
            if len(results) >= 40:
                break
        logger.info(f"[{self.source_name}] Found {len(results)}")
        return results