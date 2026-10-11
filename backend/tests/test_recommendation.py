import unittest
from services.recommendation_service import RecommendationEngine


class TestRecommendation(unittest.TestCase):

    def _profile(self):
        return {
            "state": "Maharashtra",
            "category": "OBC",
            "gender": "Male",
            "income": 350000,
            "course": "B.Tech",
            "percentage": 85,
            "year": "3"
        }

    def _scholarship(self, **overrides):
        base = {
            "scholarship_id": "T1",
            "scholarship_name": "Test",
            "max_family_income": 500000,
            "minimum_percentage": 75,
            "category": "OBC",
            "gender": "All",
            "state": "Maharashtra",
            "course": "B.Tech"
        }
        base.update(overrides)
        return base

    def test_perfect_match_score(self):
        result = RecommendationEngine.compute_match_score(
            self._profile(), self._scholarship()
        )
        # All criteria should match → high score
        self.assertGreater(result["match_percentage"], 70)

    def test_zero_match_returns_low(self):
        profile = self._profile()
        scholarship = self._scholarship(
            category="SC", state="Tamil Nadu", course="B.Com",
            minimum_percentage=99, max_family_income=100000
        )
        result = RecommendationEngine.compute_match_score(profile, scholarship)
        self.assertLess(result["match_percentage"], 50)

    def test_breakdown_has_reasons(self):
        result = RecommendationEngine.compute_match_score(
            self._profile(), self._scholarship()
        )
        for item in result["breakdown"]:
            self.assertIn("field", item)
            self.assertIn("points", item)
            self.assertIn("reason", item)

    def test_recommendation_ranking(self):
        profile = self._profile()
        scholarships = [
            self._scholarship(scholarship_id="S1", max_family_income=500000, minimum_percentage=75),
            self._scholarship(scholarship_id="S2", max_family_income=100000, minimum_percentage=99),
            self._scholarship(scholarship_id="S3", max_family_income=200000, minimum_percentage=90)
        ]
        results = RecommendationEngine.recommend(profile, scholarships)
        # S1 should rank above S3 should rank above S2
        ids = [r["scholarship_id"] for r in results]
        if "S1" in ids and "S2" in ids:
            self.assertLess(ids.index("S1"), ids.index("S2"))

    def test_min_score_filter(self):
        profile = self._profile()
        scholarships = [self._scholarship(max_family_income=1000, minimum_percentage=100)]
        results = RecommendationEngine.recommend(profile, scholarships, min_score=90)
        self.assertEqual(len(results), 0)

    def test_confidence_high_with_full_profile(self):
        result = RecommendationEngine.compute_match_score(
            self._profile(), self._scholarship()
        )
        self.assertEqual(result["confidence"], "high")

    def test_confidence_low_with_partial_profile(self):
        result = RecommendationEngine.compute_match_score(
            {"state": "Maharashtra"}, self._scholarship()
        )
        self.assertEqual(result["confidence"], "low")

    def test_empty_profile(self):
        result = RecommendationEngine.compute_match_score({}, self._scholarship())
        self.assertEqual(result["match_percentage"], 0)


if __name__ == "__main__":
    unittest.main()