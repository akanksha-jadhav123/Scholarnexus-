"""Context-aware scholarship amount extraction. Never treats arbitrary page numbers as awards."""
import re
from bs4 import BeautifulSoup

CURRENCY = r"(?:₹|INR|Rs\.?|\$|US\$|USD|£|GBP|€|EUR|CAD\$|C\$|AUD\$|A\$)"
NUMBER = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"
UNIT = r"(?:\s*(?:thousand|k|lakh|lac|million|mn|crore|cr))?"
AMOUNT_RE = re.compile(rf"(?P<currency>{CURRENCY})\s*(?P<num>{NUMBER}){UNIT}|(?P<num2>{NUMBER})\s*(?P<unit2>thousand|k|lakh|lac|million|mn|crore|cr)\b", re.I)
LABEL_RE = re.compile(r"\b(amount|award(?:\s+amount)?|scholarship\s+(?:value|amount|worth)|value\s+of\s+(?:the\s+)?award|funding\s+amount|stipend|worth|valued\s+at)\b", re.I)
ROUNDUP_RE = re.compile(r"\b(top\s+\d+|\d+\+?\s+scholarships?|scholarships?\s+in\s+.+\s+for\s+.+|fully\s+funded\s+scholarships?)\b", re.I)


def _to_number(match):
    if match.group('num'):
        raw = match.group('num').replace(',', '')
        unit_text = match.group(0).lower()
        n = float(raw)
    else:
        n = float(match.group('num2').replace(',', ''))
        unit_text = (match.group('unit2') or '').lower()
    multiplier = 1
    if 'lakh' in unit_text or 'lac' in unit_text:
        multiplier = 100000
    elif 'crore' in unit_text or re.search(r'\bcr\b', unit_text):
        multiplier = 10000000
    elif 'million' in unit_text or re.search(r'\bmn\b', unit_text):
        multiplier = 1000000
    elif re.search(r'\b(?:thousand|k)\b', unit_text):
        multiplier = 1000
    value = n * multiplier
    # Reject tiny incidental numbers and implausible extraction artefacts.
    if value < 100 or value > 1_000_000_000:
        return None
    return int(value) if value.is_integer() else value


def extract_amount_from_text(text):
    """Only return a value if it is near an explicit award/amount label."""
    if not text:
        return None
    text = re.sub(r"\s+", " ", str(text)).strip()
    for label in LABEL_RE.finditer(text):
        window = text[label.end():label.end() + 180]
        # Avoid pulling a number from a later unrelated section.
        window = re.split(r"(?:deadline|eligibility|application process|how to apply|location)\s*[:\-]", window, flags=re.I)[0]
        m = AMOUNT_RE.search(window)
        if m:
            value = _to_number(m)
            if value is not None:
                return value
    return None


def extract_amount_from_html(html):
    """Extract a single clearly labelled award value; return None for roundup pages."""
    if not html:
        return None
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.get_text(' ', strip=True) if soup.title else ''
    # A roundup may contain many unrelated awards, so it has no single amount.
    if ROUNDUP_RE.search(title):
        return None

    # Structured data is preferred when the property explicitly describes an award.
    import json
    for node in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(node.string or node.get_text())
        except Exception:
            continue
        stack = data if isinstance(data, list) else [data]
        while stack:
            obj = stack.pop()
            if isinstance(obj, list):
                stack.extend(obj)
            elif isinstance(obj, dict):
                for key in ('award', 'amount', 'scholarshipAmount', 'awardAmount', 'value'):
                    val = obj.get(key)
                    if isinstance(val, (int, float)) and 100 <= val <= 1_000_000_000:
                        return int(val)
                    if isinstance(val, str):
                        found = extract_amount_from_text('Amount: ' + val)
                        if found:
                            return found
                stack.extend(v for v in obj.values() if isinstance(v, (dict, list)))

    # Inspect explicit label/value structures first.
    for row in soup.find_all(['tr', 'li', 'p', 'div', 'dt', 'dd']):
        text = row.get_text(' ', strip=True)
        if not text or len(text) > 700 or not LABEL_RE.search(text):
            continue
        value = extract_amount_from_text(text)
        if value:
            return value

    # Also support a bold label followed by a value in a neighbouring element.
    for label in soup.find_all(['strong', 'b', 'dt', 'th']):
        label_text = label.get_text(' ', strip=True)
        if LABEL_RE.search(label_text):
            candidate = ' '.join([
                label_text,
                label.find_next_sibling().get_text(' ', strip=True) if label.find_next_sibling() else '',
                label.parent.get_text(' ', strip=True) if label.parent else '',
            ])
            value = extract_amount_from_text(candidate)
            if value:
                return value
    return None


