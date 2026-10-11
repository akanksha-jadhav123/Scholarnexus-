"""Unit tests for scraper/deduplicator.py (uses in-memory mock)"""
import unittest
from scraper.deduplicator import Deduplicator


class MockCollection:
    def __init__(self, records=None):
        self.records = records or []

    def find_one(self, query):
        for r in self.records:
            if self._matches(r, query):
                return r
        return None

    def _matches(self, record, query):
        for k, v in query.items():
            if isinstance(v, dict) and "$regex" in v:
                import re
                pattern = v["$regex"]
                flags = re.I if "i" in v.get("$options", "") else 0
                if not re.match(pattern, str(record.get(k, "")), flags):
                    return False
            else:
                if record.get(k) != v:
                    return False
        return True


class MockDB:
    def __init__(self, scholarships=None):
        self.Scholarships = MockCollection(scholarships)


class TestDeduplicator(unittest.TestCase):

    def test_no_duplicate_empty_db(self):
        db = MockDB([])
        record = {"scholarship_name": "Test", "provider": "X", "application_url": "https://a.com"}
        self.assertFalse(Deduplicator.is_duplicate(db, record))

    def test_duplicate_by_id(self):
        db = MockDB([{"scholarship_id": "SCH001"}])
        record = {"scholarship_id": "SCH001", "scholarship_name": "X", "application_url": "https://a.com"}
        self.assertTrue(Deduplicator.is_duplicate(db, record))

    def test_duplicate_by_url(self):
        db = MockDB([{"application_url": "https://a.com"}])
        record = {"scholarship_name": "Test", "provider": "X", "application_url": "https://a.com"}
        self.assertTrue(Deduplicator.is_duplicate(db, record))

    def test_case_insensitive_name(self):
        db = MockDB([{"scholarship_name": "National Merit", "provider": "GOI"}])
        record = {"scholarship_name": "national merit", "provider": "goi", "application_url": "https://x.com"}
        self.assertTrue(Deduplicator.is_duplicate(db, record))


if __name__ == "__main__":
    unittest.main()