def check_eligibility(profile, scholarship):
    matched = []
    failed = []

    if profile.get("income") is not None and scholarship.get("max_family_income") is not None:
        if float(profile["income"]) <= float(scholarship["max_family_income"]):
            matched.append(f"Income ≤ ₹{scholarship['max_family_income']}")
        else:
            failed.append(f"Income exceeds ₹{scholarship['max_family_income']}")

    if profile.get("percentage") is not None and scholarship.get("minimum_percentage") is not None:
        if float(profile["percentage"]) >= float(scholarship["minimum_percentage"]):
            matched.append(f"Marks ≥ {scholarship['minimum_percentage']}%")
        else:
            failed.append(f"Marks below {scholarship['minimum_percentage']}%")

    sc_cat = scholarship.get("category", "All")
    if sc_cat == "All" or sc_cat == profile.get("category"):
        matched.append(f"Category: {profile.get('category', 'N/A')}")
    else:
        failed.append(f"Category mismatch (needs {sc_cat})")

    sc_gender = scholarship.get("gender", "All")
    if sc_gender == "All" or sc_gender == profile.get("gender"):
        matched.append(f"Gender: {profile.get('gender', 'N/A')}")
    else:
        failed.append(f"Gender mismatch (needs {sc_gender})")

    sc_state = scholarship.get("state", "All")
    if sc_state == "All" or sc_state == profile.get("state"):
        matched.append(f"State: {profile.get('state', 'N/A')}")
    else:
        failed.append(f"State mismatch (needs {sc_state})")

    sc_course = scholarship.get("course", "All")
    if sc_course == "All" or sc_course == profile.get("course"):
        matched.append(f"Course: {profile.get('course', 'N/A')}")
    else:
        failed.append(f"Course mismatch (needs {sc_course})")

    if not failed:
        status = "eligible"
        reason = "You meet all criteria."
    elif len(failed) <= 2:
        status = "partial"
        reason = "Partially matched: " + "; ".join(failed)
    else:
        status = "not_eligible"
        reason = "Not eligible: " + "; ".join(failed)

    return {"status": status, "matched": matched, "failed": failed, "reason": reason}