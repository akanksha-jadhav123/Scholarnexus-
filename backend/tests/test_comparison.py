import unittest
from services.comparison_service import ComparisonService


class TestComparison(unittest.TestCase):

    def _scholarships(self):
        return [
            {
                "scholarship_id": "S1",
                "scholarship_name": "Scholarship A",
                "provider": "Provider X",
                "scholarship_amount": 50000,
                "application_deadline": "2026-12-31",
                "minimum_percentage": 80,
                "max_family_income": 500000,
                "course": "B.Tech",
                "category": "All",
                "state": "All",
                "gender": "All"
            },
            {
                "scholarship_id": "S2",
                "scholarship_name": "Scholarship B",
                "provider": "Provider Y",
                "scholarship_amount": 80000,
                "application_deadline": "2026-11-30",
                "minimum_percentage": 70,
                "max_family_income": 300000,
                "course": "All",
                "category": "OBC",
                "state": "Maharashtra",
                "gender": "All"
            },
        ]

    def test_compare_two(self):
        result = ComparisonService.compare(self._scholarships())
        self.assertEqual(result["count"], 2)
        self.assertIn("rows", result)

    def test_amount_highest_is_best(self):
        result = ComparisonService.compare(self._scholarships())
        amount_row = next(r for r in result["rows"] if r["field"] == "scholarship_amount")
        # S2 has 80000 > S1's 50000 → best should be index 1
        self.assertEqual(amount_row["best"], 1)

    def test_percentage_lowest_is_best(self):
        result = ComparisonService.compare(self._scholarships())
        pct_row = next(r for r in result["rows"] if r["field"] == "minimum_percentage")
        # S2 has 70 < S1's 80 → best should be index 1
        self.assertEqual(pct_row["best"], 1)

    def test_compare_needs_two(self):
        result = ComparisonService.compare([self._scholarships()[0]])
        self.assertIn("error", result)

    def test_compare_empty(self):
        result = ComparisonService.compare([])
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()