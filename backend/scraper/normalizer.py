"""
Normalizes raw scraped records — supports multi-value fields and NULLs.
"""
import re
from datetime import datetime


class Normalizer:

    @staticmethod
    def normalize(record):
        return {
            "scholarship_id": Normalizer._make_id(record),
            "scholarship_name": Normalizer._text(record.get("scholarship_name")),
            "provider": Normalizer._text(record.get("provider")) or "Unknown Provider",

            # Amount range (NEW)
            "amount_min": Normalizer._num_or_none(record.get("amount_min")),
            "amount_max": Normalizer._num_or_none(record.get("amount_max")) or
                          Normalizer._num_or_none(record.get("scholarship_amount")),
            # backward compat
            "scholarship_amount": Normalizer._num_or_none(record.get("scholarship_amount")) or
                                  Normalizer._num_or_none(record.get("amount_max")),

            # Course & branch
            "course": record.get("course") or None,
            "branch": record.get("branch") or None,

            # Eligibility criteria
            "minimum_percentage": Normalizer._num_or_none(record.get("minimum_percentage")),
            "max_family_income": Normalizer._num_or_none(record.get("max_family_income")) or
                                 Normalizer._num_or_none(record.get("family_income_limit")),

            # Multi-value fields (NEW)
            "eligible_states": Normalizer._to_multi(record.get("eligible_states") or record.get("state")),
            "eligible_categories": Normalizer._to_multi(record.get("eligible_categories") or record.get("category")),
            "eligible_courses": Normalizer._to_multi(record.get("eligible_courses") or record.get("course")),
            "eligible_genders": Normalizer._to_multi(record.get("eligible_genders") or record.get("gender")),

            # Backward-compatible single values (for eligibility engine)
            "state": record.get("state") or Normalizer._first(record.get("eligible_states")) or None,
            "category": record.get("category") or Normalizer._first(record.get("eligible_categories")) or None,
            "gender": record.get("gender") or Normalizer._first(record.get("eligible_genders")) or None,

            # Dates
            "application_start": Normalizer._date(record.get("application_start") or record.get("application_start_date")),
            "application_deadline": Normalizer._date(record.get("application_deadline") or record.get("deadline")),

            # Documents
            "required_documents": Normalizer._list(record.get("required_documents")),
            "eligibility_description": Normalizer._text(record.get("eligibility_description")),

            # URLs
            "official_source": record.get("official_source") or "",
            "application_url": record.get("application_url") or record.get("official_url") or "",

            "status": record.get("status") or "Active",

            # Source tracking
            "source": record.get("source") or record.get("source_name") or "unknown",
            "source_url": record.get("source_url") or record.get("official_source") or "",
            "source_type": record.get("source_type") or "Unknown",
            "source_trust_score": record.get("source_trust_score") or 5,
            "link_status": record.get("link_status") or "pending",
            "last_verified_at": None,

            # Data quality
            "data_quality": Normalizer._quality_flags(record),
            "scraped_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }

    @staticmethod
    def _quality_flags(record):
        flags = {"complete": True, "missing_fields": []}
        for f in ["scholarship_name", "application_url"]:
            if not record.get(f):
                flags["complete"] = False
                flags["missing_fields"].append(f)
        # Mark nulls explicitly
        for f in ["amount_max", "minimum_percentage", "max_family_income", "application_deadline"]:
            if not record.get(f):
                flags["missing_fields"].append(f)
        return flags

    @staticmethod
    def _text(t):
        if t is None:
            return ""
        return " ".join(str(t).split()).strip()[:500]

    @staticmethod
    def _num_or_none(v):
        """Return number or None — never a misleading default."""
        if v is None or v == "":
            return None
        try:
            s = str(v).lower().replace("₹", "").replace(",", "").replace("rs.", "").strip()
            if "lakh" in s:
                return float(re.sub(r"[^0-9.]", "", s.split("lakh")[0]) or 0) * 100000
            if "crore" in s:
                return float(re.sub(r"[^0-9.]", "", s.split("crore")[0]) or 0) * 10000000
            if s.endswith("k"):
                return float(s[:-1]) * 1000
            return float(re.sub(r"[^0-9.]", "", s) or 0)
        except Exception:
            return None

    @staticmethod
    def _date(d):
        if not d:
            return None
        formats = [
            "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y",
            "%d %b %Y", "%d %B %Y", "%b %d, %Y",
            "%d.%m.%Y", "%Y/%m/%d"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(str(d).strip()[:30], fmt).date().isoformat()
            except Exception:
                continue
        return None

    @staticmethod
    def _list(v):
        if not v:
            return []
        if isinstance(v, list):
            return [str(x).strip() for x in v if x]
        return [x.strip() for x in str(v).split(";") if x.strip()]

    @staticmethod
    def _to_multi(v):
        """Multi-value field → list."""
        if not v:
            return []
        if isinstance(v, list):
            return [str(x).strip() for x in v if x]
        # Split on common delimiters
        return [x.strip() for x in re.split(r"[;,|]", str(v)) if x.strip()]

    @staticmethod
    def _first(v):
        """Return first value of a multi-value field."""
        if not v:
            return None
        if isinstance(v, list):
            return v[0] if v else None
        return str(v).split(";")[0].strip() or None

    @staticmethod
    def _make_id(record):
        if record.get("scholarship_id"):
            return record["scholarship_id"]
        import hashlib
        key = f"{record.get('scholarship_name', '')}|{record.get('provider', '')}"
        h = hashlib.md5(key.encode()).hexdigest()[:8].upper()
        return f"AUTO{h}"