"""
AI Recommendation — weighted match score + ranking + explainability.
"""

WEIGHTS = {
    "percentage": 25,
    "income": 20,
    "category": 15,
    "course": 15,
    "state": 10,
    "year": 10,
    "gender": 5
}


class RecommendationEngine:

    @classmethod
    def compute_match_score(cls, profile, scholarship):
        """Compute weighted match score (0-100) + breakdown."""
        if not profile:
            return {"match_percentage": 0, "breakdown": [], "confidence": "low"}

        score = 0
        breakdown = []
        missing = []

        # Percentage
        cls._score_percentage(profile, scholarship, breakdown)
        # Income
        cls._score_income(profile, scholarship, breakdown)
        # Category, Course, State, Year, Gender
        for field in ["category", "course", "state", "year", "gender"]:
            cls._score_field(profile, scholarship, field, breakdown)

        score = sum(b["points"] for b in breakdown)

        # Confidence based on profile completeness
        profile_fields = ["state", "category", "gender", "income", "course", "percentage"]
        filled = sum(1 for f in profile_fields if profile.get(f))
        confidence = "high" if filled == len(profile_fields) else "medium" if filled >= 4 else "low"

        return {
            "match_percentage": score,
            "breakdown": breakdown,
            "confidence": confidence
        }

    @classmethod
    def _score_percentage(cls, profile, scholarship, breakdown):
        p_pct = profile.get("percentage")
        s_min = scholarship.get("minimum_percentage")
        if p_pct is None or s_min is None or s_min == 0:
            return
        try:
            if float(p_pct) >= float(s_min):
                breakdown.append({
                    "field": "percentage",
                    "points": WEIGHTS["percentage"],
                    "reason": f"Your {p_pct}% meets the {s_min}% requirement"
                })
        except (ValueError, TypeError):
            pass

    @classmethod
    def _score_income(cls, profile, scholarship, breakdown):
        p_income = profile.get("income")
        s_limit = scholarship.get("max_family_income")
        if p_income is None or s_limit is None or s_limit >= 999999999:
            return
        try:
            if float(p_income) <= float(s_limit):
                breakdown.append({
                    "field": "income",
                    "points": WEIGHTS["income"],
                    "reason": f"Income within ₹{int(s_limit):,} limit"
                })
        except (ValueError, TypeError):
            pass

    @classmethod
    def _score_field(cls, profile, scholarship, field, breakdown):
        p_val = profile.get(field)
        s_val = scholarship.get(field, "All")
        if not p_val:
            return
        if not s_val or str(s_val).lower() in ("all", "any", ""):
            breakdown.append({
                "field": field,
                "points": WEIGHTS[field],
                "reason": f"Open to all ({field})"
            })
        elif str(p_val).strip().lower() == str(s_val).strip().lower():
            breakdown.append({
                "field": field,
                "points": WEIGHTS[field],
                "reason": f"{field.capitalize()} matches ({p_val})"
            })

    @classmethod
    def recommend(cls, profile, scholarships, limit=20, min_score=20):
        """Return ranked scholarships with match score + breakdown."""
        results = []

        for sc in scholarships:
            result = cls.compute_match_score(profile, sc)
            if result["match_percentage"] < min_score:
                continue

            sc_out = {k: v for k, v in sc.items() if k != "_id"}
            sc_out["match_percentage"] = result["match_percentage"]
            sc_out["breakdown"] = result["breakdown"]
            sc_out["confidence"] = result["confidence"]
            results.append(sc_out)

        # Sort descending by match %
        results.sort(key=lambda x: (
            -x["match_percentage"],                      # primary: highest score
            x.get("application_deadline") or "9999",     # secondary: earliest deadline
            -(x.get("scholarship_amount") or 0)          # tertiary: highest amount
        ))

        return results[:limit]


# Backward-compatible functions
def compute_match_score(profile, scholarship):
    return RecommendationEngine.compute_match_score(profile, scholarship)


def recommend_scholarships(profile, scholarships):
    return RecommendationEngine.recommend(profile, scholarships)