"""
End-to-end test — verifies the full flow:
Register → Login → Profile → Search → Eligibility → Recommendations → Bookmark → Apply
"""
import os
import sys
import json
import requests
from datetime import datetime

BASE = "http://localhost:5000/api"
TEST_EMAIL = f"e2e_{int(datetime.utcnow().timestamp())}@test.com"
TEST_PASSWORD = "test1234"

results = []


def check(name, passed, detail=""):
    icon = "✅" if passed else "❌"
    results.append({"name": name, "passed": passed, "detail": detail})
    print(f"  {icon} {name} {('- ' + detail) if detail else ''}")


def main():
    print("\n" + "=" * 60)
    print("  ScholarNexus — End-to-End Test")
    print("=" * 60 + "\n")

    # 1. Health check
    print("1. Health Check")
    r = requests.get(f"{BASE}/health")
    check("Health endpoint", r.status_code == 200 and r.json().get("status") == "ok")

    # 2. Register
    print("\n2. Student Registration")
    r = requests.post(f"{BASE}/auth/register", json={
        "name": "E2E Test User",
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    check("Register new user", r.status_code == 201)

    # 3. Duplicate registration rejected
    r = requests.post(f"{BASE}/auth/register", json={
        "name": "E2E Test User",
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    check("Duplicate email rejected (409)", r.status_code == 409)

    # 4. Login
    print("\n3. Login")
    r = requests.post(f"{BASE}/auth/login", json={
        "email": TEST_EMAIL, "password": TEST_PASSWORD
    })
    check("Login succeeds", r.status_code == 200)
    token = r.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # 5. Wrong password rejected
    r = requests.post(f"{BASE}/auth/login", json={
        "email": TEST_EMAIL, "password": "wrong"
    })
    check("Wrong password rejected (401)", r.status_code == 401)

    # 6. Profile before completion
    print("\n4. Profile")
    r = requests.get(f"{BASE}/profile/", headers=headers)
    check("Get empty profile", r.status_code == 200)

    # 7. Save profile
    r = requests.post(f"{BASE}/profile/", headers=headers, json={
        "state": "Maharashtra", "category": "OBC", "gender": "Male",
        "income": 350000, "course": "B.Tech", "branch": "CSE",
        "year": "3", "percentage": 85, "college": "Test College"
    })
    check("Save profile", r.status_code == 200)

    # 8. Invalid profile (missing fields)
    r = requests.post(f"{BASE}/profile/", headers=headers, json={"state": "MH"})
    check("Invalid profile rejected (400)", r.status_code == 400)

    # 9. Invalid percentage
    r = requests.post(f"{BASE}/profile/", headers=headers, json={
        "state": "MH", "category": "OBC", "gender": "Male",
        "income": 350000, "course": "B.Tech", "percentage": 150
    })
    check("Invalid percentage rejected (400)", r.status_code == 400)

    # 10. Profile completion
    r = requests.get(f"{BASE}/profile/completion", headers=headers)
    check("Profile completion = 100%", r.json().get("completion") == 100)

    # 11. Search scholarships
    print("\n5. Scholarships")
    r = requests.get(f"{BASE}/scholarships/search")
    check("Search returns results", r.status_code == 200 and r.json().get("count", 0) > 0)
    total = r.json().get("count", 0)

    r = requests.get(f"{BASE}/scholarships/search", params={"category": "SC"})
    check("Filter by category works", r.status_code == 200)

    r = requests.get(f"{BASE}/scholarships/search", params={"state": "Maharashtra"})
    check("Filter by state works", r.status_code == 200)

    # 12. Get a scholarship
    r = requests.get(f"{BASE}/scholarships/")
    first = r.json()["results"][0]
    sid = first["scholarship_id"]
    check(f"Get scholarship list ({total} total)", r.status_code == 200)

    # 13. Eligibility check
    print("\n6. Eligibility")
    r = requests.get(f"{BASE}/scholarships/{sid}/eligibility", headers=headers)
    check(f"Check eligibility for {sid}", r.status_code == 200)
    if r.status_code == 200:
        data = r.json()
        check("Eligibility has status", "status" in data)
        check("Eligibility has matched[]", "matched" in data)
        check("Eligibility has failed[]", "failed" in data)

    # 14. Recommendations
    print("\n7. AI Recommendations")
    r = requests.get(f"{BASE}/scholarships/recommendations", headers=headers)
    check("Recommendations returned", r.status_code == 200)
    if r.status_code == 200:
        recs = r.json().get("recommendations", [])
        check(f"Has recommendations ({len(recs)})", len(recs) > 0)
        if recs:
            check("Each has match_percentage", "match_percentage" in recs[0])
            check("Each has breakdown", "breakdown" in recs[0])
            # Check sorted descending
            scores = [r["match_percentage"] for r in recs]
            check("Sorted descending", scores == sorted(scores, reverse=True))

    # 15. Bookmark
    print("\n8. Bookmark")
    r = requests.post(f"{BASE}/scholarships/bookmark/{sid}", headers=headers)
    check(f"Bookmark {sid}", r.status_code == 200)

    r = requests.get(f"{BASE}/scholarships/bookmarks", headers=headers)
    check("Bookmark appears in list", any(b["scholarship_id"] == sid for b in r.json()))

    # 16. Unbookmark (toggle)
    r = requests.post(f"{BASE}/scholarships/bookmark/{sid}", headers=headers)
    check("Unbookmark works", r.json().get("bookmarked") is False)

    # 17. Document checklist
    print("\n9. Documents")
    r = requests.get(f"{BASE}/documents/{sid}", headers=headers)
    check("Get document checklist", r.status_code == 200)
    if r.status_code == 200:
        data = r.json()
        check("Checklist has items", "checklist" in data)

    # 18. Application tracking
    print("\n10. Application Tracking")
    r = requests.post(f"{BASE}/applications/", headers=headers, json={
        "scholarship_id": sid, "status": "Interested"
    })
    check("Create application", r.status_code == 200)

    r = requests.post(f"{BASE}/applications/", headers=headers, json={
        "scholarship_id": sid, "status": "InvalidStatus"
    })
    check("Invalid status rejected (400)", r.status_code == 400)

    r = requests.get(f"{BASE}/applications/", headers=headers)
    check("Application appears in list", any(a["scholarship_id"] == sid for a in r.json()))

    # 19. Chatbot
    print("\n11. Chatbot")
    r = requests.post(f"{BASE}/chatbot/ask", json={"question": "How many scholarships are available?"})
    check("Chatbot responds", r.status_code == 200 and r.json().get("intent") == "count")

    r = requests.post(f"{BASE}/chatbot/ask", headers=headers,
                      json={"question": "Am I eligible for National Merit Scholarship?"})
    check("Chatbot eligibility intent", r.json().get("intent") == "eligibility")

    # 20. Notifications
    print("\n12. Notifications")
    r = requests.get(f"{BASE}/notifications/", headers=headers)
    check("Get notifications", r.status_code == 200)

    # 21. Unauthorized access
    print("\n13. Security")
    r = requests.get(f"{BASE}/profile/")
    check("Unauthorized profile blocked (401)", r.status_code == 401)

    r = requests.get(f"{BASE}/scholarships/recommendations")
    check("Unauthorized recommendations blocked (401)", r.status_code == 401)

    r = requests.post(f"{BASE}/admin/analytics")
    check("Admin endpoint protected (401)", r.status_code == 401)

    # Summary
    print("\n" + "=" * 60)
    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed
    print(f"  RESULTS: {passed} passed, {failed} failed of {len(results)}")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())