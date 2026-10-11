"""Unit tests for scraper/extractors.py"""
import unittest
from scraper.extractors import ScholarshipExtractor


class TestExtractors(unittest.TestCase):

    def test_extract_amount_rupees(self):
        self.assertEqual(ScholarshipExtractor.extract_amount("₹50,000"), 50000)

    def test_extract_amount_lakh(self):
        self.assertEqual(ScholarshipExtractor.extract_amount("Rs 5 lakh"), 500000)

    def test_extract_amount_crore(self):
        self.assertEqual(ScholarshipExtractor.extract_amount("₹1.5 crore"), 15000000)

    def test_extract_amount_empty(self):
        self.assertIsNone(ScholarshipExtractor.extract_amount(""))

    def test_extract_deadline_dash(self):
        self.assertEqual(ScholarshipExtractor.extract_deadline("Apply by 31-12-2026"), "31-12-2026")

    def test_extract_deadline_slash(self):
        self.assertEqual(ScholarshipExtractor.extract_deadline("Deadline: 15/03/2026"), "15/03/2026")

    def test_extract_from_html(self):
        html = '<a href="/scholarship/abc">National Merit Scholarship for Students</a>'
        results = ScholarshipExtractor.extract_from_html(html)
        self.assertEqual(len(results), 1)
        self.assertIn("National Merit", results[0]["scholarship_name"])


if __name__ == "__main__":
    unittest.main()