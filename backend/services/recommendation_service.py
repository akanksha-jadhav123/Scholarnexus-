WEIGHTS = {
    "income": 20, "percentage": 25, "category": 15,
    "state": 10, "course": 15, "gender": 5, "year": 10
}


def compute_match_score(profile, scholarship):
    score = 0
    breakdown = []

    if profile.get("income") is not None and scholarship.get("max_family_income") is not None:
        if float(profile["income"]) <= float(scholarship["max_family_income"]):
            score += WEIGHTS["income"]
            breakdown.append({"field": "income", "points": WEIGHTS["income"], "matched": True})

    if profile.get("percentage") is not None and scholarship.get("minimum_percentage") is not None:
        if float(profile["percentage"]) >= float(scholarship["minimum_percentage"]):
            score += WEIGHTS["percentage"]
            breakdown.append({"field": "percentage", "points": WEIGHTS["percentage"], "matched": True})

    for field in ["category", "state", "course", "gender"]:
        sc_val = scholarship.get(field, "All")
        if sc_val == "All" or sc_val == profile.get(field):
            score += WEIGHTS[field]
            breakdown.append({"field": field, "points": WEIGHTS[field], "matched": True})

    return {"match_percentage": score, "breakdown": breakdown}


def recommend_scholarships(profile, scholarships):
    results = []
    for sc in scholarships:
        result = compute_match_score(profile, sc)
        if result["match_percentage"] > 0:
            sc_out = {k: v for k, v in sc.items() if k != "_id"}
            sc_out["match_percentage"] = result["match_percentage"]
            sc_out["breakdown"] = result["breakdown"]
            results.append(sc_out)
    results.sort(key=lambda x: x["match_percentage"], reverse=True)
    return results