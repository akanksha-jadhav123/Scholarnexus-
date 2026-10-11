"""
Scraper for scholarships.gov.in (National Scholarship Portal).

Uses the public JSON endpoints used by the site itself.
Falls back to HTML scraping if the API changes.
"""
from scraper.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class ScholarshipsGovScraper(BaseScraper):

    def __init__(self):
        super().__init__(
            source_name="scholarships.gov.in",
            base_url="https://scholarships.gov.in",
            delay=1
        )
        # Public JSON endpoints (used by NSP's own frontend)
        self.api_endpoints = [
            "https://scholarships.gov.in/public/scheme/all",
            "https://scholarships.gov.in/public/scheme/list",
            "https://scholarships.gov.in/api/schemes",
        ]

    def scrape(self):
        """Try JSON APIs first, fall back to HTML."""
        # 1. Try JSON APIs
        for url in self.api_endpoints:
            try:
                import requests
                resp = requests.get(url, headers=self.headers, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    records = self._parse_json(data)
                    if records:
                        logger.info(f"[{self.source_name}] JSON API {url} → {len(records)} records")
                        return records
            except Exception as e:
                logger.debug(f"[{self.source_name}] API {url} failed: {e}")

        # 2. Fallback: HTML scraping
        logger.info(f"[{self.source_name}] JSON APIs failed, using HTML fallback")
        return super().scrape()

    def _parse_json(self, data):
        """Handle various JSON shapes."""
        records = []
        items = []

        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for key in ["data", "schemes", "results", "content", "list"]:
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    break

        for item in items[:100]:
            if not isinstance(item, dict):
                continue
            name = item.get("schemeName") or item.get("name") or item.get("title")
            if not name:
                continue

            records.append({
                "scholarship_name": name,
                "provider": item.get("provider") or "Government of India",
                "eligibility_description": item.get("description") or item.get("eligibility") or "",
                "application_deadline": item.get("lastDate") or item.get("deadline"),
                "scholarship_amount": item.get("amount") or item.get("scholarshipAmount"),
                "category": item.get("category") or "All",
                "course": item.get("course") or "All",
                "official_source": self.base_url,
                "application_url": item.get("url") or item.get("applyLink") or self.base_url,
                "status": "Active"
            })

        return records

    def parse(self, soup):
        """Fallback HTML parser — improved selectors."""
        results = []

        # Try many selectors (site structure changes often)
        selectors = [
            "div.scheme-card", "div.scheme-item", "div.card-body",
            "li.scheme", "article", "div.service-item",
            "a[href*='scheme']", "a[href*='scholarship']"
        ]

        seen_names = set()

        for sel in selectors:
            for card in soup.select(sel)[:80]:
                try:
                    if card.name == "a":
                        name = card.get_text(strip=True)
                        href = card.get("href", "")
                        desc = ""
                    else:
                        name_el = card.select_one("h1, h2, h3, h4, h5, .title, .heading")
                        if not name_el:
                            continue
                        name = name_el.get_text(strip=True)
                        link = card.select_one("a[href]")
                        href = link["href"] if link else ""
                        desc_el = card.select_one("p, .desc, .description")
                        desc = desc_el.get_text(strip=True) if desc_el else ""

                    if not name or len(name) < 8 or name in seen_names:
                        continue
                    # Filter out generic nav links
                    if name.lower() in ["home", "about", "contact", "login", "register", "faq"]:
                        continue
                    if not any(k in name.lower() for k in
                               ["scholarship", "scheme", "fellowship", "grant", "award", "stipend"]):
                        continue

                    seen_names.add(name)

                    if href.startswith("/"):
                        href = self.base_url + href
                    elif not href.startswith("http"):
                        href = self.base_url

                    results.append({
                        "scholarship_name": name[:200],
                        "provider": "Government of India",
                        "eligibility_description": desc[:300],
                        "official_source": self.base_url,
                        "application_url": href,
                        "status": "Active"
                    })

                    if len(results) >= 40:
                        break
                except Exception:
                    continue

        logger.info(f"[{self.source_name}] HTML fallback → {len(results)} records")
        return results