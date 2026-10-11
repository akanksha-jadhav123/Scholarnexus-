import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from database import get_scholarship_collection
from datetime import datetime
import hashlib
import time
import re


BASE_URL = "https://www.buddy4study.com"
LIST_URL = "https://www.buddy4study.com/scholarships"

SKIP_KEYWORDS = [
    "education loan", "loan programme", "loan program",
    "psychometric test", "stream selector",
]


def make_id(name, url):
    return hashlib.md5(f"{name}|{url}".encode()).hexdigest()[:12]


def clean(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def should_skip(title):
    t = title.lower()
    return any(k in t for k in SKIP_KEYWORDS)


def get_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)


def find_card_for_title(title_tag):
    """
    Walk up from the title until we find an ancestor that contains
    'awardCont' blocks (the amount/eligibility container), but does NOT
    contain any OTHER scholarshipName (which would mean we went too far up).
    """
    node = title_tag
    for _ in range(10):
        parent = node.parent
        if not parent:
            return None

        # Count OTHER scholarshipName elements inside this parent
        all_titles = parent.find_all("h4", class_=re.compile(r"scholarshipName"))
        # If this parent has exactly 1 title (this one), it's likely our card
        if len(all_titles) == 1:
            # And it should contain the awardCont structure
            if parent.find("div", class_=re.compile(r"awardCont")):
                return parent

        # If parent has many titles → we've gone too far up. Return previous.
        if len(all_titles) > 1:
            return node

        node = parent

    return None


def parse_card(card, title_tag):
    a_tag = card.find("a", href=re.compile(r"/scholarship/"))
    if not a_tag:
        # Try the title tag's nearest ancestor with a link
        for p in title_tag.parents:
            a_tag = p.find("a", href=re.compile(r"/scholarship/"))
            if a_tag:
                break
    if not a_tag:
        return None

    href = a_tag.get("href", "")
    full_url = href if href.startswith("http") else BASE_URL + href

    title = clean(title_tag.get_text())
    if not title or len(title) < 3:
        return None
    if should_skip(title):
        return None

    amount = "N/A"
    eligibility = "N/A"
    for block in card.find_all("div", class_=re.compile(r"awardCont")):
        h = block.find(["h4", "h5", "h3"])
        p = block.find("p")
        if not h or not p:
            continue
        label = clean(h.get_text()).lower()
        value = clean(p.get_text())
        if "award" in label and amount == "N/A":
            amount = value
        elif "eligibility" in label and eligibility == "N/A":
            eligibility = value

    # Deadline
    deadline = "N/A"
    card_text = clean(card.get_text(" "))
    m = re.search(r"Deadline[^\d]*(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})", card_text)
    if not m:
        m = re.search(r"\b(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})\b", card_text)

    if m:
        raw_date = m.group(1) if m.groups() else m.group(0)
        for fmt in ("%d %B %Y", "%d %b %Y", "%d-%m-%Y"):
            try:
                dt = datetime.strptime(raw_date, fmt)
                deadline = dt.strftime("%Y-%m-%d")
                break
            except Exception:
                continue
        if deadline == "N/A":
            deadline = raw_date

    return {
        "scholarship_id": make_id(title, full_url),
        "scholarship_name": title[:200],
        "provider": "Buddy4Study",
        "scholarship_amount": amount[:150],
        "course": "All",
        "state": "All India",
        "category": "All",
        "gender": "All",
        "application_deadline": deadline,
        "minimum_percentage": 0,
        "max_income": 0,
        "eligibility": eligibility[:400],
        "apply_link": full_url,
        "source_website": "buddy4study.com",
        "scraped_at": datetime.now()
    }


def scrape_list():
    collection = get_scholarship_collection()
    driver = get_driver()

    try:
        print(f"🌐 Opening: {LIST_URL}")
        driver.get(LIST_URL)
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[class*='scholarshipName']")
            )
        )
        time.sleep(3)

        print("📜 Scrolling...")
        last = 0
        for i in range(20):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            cur = len(driver.find_elements(By.CSS_SELECTOR, "[class*='scholarshipName']"))
            if cur == last and i > 3:
                break
            last = cur
        print(f"   Total titles: {last}")

        html = driver.page_source
        print(f"✅ Got HTML ({len(html)} chars)\n")

    finally:
        driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    title_tags = soup.find_all("h4", class_=re.compile(r"scholarshipName"))
    print(f"🔍 Found {len(title_tags)} title tags\n")

    saved = 0
    skipped = 0
    seen_ids = set()

    for title_tag in title_tags:
        card = find_card_for_title(title_tag)
        if not card:
            print(f"  ⚠️  No card found for: {clean(title_tag.get_text())[:60]}")
            skipped += 1
            continue

        doc = parse_card(card, title_tag)
        if not doc:
            skipped += 1
            continue

        if doc["scholarship_id"] in seen_ids:
            continue
        seen_ids.add(doc["scholarship_id"])

        collection.update_one(
            {"scholarship_id": doc["scholarship_id"]},
            {"$set": doc},
            upsert=True
        )
        saved += 1
        print(f"  💾 {doc['scholarship_name'][:60]}")
        print(f"      💰 {doc['scholarship_amount']}")
        print(f"      📅 {doc['application_deadline']}")

    print(f"\n🎉 Saved: {saved}  |  Skipped: {skipped}")
    print(f"📊 Total in DB: {collection.count_documents({})}")


if __name__ == "__main__":
    import sys
    if "--no-prompt" in sys.argv:
        print("🤖 Running in scheduled mode (no prompt)")
    else:
        confirm = input("Clear existing BUDDY4STUDY entries first? (y/n): ").strip().lower()
        if confirm == "y":
            from database import get_scholarship_collection as gsc
            # Only delete Buddy4Study source — keep Maharashtra/NSP/AICTE safe!
            deleted = gsc().delete_many({"source_website": "buddy4study.com"})
            print(f"🗑️  Deleted {deleted.deleted_count} old Buddy4Study documents\n")

    scrape_list()