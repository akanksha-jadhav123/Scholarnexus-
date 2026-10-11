"""Scrape scholarship detail pages; expand roundup articles into individual awards."""
from scraper.base_scraper import BaseScraper
from scraper.amount_extractor import extract_amount_from_html, extract_currency_from_html, extract_currency_from_text, extract_awards_from_article, is_roundup_title
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class Scholars4DevScraper(BaseScraper):
    def __init__(self):
        super().__init__(source_name='scholars4dev.com', base_url='https://www.scholars4dev.com/category/scholarships/', delay=2)

    def parse(self, soup):
        results, seen = [], set()
        for a in soup.find_all('a', href=True):
            title = a.get_text(' ', strip=True)
            url = urljoin(self.base_url, a['href'])
            if not title or len(title) < 15 or title.lower() in seen:
                continue
            if not any(k in title.lower() for k in ['scholarship', 'fellowship', 'grant', 'award']):
                continue
            if not url.startswith('https://www.scholars4dev.com/category/scholarships/'):
                # Allow other article paths on this domain only.
                if not url.startswith('https://www.scholars4dev.com/'):
                    continue
            seen.add(title.lower())
            html = self.fetch(url)
            if not html:
                continue
            if is_roundup_title(title):
                # A guide contains multiple scholarships; extract each award section separately.
                for item in extract_awards_from_article(html, url, 'Scholars4Dev', self.source_name):
                    key = (item['scholarship_name'].lower(), item['application_url'])
                    if key not in seen and len(results) < 40:
                        results.append(item)
                        seen.add(key[0])
            else:
                amount = extract_amount_from_html(html)
                results.append({
                    'scholarship_name': title[:200], 'provider': 'Scholars4Dev',
                    'source': self.source_name, 'source_type': 'International', 'source_trust_score': 7,
                    'official_source': url, 'source_url': url, 'application_url': url,
                    'scholarship_amount': amount, 'amount_max': amount, 'scholarship_currency': extract_currency_from_html(html), 'status': 'Active'
                })
            if len(results) >= 40:
                break
        logger.info('[%s] Found %s award records', self.source_name, len(results))
        return results