def is_roundup_title(title):
    return bool(ROUNDUP_RE.search(title or ''))


def extract_awards_from_article(html, article_url, provider, source_name, source_type='International'):
    """Split a roundup article into individual heading sections and extract each section's own award.

    This is intentionally conservative: sections without a meaningful heading are ignored, and an
    amount is only stored when an explicit amount/award label is present in that section.
    """
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('article') or soup.find('main') or soup.body or soup
    headings = content.find_all(['h2', 'h3', 'h4'])
    items = []
    seen = set()
    for heading in headings:
        title = heading.get_text(' ', strip=True)
        if not title or len(title) < 8 or title.lower() in seen:
            continue
        if re.search(r'^(related|more|comments|leave a reply|table of contents|frequently asked questions|faqs?)\b', title, re.I):
            continue
        section_bits = []
        link_url = None
        node = heading.find_next_sibling()
        while node and node.name not in ('h1', 'h2', 'h3', 'h4'):
            section_bits.append(node.get_text(' ', strip=True))
            if link_url is None:
                a = node.find('a', href=True)
                if a:
                    link_url = a['href']
            node = node.find_next_sibling()
        section_text = ' '.join(section_bits)
        # Only headings that plausibly identify an award are retained.
        if not re.search(r'\b(scholarship|fellowship|grant|award|funding|bursary)\b', title, re.I):
            continue
        amount = extract_amount_from_text(section_text)
        if link_url and link_url.startswith('/'):
            from urllib.parse import urljoin
            link_url = urljoin(article_url, link_url)
        if not link_url or not link_url.startswith('http'):
            link_url = article_url
        seen.add(title.lower())
        items.append({
            'scholarship_name': title[:200], 'provider': provider, 'source': source_name,
            'source_type': source_type, 'source_trust_score': 7,
            'official_source': article_url, 'source_url': article_url,
            'application_url': link_url, 'scholarship_amount': amount,
            'amount_max': amount, 'scholarship_currency': extract_currency_from_text(section_text), 'status': 'Active'
        })
    return items


def extract_currency_from_text(text):
    """Return a currency code only when a currency marker is explicitly present."""
    if not text:
        return None
    # Prefer explicit country/currency codes before symbols.
    patterns = [
        (r'\b(?:US\$|USD)\b|US\$', 'USD'),
        (r'\b(?:INR|Rs\.?)\b|₹', 'INR'),
        (r'\b(?:CAD|C\$)\b', 'CAD'),
        (r'\b(?:AUD|A\$)\b', 'AUD'),
        (r'\b(?:GBP)\b|£', 'GBP'),
        (r'\b(?:EUR)\b|€', 'EUR'),
        (r'\b(?:CHF)\b', 'CHF'),
    ]
    for pattern, code in patterns:
        if re.search(pattern, text, re.I):
            return code
    return None


def extract_currency_from_html(html):
    if not html:
        return None
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.get_text(' ', strip=True) if soup.title else ''
    if ROUNDUP_RE.search(title):
        return None
    for row in soup.find_all(['tr', 'li', 'p', 'div', 'dt', 'dd']):
        text = row.get_text(' ', strip=True)
        if text and len(text) <= 700 and LABEL_RE.search(text) and AMOUNT_RE.search(text):
            currency = extract_currency_from_text(text)
            if currency:
                return currency
    return None
