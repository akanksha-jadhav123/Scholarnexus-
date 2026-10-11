"""
Eligibility Checker — rule-based 6-criteria engine with explanations.
Returns status, matched[], failed[], reason, and score contribution.
"""


class EligibilityChecker:

    CRITERIA = ["income", "percentage", "category", "gender", "state", "course"]

    @classmethod
    def check(cls, profile, scholarship):
        """Returns detailed eligibility result."""
        matched = []
        failed = []
        warnings = []

        # Handle missing profile fields
        if not profile:
            return {
                "status": "incomplete_profile",
                "matched": [],
                "failed": [],
                "warnings": ["Please complete your profile to check eligibility."],
                "reason": "Profile is empty.",
                "score": 0
            }

        # 1. Income
        cls._check_income(profile, scholarship, matched, failed)

        # 2. Percentage
        cls._check_percentage(profile, scholarship, matched, failed)

        # 3-6. Category, Gender, State, Course
        for field in ["category", "gender", "state", "course"]:
            cls._check_field(profile, scholarship, field, matched, failed)

        # Status determination
        if not failed:
            status = "eligible"
            reason = "You meet all criteria. Apply now!"
        elif len(failed) <= 2:
            status = "partial"
            reason = f"Almost there! You're missing {len(failed)} criterion/criteria."
        else:
            status = "not_eligible"
            reason = f"Not eligible — you don't meet {len(failed)} criteria."

        # Score: matched / total × 100
        total = len(matched) + len(failed)
        score = int((len(matched) / total) * 100) if total > 0 else 0

        return {
            "status": status,
            "matched": matched,
            "failed": failed,
            "warnings": warnings,
            "reason": reason,
            "score": score,
            "criteria_checked": total,
            "criteria_matched": len(matched)
        }

    @classmethod
    def _check_income(cls, profile, scholarship, matched, failed):
        p_income = profile.get("income")
        s_limit = scholarship.get("max_family_income")

        if p_income is None:
            failed.append("Income not provided in profile")
            return
        if s_limit is None:                       # ✅ Was s_limit >= 999999999
            matched.append("No income limit specified for this scholarship")
            return

        try:
            if float(p_income) <= float(s_limit):
                matched.append(f"Your income ₹{int(p_income):,} ≤ limit ₹{int(s_limit):,}")
            else:
                failed.append(f"Income ₹{int(p_income):,} exceeds limit ₹{int(s_limit):,}")
        except (ValueError, TypeError):
            failed.append("Invalid income value")

    @classmethod
    def _check_percentage(cls, profile, scholarship, matched, failed):
        p_pct = profile.get("percentage")
        s_min = scholarship.get("minimum_percentage")

        if p_pct is None:
            failed.append("Percentage not provided in profile")
            return
        if s_min is None:                          # ✅ Was s_min == 0
            matched.append("No minimum percentage specified")
            return

        try:
            if float(p_pct) >= float(s_min):
                matched.append(f"Your {p_pct}% ≥ required {s_min}%")
            else:
                failed.append(f"Your {p_pct}% is below required {s_min}%")
        except (ValueError, TypeError):
            failed.append("Invalid percentage value")

    @classmethod
    def _check_field(cls, profile, scholarship, field, matched, failed):
        p_val = profile.get(field)
        s_val = scholarship.get(field)

        label = field.capitalize()

        if not p_val:
            failed.append(f"{label} not provided in profile")
            return

        # Scholarship criterion unknown — flag it
        if s_val is None:
            matched.append(f"{label}: Open (criterion not specified)")
            return

        # Scholarship open to all
        if str(s_val).lower() in ("all", "any", ""):
            matched.append(f"{label}: Open to all ({p_val})")
            return

        # Case-insensitive comparison
        if str(p_val).strip().lower() == str(s_val).strip().lower():
            matched.append(f"{label} matches: {p_val}")
        else:
            failed.append(f"{label} mismatch (needs {s_val}, you have {p_val})")

# Backward-compatible function
def check_eligibility(profile, scholarship):
    return EligibilityChecker.check(profile, scholarship)