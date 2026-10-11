"""
Validates application URLs before saving.
Checks HTTP status and marks links as active / broken / pending.
"""
import time
import logging
import requests

logger = logging.getLogger(__name__)


class LinkValidator:

    def __init__(self, delay=1, timeout=10):
        self.delay = delay
        self.timeout = timeout
        self.headers = {
            "User-Agent": "ScholarNexusBot/1.0 (Educational Project)"
        }

    def validate(self, url):
        """Return dict: {status, http_code, error}."""
        if not url or not url.startswith("http"):
            return {"status": "invalid", "http_code": None, "error": "Not a valid URL"}

        try:
            time.sleep(self.delay)
            # Try HEAD first (faster)
            resp = requests.head(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)

            # Some servers block HEAD — retry with GET
            if resp.status_code == 405:
                resp = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)

            if 200 <= resp.status_code < 400:
                return {"status": "active", "http_code": resp.status_code, "error": None}
            elif resp.status_code == 404:
                return {"status": "broken", "http_code": 404, "error": "Not found"}
            else:
                return {"status": "broken", "http_code": resp.status_code, "error": f"HTTP {resp.status_code}"}

        except requests.exceptions.Timeout:
            return {"status": "pending", "http_code": None, "error": "Timeout"}
        except requests.exceptions.SSLError:
            return {"status": "broken", "http_code": None, "error": "SSL error"}
        except Exception as e:
            return {"status": "pending", "http_code": None, "error": str(e)[:100]}