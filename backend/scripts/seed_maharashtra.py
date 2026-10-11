import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_scholarship_collection
import hashlib


def make_id(name):
    return hashlib.md5(name.encode()).hexdigest()[:12]


MAHARASHTRA_SCHEMES = [
    {
        "scholarship_name": "Rajarshi Chhatrapati Shahu Maharaj Shikshan Shulkh Shishyavrutti Yojna",
        "provider": "Government of Maharashtra (MahaDBT)",
        "scholarship_amount": "Tuition fee waiver up to 100%",
        "course": "All UG/PG",
        "state": "Maharashtra",
        "category": "EBC",
        "gender": "All",
        "application_deadline": "2026-12-31",
        "minimum_percentage": 50,
        "max_income": 800000,
        "eligibility": "Maharashtra domicile, EBC category students, family income < ₹8 lakh. Available for UG/PG professional courses.",
        "apply_link": "https://mahadbt.maharashtra.gov.in/",
        "source_website": "mahadbt.maharashtra.gov.in",
    },
    {
        "scholarship_name": "Dr. Panjabrao Deshmukh Vasatigruh Nirvah Bhatta Yojna",
        "provider": "Government of Maharashtra (MahaDBT)",
        "scholarship_amount": "₹10,000 - ₹30,000 per year",
        "course": "All UG/PG",
        "state": "Maharashtra",
        "category": "All",
        "gender": "All",
        "application_deadline": "2026-12-31",
        "minimum_percentage": 50,
        "max_income": 800000,
        "eligibility": "Maharashtra students in professional courses. Family income < ₹8 lakh.",
        "apply_link": "https://mahadbt.maharashtra.gov.in/",
        "source_website": "mahadbt.maharashtra.gov.in",
    },
    {
        "scholarship_name": "Government of India Post-Matric Scholarship for SC Students (Maharashtra)",
        "provider": "Government of India / Maharashtra (MahaDBT)",
        "scholarship_amount": "Tuition fees + maintenance allowance",
        "course": "Post-Matric (11th onwards)",
        "state": "Maharashtra",
        "category": "SC",
        "gender": "All",
        "application_deadline": "2026-12-31",
        "minimum_percentage": 0,
        "max_income": 250000,
        "eligibility": "SC category students from Maharashtra. Family income < ₹2.5 lakh.",
        "apply_link": "https://mahadbt.maharashtra.gov.in/",
        "source_website": "mahadbt.maharashtra.gov.in",
    },
    {
        "scholarship_name": "Post-Matric Scholarship for OBC Students (Maharashtra)",
        "provider": "Government of Maharashtra (MahaDBT)",
        "scholarship_amount": "Tuition fees + maintenance",
        "course": "Post-Matric",
        "state": "Maharashtra",
        "category": "OBC",
        "gender": "All",
        "application_deadline": "2026-12-31",
        "minimum_percentage": 0,
        "max_income": 250000,
        "eligibility": "OBC students from Maharashtra. Family income < ₹2.5 lakh.",
        "apply_link": "https://mahadbt.maharashtra.gov.in/",
        "source_website": "mahadbt.maharashtra.gov.in",
    },
    {
        "scholarship_name": "Post-Matric Scholarship for VJNT Students (Maharashtra)",
        "provider": "Government of Maharashtra (MahaDBT)",
        "scholarship_amount": "Tuition fees + maintenance",
        "course": "Post-Matric",
        "state": "Maharashtra",
        "category": "VJNT",
        "gender": "All",
        "application_deadline": "2026-12-31",
        "minimum_percentage": 0,
        "max_income": 250000,
        "eligibility": "Vimukta Jati and Nomadic Tribes students from Maharashtra.",
        "apply_link": "https://mahadbt.maharashtra.gov.in/",
        "source_website": "mahadbt.maharashtra.gov.in",
    },
    {
        "scholarship_name": "Post-Matric Scholarship for SBC Students (Maharashtra)",
        "provider": "Government of Maharashtra (MahaDBT)",
        "scholarship_amount": "Tuition fees + maintenance",
        "course": "Post-Matric",
        "state": "Maharashtra",
        "category": "SBC",
        "gender": "All",
        "application_deadline": "2026-12-31",
        "minimum_percentage": 0,
        "max_income": 250000,
        "eligibility": "Special Backward Class students from Maharashtra.",
        "apply_link": "https://mahadbt.maharashtra.gov.in/",
        "source_website": "mahadbt.maharashtra.gov.in",
    },
    {
        "scholarship_name": "Post-Matric Scholarship for ST Students (Maharashtra)",
        "provider": "Government of Maharashtra (Tribal Development Dept)",
        "scholarship_amount": "Tuition fees + maintenance",
        "course": "Post-Matric",
        "state": "Maharashtra",
        "category": "ST",
        "gender": "All",
        "application_deadline": "2026-12-31",
        "minimum_percentage": 0,
        "max_income": 250000,
        "eligibility": "ST students from Maharashtra. Family income < ₹2.5 lakh.",
        "apply_link": "https://tribal.maharashtra.gov.in/",
        "source_website": "tribal.maharashtra.gov.in",
    },
    {
        "scholarship_name": "Post-Matric Scholarship for Minority Students (Maharashtra)",
        "provider": "Government of Maharashtra (Minority Development Dept)",
        "scholarship_amount": "Tuition fees + maintenance",
        "course": "Post-Matric",
        "state": "Maharashtra",
        "category": "Minority",
        "gender": "All",
        "application_deadline": "2026-12-31",
        "minimum_percentage": 50,
        "max_income": 200000,
        "eligibility": "Minority community students from Maharashtra. Family income < ₹2 lakh.",
        "apply_link": "https://mdd.maharashtra.gov.in/",
        "source_website": "mdd.maharashtra.gov.in",
    },
    {
        "scholarship_name": "Eklavya Scholarship (Maharashtra)",
        "provider": "Government of Maharashtra",
        "scholarship_amount": "₹10,000 - ₹25,000",
        "course": "PG",
        "state": "Maharashtra",
        "category": "All",
        "gender": "All",
        "application_deadline": "2026-12-31",
        "minimum_percentage": 60,
        "max_income": 300000,
        "eligibility": "Maharashtra students pursuing PG. Minimum 60% in graduation.",
        "apply_link": "https://mahadbt.maharashtra.gov.in/",
        "source_website": "mahadbt.maharashtra.gov.in",
    },
    {
        "scholarship_name": "State Government Open Merit Scholarship (Maharashtra)",
        "provider": "Government of Maharashtra",
        "scholarship_amount": "₹100 per month",
        "course": "11th & 12th",
        "state": "Maharashtra",
        "category": "All",
        "gender": "All",
        "application_deadline": "2026-12-31",
        "minimum_percentage": 60,
        "max_income": 0,
        "eligibility": "Merit-based for Maharashtra 11th & 12th students.",
        "apply_link": "https://mahadbt.maharashtra.gov.in/",
        "source_website": "mahadbt.maharashtra.gov.in",
    },
    {
        "scholarship_name": "Rajya Parishad Merit Scholarship (Maharashtra)",
        "provider": "Government of Maharashtra",
        "scholarship_amount": "Variable",
        "course": "All",
        "state": "Maharashtra",
        "category": "All",
        "gender": "All",
        "application_deadline": "2026-12-31",
        "minimum_percentage": 75,
        "max_income": 0,
        "eligibility": "Top-performing Maharashtra students in board exams.",
        "apply_link": "https://mahadbt.maharashtra.gov.in/",
        "source_website": "mahadbt.maharashtra.gov.in",
    },
]


def seed():
    collection = get_scholarship_collection()
    saved = 0
    for s in MAHARASHTRA_SCHEMES:
        s["scholarship_id"] = make_id(s["scholarship_name"])
        s["scraped_at"] = datetime.now()
        collection.update_one(
            {"scholarship_id": s["scholarship_id"]},
            {"$set": s},
            upsert=True
        )
        saved += 1
        print(f"  ✅ {s['scholarship_name'][:70]}")
    print(f"\n🎉 Seeded {saved} Maharashtra scholarships")
    print(f"📊 Total in DB: {collection.count_documents({})}")


if __name__ == "__main__":
    seed()