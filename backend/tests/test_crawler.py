import unittest
from scraper.crawler import SCRAPER_CLASSES, Crawler


class TestCrawler(unittest.TestCase):

    def test_scraper_classes_loaded(self):
        self.assertGreater(len(SCRAPER_CLASSES), 0)

    def test_crawler_init(self):
        c = Crawler(max_workers=3)
        self.assertEqual(c.max_workers, 3)

    def test_crawler_default_workers(self):
        c = Crawler()
        self.assertEqual(c.max_workers, 5)


if __name__ == "__main__":
    unittest.main()