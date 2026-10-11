"""
Validates normalized scholarship records before saving.
"""
import re


class Validator:

    REQUIRED_FIELDS = ["scholarship_name", "application_url"]

    @classmethod
    def validate(cls, record):
        """Return (is_valid, errors)."""
        errors = []

        # 1. Required fields
        for field in cls.REQUIRED_FIELDS:
            if not record.get(field):
                errors.append(f"missing {field}")

        # 2. Name length
        name = record.get("scholarship_name", "")
        if name and len(name) < 5:
            errors.append("name too short")

        # 3. URL format
        url = record.get("application_url", "")
        if url and not re.match(r"^https?://", url):
            errors.append("invalid URL")

        # 4. Numeric ranges
        pct = record.get("minimum_percentage")
        if pct is not None and (pct < 0 or pct > 100):
            errors.append("percentage out of range")

        income = record.get("max_family_income")
        if income is not None and income < 0:
            errors.append("negative income")

        # 5. Deadline not in past (optional)
        deadline = record.get("application_deadline")
        if deadline:
            try:
                from datetime import datetime
                d = datetime.strptime(deadline, "%Y-%m-%d").date()
                if d.year < 2020 or d.year > 2030:
                    errors.append("deadline year out of range")
            except Exception:
                pass

        return (len(errors) == 0, errors)

    @classmethod
    def is_valid(cls, record):
        valid, _ = cls.validate(record)
        return valid