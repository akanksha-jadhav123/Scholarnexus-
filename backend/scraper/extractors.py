"""
Extractors — parse raw HTML into structured scholarship data.
Complements the source-specific scrapers (used for one-off extractions).
"""
import re
from bs4 import BeautifulSoup


class ScholarshipExtractor:
    """Generic extractor for scholarship HTML blocks."""

    @staticmethod
    def extract_from_html(html):
        """Extract scholarship-like links from any HTML page."""
        soup = BeautifulSoup(html, "html.parser")
        results = []
        seen = set()

        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]

            if not text or len(text) < 12 or text in seen:
                continue
            if text.lower() in ["home", "about", "contact", "login", "register", "faq"]:
                continue
            if not any(k in text.lower() for k in
                       ["scholarship", "scheme", "fellowship", "grant", "award", "stipend"]):
                continue

            seen.add(text)
            results.append({
                "scholarship_name": text[:200],
                "application_url": href,
                "_raw_html": str(a.parent)[:500]
            })

        return results

    @staticmethod
    def extract_amount(text):
        """Extract ₹ amount from text. Handles: ₹1.5 crore, Rs 5 lakh, ₹50,000, 10k."""
        if not text:
            return None
        # Allow digits + commas + decimal points in the number part
        m = re.search(r"[₹Rs\.\s]*([\d,]+(?:\.\d+)?)\s*(lakh|crore|k)?", text, re.I)
        if not m:
            return None
        try:
            num = float(m.group(1).replace(",", ""))
        except ValueError:
            return None
        unit = (m.group(2) or "").lower()
        if unit == "lakh":
            num *= 100000
        elif unit == "crore":
            num *= 10000000
        elif unit == "k":
            num *= 1000
        return num

    @staticmethod
    def extract_deadline(text):
        """Extract a date from text."""
        if not text:
            return None
        patterns = [
            r"\d{1,2}[-/]\d{1,2}[-/]\d{4}",
            r"\d{1,2}\s+\w+\s+\d{4}",
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return m.group(0)
        return None