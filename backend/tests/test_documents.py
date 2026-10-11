import unittest


class TestDocuments(unittest.TestCase):

    def test_document_status_values(self):
        valid = ["pending", "completed"]
        self.assertIn("pending", valid)
        self.assertIn("completed", valid)

    def test_checklist_completion_calculation(self):
        checklist = [
            {"document_name": "Aadhaar", "status": "completed"},
            {"document_name": "Marksheet", "status": "completed"},
            {"document_name": "Income Cert", "status": "pending"},
        ]
        completed = sum(1 for c in checklist if c["status"] == "completed")
        total = len(checklist)
        pct = int((completed / total) * 100)
        self.assertEqual(completed, 2)
        self.assertEqual(total, 3)
        self.assertEqual(pct, 66)


if __name__ == "__main__":
    unittest.main()