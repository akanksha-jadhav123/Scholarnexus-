import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_scholarship_collection
import hashlib

def make_id(name):
    return hashlib.md5(name.encode()).hexdigest()[:12]

def seed_aicte_data():
    collection = get_scholarship_collection()
    
    aicte_scholarships = [
        {
            "scholarship_name": "AICTE Pragati Scholarship Scheme for Girl Students",
            "provider": "AICTE (Government of India)",
            "scholarship_amount": "₹50,000 per annum",
            "course": "Degree/Diploma (Technical)",
            "state": "All India",
            "category": "Girl Students",
            "gender": "Female",
            "application_deadline": "2025-10-31", # Based on recent notification [citation:18]
            "minimum_percentage": 0,
            "max_income": 800000,
            "eligibility": "Girl students admitted to 1st year of AICTE approved Degree/Diploma course. Family income must be less than ₹8 lakh per annum.",
            "apply_link": "https://scholarships.gov.in",
            "source_website": "aicte-india.org",
            "scraped_at": datetime.now()
        },
        {
            "scholarship_name": "AICTE Saksham Scholarship Scheme for Specially-Abled Students",
            "provider": "AICTE (Government of India)",
            "scholarship_amount": "₹50,000 per annum",
            "course": "Degree/Diploma (Technical)",
            "state": "All India",
            "category": "Specially-Abled",
            "gender": "All",
            "application_deadline": "2025-10-31",
            "minimum_percentage": 0,
            "max_income": 800000,
            "eligibility": "Specially-abled students with ≥40% disability, admitted to 1st year of AICTE approved Degree/Diploma course. Family income < ₹8 lakh per annum.",
            "apply_link": "https://scholarships.gov.in",
            "source_website": "aicte-india.org",
            "scraped_at": datetime.now()
        },
        {
            "scholarship_name": "AICTE Swanath Scholarship Scheme",
            "provider": "AICTE (Government of India)",
            "scholarship_amount": "₹50,000 per annum",
            "course": "Degree/Diploma (Technical)",
            "state": "All India",
            "category": "Orphan/COVID-affected/Martyrs' Wards",
            "gender": "All",
            "application_deadline": "2025-10-31",
            "minimum_percentage": 0,
            "max_income": 800000,
            "eligibility": "Orphans, wards of parents who died due to COVID-19, or wards of Armed Forces/Paramilitary martyrs. Family income < ₹8 lakh.",
            "apply_link": "https://scholarships.gov.in",
            "source_website": "aicte-india.org",
            "scraped_at": datetime.now()
        },
        {
            "scholarship_name": "AICTE PG Scholarship Scheme (GATE/GPAT)",
            "provider": "AICTE (Government of India)",
            "scholarship_amount": "₹12,400 per month",
            "course": "M.E/M.Tech/M.Arch/M.Pharm",
            "state": "All India",
            "category": "PG Students",
            "gender": "All",
            "application_deadline": "2025-12-15", # Based on recent notification [citation:37]
            "minimum_percentage": 0,
            "max_income": 0,
            "eligibility": "Full-time students admitted to AICTE approved PG programs with a valid GATE/GPAT score at the time of admission.",
            "apply_link": "https://pgscholarship.aicte.gov.in/",
            "source_website": "aicte-india.org",
            "scraped_at": datetime.now()
        }
    ]
    
    saved_count = 0
    for s in aicte_scholarships:
        s["scholarship_id"] = make_id(s["scholarship_name"])
        collection.update_one(
            {"scholarship_id": s["scholarship_id"]},
            {"$set": s},
            upsert=True
        )
        saved_count += 1
        print(f"✅ Saved: {s['scholarship_name']}")
    
    print(f"\n🎉 Successfully seeded {saved_count} AICTE scholarships.")

if __name__ == "__main__":
    seed_aicte_data()