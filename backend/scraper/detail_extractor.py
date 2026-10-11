import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ScholarshipDetailExtractor:

    @staticmethod
    def clean_text(value):
        if not value:
            return None

        value = re.sub(
            r"\s+",
            " ",
            str(value)
        ).strip()

        return value if value else None


    @staticmethod
    def extract_amount(text):
        if not text:
            return None

        patterns = [
            r"(?:₹|INR|Rs\.?)\s?[\d,]+(?:\.\d+)?",
            r"[\d,]+(?:\.\d+)?\s?(?:INR|USD|\$|rupees)",
            r"(?:up to|worth|value of)\s+(?:₹|INR|Rs\.?)?\s?[\d,]+",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                return match.group(0).strip()

        return None


    @staticmethod
    def extract_percentage(text):
        if not text:
            return None

        patterns = [
            r"(?:minimum|min\.?|at least)\s*(\d+(?:\.\d+)?)\s*%",
            r"(\d+(?:\.\d+)?)\s*%\s*(?:or above|and above)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                try:
                    return float(match.group(1))
                except Exception:
                    pass

        return None


    @staticmethod
    def extract_income(text):
        if not text:
            return None

        patterns = [
            r"(?:family|annual|household)\s+income.*?(?:₹|INR|Rs\.?)\s?([\d,]+)",
            r"(?:income).*?(?:₹|INR|Rs\.?)\s?([\d,]+)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                try:
                    return float(
                        match.group(1)
                        .replace(",", "")
                    )
                except Exception:
                    pass

        return None


    @staticmethod
    def extract_deadline(text):
        if not text:
            return None

        patterns = [

            # 31 December 2026
            r"\b(\d{1,2}\s+"
            r"(?:January|February|March|April|May|June|July|August|"
            r"September|October|November|December)"
            r"\s+\d{4})\b",

            # December 31, 2026
            r"\b((?:January|February|March|April|May|June|July|August|"
            r"September|October|November|December)"
            r"\s+\d{1,2},\s+\d{4})\b",

            # 31/12/2026
            r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b",

            # 2026-12-31
            r"\b(\d{4}-\d{2}-\d{2})\b",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if not match:
                continue

            value = match.group(1)

            formats = [
                "%d %B %Y",
                "%B %d, %Y",
                "%d/%m/%Y",
                "%d-%m-%Y",
                "%Y-%m-%d",
            ]

            for fmt in formats:

                try:
                    return datetime.strptime(
                        value,
                        fmt
                    ).date().isoformat()

                except ValueError:
                    continue

        return None


    @staticmethod
    def extract_course(text):
        if not text:
            return None

        courses = [
            "B.Tech",
            "B.E.",
            "Bachelor of Technology",
            "Engineering",
            "B.Sc",
            "B.Com",
            "B.A.",
            "BBA",
            "BCA",
            "MBA",
            "M.Tech",
            "M.E.",
            "M.Sc",
            "M.Com",
            "PhD",
            "Doctoral",
            "Postgraduate",
            "Undergraduate",
        ]

        found = []

        for course in courses:

            if re.search(
                re.escape(course),
                text,
                re.IGNORECASE
            ):
                found.append(course)

        if found:
            return list(dict.fromkeys(found))

        return None


    @staticmethod
    def extract_state(text):
        if not text:
            return None

        states = [
            "Maharashtra",
            "Karnataka",
            "Tamil Nadu",
            "Gujarat",
            "Uttar Pradesh",
            "Madhya Pradesh",
            "Rajasthan",
            "West Bengal",
            "Telangana",
            "Andhra Pradesh",
            "Kerala",
            "Delhi",
            "Bihar",
            "Odisha",
            "Punjab",
            "Haryana",
            "Goa",
            "Jharkhand",
            "Chhattisgarh",
            "Assam",
            "International",
        ]

        found = []

        for state in states:

            if re.search(
                re.escape(state),
                text,
                re.IGNORECASE
            ):
                found.append(state)

        if found:
            return list(dict.fromkeys(found))

        return None


    @classmethod
    def extract(cls, soup):

        # Get complete visible page text
        text = soup.get_text(
            " ",
            strip=True
        )

        text = cls.clean_text(text)

        return {
            "scholarship_amount":
                cls.extract_amount(text),

            "application_deadline":
                cls.extract_deadline(text),

            "minimum_percentage":
                cls.extract_percentage(text),

            "max_family_income":
                cls.extract_income(text),

            "eligible_courses":
                cls.extract_course(text) or [],

            "eligible_states":
                cls.extract_state(text) or [],

            "eligibility_description":
                text[:2000] if text else None,
        }