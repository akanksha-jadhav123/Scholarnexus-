"""
Scholarship Comparison — side-by-side field comparison with highlights.
"""


class ComparisonService:

    FIELDS = [
        {"key": "provider", "label": "Provider", "type": "text"},
        {"key": "scholarship_amount", "label": "Amount (₹)", "type": "number", "higher_better": True},
        {"key": "application_deadline", "label": "Deadline", "type": "date"},
        {"key": "minimum_percentage", "label": "Min %", "type": "number", "lower_better": True},
        {"key": "max_family_income", "label": "Max Income (₹)", "type": "number", "higher_better": True},
        {"key": "course", "label": "Course", "type": "text"},
        {"key": "category", "label": "Category", "type": "text"},
        {"key": "state", "label": "State", "type": "text"},
        {"key": "gender", "label": "Gender", "type": "text"},
    ]

    @classmethod
    def compare(cls, scholarships):
        """Return a structured comparison table."""
        if not scholarships or len(scholarships) < 2:
            return {"error": "Need at least 2 scholarships to compare"}

        rows = []

        for field in cls.FIELDS:
            row = {
                "field": field["key"],
                "label": field["label"],
                "values": [],
                "best": None
            }

            values = [sc.get(field["key"]) for sc in scholarships]
            row["values"] = values

            # Determine best value
            if field["type"] == "number":
                numeric = []
                for i, v in enumerate(values):
                    try:
                        numeric.append((i, float(v) if v is not None else None))
                    except (ValueError, TypeError):
                        numeric.append((i, None))

                valid = [(i, v) for i, v in numeric if v is not None]
                if valid:
                    if field.get("higher_better"):
                        best = max(valid, key=lambda x: x[1])
                    elif field.get("lower_better"):
                        best = min(valid, key=lambda x: x[1])
                    else:
                        best = None
                    if best:
                        row["best"] = best[0]

            elif field["type"] == "date":
                # Earliest date that isn't in the past
                from datetime import datetime
                today = datetime.utcnow().date()
                valid = []
                for i, v in enumerate(values):
                    if not v:
                        continue
                    try:
                        d = datetime.fromisoformat(str(v)).date()
                        if d >= today:
                            valid.append((i, d))
                    except Exception:
                        pass
                if valid:
                    best = min(valid, key=lambda x: x[1])
                    row["best"] = best[0]

            rows.append(row)

        return {
            "count": len(scholarships),
            "scholarships": [
                {
                    "scholarship_id": s.get("scholarship_id"),
                    "scholarship_name": s.get("scholarship_name")
                } for s in scholarships
            ],
            "rows": rows
        }