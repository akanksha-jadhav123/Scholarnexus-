"""
Configuration for all permitted scholarship sources.
Each source has:
  - name: identifier
  - base_url: root URL
  - type: National / State / Aggregator / NGO / Corporate / International
  - trust_score: 1-10 (used for ranking scraped data)
  - enabled: bool
  - crawl_patterns: URL patterns to discover scholarship pages
"""

SOURCES = [
    {
        "name": "scholarships.gov.in",
        "base_url": "https://scholarships.gov.in",
        "type": "National",
        "trust_score": 10,
        "enabled": True,
        "crawl_patterns": [
            "/scheme",
            "/scholarship",
            "/all-scheme"
        ]
    },
    {
        "name": "nsdl.co.in",
        "base_url": "https://www.nsdl.co.in",
        "type": "Government",
        "trust_score": 9,
        "enabled": True,
        "crawl_patterns": ["/scholarship"]
    },
    {
        "name": "mahadbt.maharashtra.gov.in",
        "base_url": "https://mahadbt.maharashtra.gov.in",
        "type": "State",
        "trust_score": 9,
        "enabled": True,
        "crawl_patterns": ["/SchemeData", "/Scheme"]
    },
    {
        "name": "buddy4study.com",
        "base_url": "https://www.buddy4study.com",
        "type": "Aggregator",
        "trust_score": 7,
        "enabled": True,
        "crawl_patterns": ["/scholarships", "/scholarship/"]
    },
    {
        "name": "scholarshipsindia.org",
        "base_url": "https://www.scholarshipsindia.org",
        "type": "Aggregator",
        "trust_score": 7,
        "enabled": True,
        "crawl_patterns": ["/scholarship"]
    },
    {
        "name": "vidyasaarathi.co.in",
        "base_url": "https://www.vidyasaarathi.co.in",
        "type": "Aggregator",
        "trust_score": 9,
        "enabled": True,
        "crawl_patterns": ["/Vidyasaarathi/scholarships"]
    },
    {
        "name": "wemakescholars.com",
        "base_url": "https://www.wemakescholars.com",
        "type": "Aggregator",
        "trust_score": 7,
        "enabled": True,
        "crawl_patterns": ["/scholarship"]
    },
    {
        "name": "scholarshipportal.com",
        "base_url": "https://www.scholarshipportal.com",
        "type": "International",
        "trust_score": 7,
        "enabled": True,
        "crawl_patterns": ["/scholarships/india"]
    },
    {
        "name": "sitaramjindalfoundation.org",
        "base_url": "https://www.sitaramjindalfoundation.org",
        "type": "NGO",
        "trust_score": 8,
        "enabled": True,
        "crawl_patterns": ["/scholarship"]
    },
    {
        "name": "reliancefoundation.org",
        "base_url": "https://www.reliancefoundation.org",
        "type": "Corporate",
        "trust_score": 9,
        "enabled": True,
        "crawl_patterns": ["/scholarships"]
    },
        {
        "name": "scholarshipsads.com",
        "base_url": "https://www.scholarshipsads.com",
        "type": "Aggregator",
        "trust_score": 6,
        "enabled": True,
        "crawl_patterns": ["/"]
    },
    {
        "name": "scholarshiproar.com",
        "base_url": "https://scholarshiproar.com/scholarships/",
        "type": "Aggregator",
        "trust_score": 6,
        "enabled": True,
        "crawl_patterns": ["/scholarships/"]
    },
    {
        "name": "indiascholarship.com",
        "base_url": "https://www.indiascholarship.com",
        "type": "Aggregator",
        "trust_score": 6,
        "enabled": True,
        "crawl_patterns": ["/"]
    },
    {
        "name": "aicte-india.org",
        "base_url": "https://www.aicte-india.org/schemes/students-development-schemes",
        "type": "Government",
        "trust_score": 10,
        "enabled": True,
        "crawl_patterns": ["/schemes"]
    },
    {
        "name": "ugc.gov.in",
        "base_url": "https://www.ugc.gov.in/scholarship",
        "type": "Government",
        "trust_score": 10,
        "enabled": True,
        "crawl_patterns": ["/scholarship"]
    },
]


def get_enabled_sources():
    return [s for s in SOURCES if s.get("enabled")]


def get_source(name):
    for s in SOURCES:
        if s["name"] == name:
            return s
    return None