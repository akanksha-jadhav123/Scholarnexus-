import unittest
from services.eligibility_service import EligibilityChecker


class TestEligibility(unittest.TestCase):

    def _profile(self, **overrides):
        base = {
            "state": "Maharashtra",
            "category": "OBC",
            "gender": "Male",
            "income": 350000,
            "course": "B.Tech",
            "percentage": 85
        }
        base.update(overrides)
        return base

    def _scholarship(self, **overrides):
        base = {
            "scholarship_id": "TEST001",
            "scholarship_name": "Test Scholarship",
            "max_family_income": 500000,
            "minimum_percentage": 75,
            "category": "OBC",
            "gender": "All",
            "state": "Maharashtra",
            "course": "B.Tech"
        }
        base.update(overrides)
        return base

    def test_all_criteria_matched(self):
        result = EligibilityChecker.check(self._profile(), self._scholarship())
        self.assertEqual(result["status"], "eligible")
        self.assertEqual(len(result["failed"]), 0)

    def test_income_exceeds_limit(self):
        result = EligibilityChecker.check(
            self._profile(income=900000),
            self._scholarship()
        )
        self.assertIn(result["status"], ["partial", "not_eligible"])
        self.assertTrue(any("income" in f.lower() for f in result["failed"]))

    def test_percentage_below_minimum(self):
        result = EligibilityChecker.check(
            self._profile(percentage=50),
            self._scholarship()
        )
        self.assertTrue(any("below" in f.lower() for f in result["failed"]))

    def test_category_mismatch(self):
        result = EligibilityChecker.check(
            self._profile(category="General"),
            self._scholarship()
        )
        self.assertTrue(any("Category" in f for f in result["failed"]))

    def test_wildcard_all(self):
        result = EligibilityChecker.check(
            self._profile(),
            self._scholarship(category="All", state="All", course="All")
        )
        self.assertEqual(result["status"], "eligible")

    def test_missing_profile(self):
        result = EligibilityChecker.check({}, self._scholarship())
        self.assertEqual(result["status"], "incomplete_profile")

    def test_boundary_income_exact(self):
        result = EligibilityChecker.check(
            self._profile(income=500000),
            self._scholarship(max_family_income=500000)
        )
        # Income exactly at limit should pass
        income_ok = any("income" in m.lower() for m in result["matched"])
        self.assertTrue(income_ok, "Income at exact limit should pass")

    def test_boundary_percentage_exact(self):
        result = EligibilityChecker.check(
            self._profile(percentage=75),
            self._scholarship(minimum_percentage=75)
        )
        pct_ok = any("75" in m for m in result["matched"])
        self.assertTrue(pct_ok, "Percentage at exact limit should pass")

    def test_multi_criteria_failure(self):
        result = EligibilityChecker.check(
            self._profile(income=900000, percentage=50, category="General"),
            self._scholarship()
        )
        self.assertEqual(result["status"], "not_eligible")
        self.assertGreaterEqual(len(result["failed"]), 3)

    def test_score_is_percentage(self):
        result = EligibilityChecker.check(self._profile(), self._scholarship())
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)


if __name__ == "__main__":
    unittest.main()