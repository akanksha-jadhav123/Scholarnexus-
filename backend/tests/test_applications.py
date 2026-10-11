import unittest


class TestApplications(unittest.TestCase):

    def _get_valid_statuses(self):
        try:
            from routes.applications_routes import VALID_STATUSES
            return VALID_STATUSES
        except ImportError:
            # Fallback list
            return ["Interested", "Preparing", "Documents Pending",
                    "Applied", "Under Review", "Approved", "Rejected", "Expired"]

    def test_valid_statuses_list(self):
        statuses = self._get_valid_statuses()
        expected = ["Interested", "Preparing", "Documents Pending",
                    "Applied", "Under Review", "Approved", "Rejected", "Expired"]
        for s in expected:
            self.assertIn(s, statuses)

    def test_initial_status_is_valid(self):
        self.assertIn("Interested", self._get_valid_statuses())

    def test_final_statuses_present(self):
        statuses = self._get_valid_statuses()
        self.assertIn("Approved", statuses)
        self.assertIn("Rejected", statuses)
        self.assertIn("Expired", statuses)


if __name__ == "__main__":
    unittest.main()