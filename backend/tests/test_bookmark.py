"""
Tests bookmark logic — uses an in-memory mock DB.
"""
import unittest


class MockCollection:
    def __init__(self):
        self.records = []

    def find_one(self, query):
        for r in self.records:
            if all(r.get(k) == v for k, v in query.items() if not isinstance(v, dict)):
                return r
        return None

    def update_one(self, query, update, upsert=False):
        record = self.find_one(query)
        if not record and upsert:
            record = dict(query)
            self.records.append(record)

        if record and "$addToSet" in update:
            for k, v in update["$addToSet"].items():
                if k not in record:
                    record[k] = []
                if v not in record[k]:
                    record[k].append(v)

        if record and "$pull" in update:
            for k, v in update["$pull"].items():
                if k in record and isinstance(record[k], list):
                    record[k] = [x for x in record[k] if x != v]

        return MagicMockResult(record is not None)


class MagicMockResult:
    def __init__(self, matched):
        self.matched_count = 1 if matched else 0


class TestBookmark(unittest.TestCase):

    def test_add_bookmark(self):
        col = MockCollection()
        col.records.append({"_id": "u1", "bookmarks": []})
        col.update_one({"_id": "u1"}, {"$addToSet": {"bookmarks": "SCH001"}})
        self.assertIn("SCH001", col.records[0]["bookmarks"])

    def test_remove_bookmark(self):
        col = MockCollection()
        col.records.append({"_id": "u1", "bookmarks": ["SCH001"]})
        col.update_one({"_id": "u1"}, {"$pull": {"bookmarks": "SCH001"}})
        self.assertNotIn("SCH001", col.records[0]["bookmarks"])

    def test_no_duplicate_bookmark(self):
        col = MockCollection()
        col.records.append({"_id": "u1", "bookmarks": ["SCH001"]})
        col.update_one({"_id": "u1"}, {"$addToSet": {"bookmarks": "SCH001"}})
        self.assertEqual(len(col.records[0]["bookmarks"]), 1)


if __name__ == "__main__":
    unittest.main()