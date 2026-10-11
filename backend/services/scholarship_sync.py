"""
ScholarNexus Scholarship Sync

Coordinates the complete scholarship data pipeline:

Crawl
  ↓
Normalize
  ↓
Validate
  ↓
Find existing record
  ↓
Update existing record OR insert new record
  ↓
Return sync statistics
"""

import logging
from datetime import datetime

from scraper.crawler import Crawler
from scraper.normalizer import Normalizer
from scraper.validator import Validator


logger = logging.getLogger(__name__)


class ScholarshipSync:

    def __init__(self, db):
        self.db = db

    # ============================================================
    # MAIN SYNC FUNCTION
    # ============================================================

    def run(self):

        stats = {
            "started_at": datetime.utcnow().isoformat(),

            "crawled": 0,
            "validated": 0,

            "updated": 0,
            "inserted": 0,

            "duplicates": 0,
            "rejected": 0,

            "sources": [],
            "errors": []
        }

        # ========================================================
        # STEP 1 — CRAWL
        # ========================================================

        try:

            logger.info(
                "[Sync] Starting scholarship crawler..."
            )

            crawler = Crawler(
                max_workers=5
            )

            result = crawler.crawl()

            # Crawler may return:
            #
            # (raw_records, source_stats)
            #
            # OR
            #
            # raw_records

            if isinstance(result, tuple):

                raw_records = result[0]

                if len(result) > 1:
                    source_stats = result[1]
                else:
                    source_stats = []

            else:

                raw_records = result
                source_stats = []

            if raw_records is None:
                raw_records = []

            stats["crawled"] = len(
                raw_records
            )

            stats["sources"] = source_stats

            logger.info(
                f"[Sync] Crawled "
                f"{len(raw_records)} records"
            )

        except Exception as e:

            logger.exception(
                "[Sync] Fatal crawler error"
            )

            stats["errors"].append(
                f"Crawler error: {str(e)}"
            )

            stats["ended_at"] = (
                datetime.utcnow().isoformat()
            )

            stats["db_total"] = (
                self.db.Scholarships.count_documents({})
            )

            return stats

        # ========================================================
        # STEP 2 — NORMALIZE
        # ========================================================

        for index, raw in enumerate(raw_records):

            try:

                if not isinstance(raw, dict):

                    logger.warning(
                        f"[Sync] Skipping invalid "
                        f"record #{index + 1}"
                    )

                    stats["rejected"] += 1
                    continue

                norm = Normalizer.normalize(
                    raw
                )

                if not norm:

                    stats["rejected"] += 1

                    logger.warning(
                        f"[Sync] Normalizer returned "
                        f"empty record #{index + 1}"
                    )

                    continue

                # =================================================
                # STEP 3 — VALIDATE
                # =================================================

                is_valid, errors = (
                    Validator.validate(norm)
                )

                if not is_valid:

                    stats["rejected"] += 1

                    scholarship_name = (
                        norm.get(
                            "scholarship_name",
                            "Unknown scholarship"
                        )
                    )

                    logger.warning(
                        "[Sync] Rejected scholarship: "
                        f"{scholarship_name}"
                    )

                    if errors:

                        logger.warning(
                            f"[Sync] Validation errors: "
                            f"{errors}"
                        )

                    continue

                stats["validated"] += 1

                # =================================================
                # STEP 4 — FIND EXISTING RECORD
                # =================================================

                existing = self._find_existing(
                    norm
                )

                # =================================================
                # STEP 5 — UPDATE EXISTING
                # =================================================

                if existing:

                    update_data = (
                        self._build_update_data(
                            norm,
                            existing
                        )
                    )

                    if update_data:

                        self.db.Scholarships.update_one(
                            {
                                "_id":
                                    existing["_id"]
                            },
                            {
                                "$set":
                                    update_data
                            }
                        )

                        stats["updated"] += 1

                        logger.info(
                            "[Sync] Updated: "
                            f"{norm.get('scholarship_name')}"
                        )

                    else:

                        stats["duplicates"] += 1

                        logger.info(
                            "[Sync] No new data: "
                            f"{norm.get('scholarship_name')}"
                        )

                    continue

                # =================================================
                # STEP 6 — INSERT NEW RECORD
                # =================================================

                self.db.Scholarships.insert_one(
                    norm
                )

                stats["inserted"] += 1

                logger.info(
                    "[Sync] Inserted: "
                    f"{norm.get('scholarship_name')}"
                )

            except Exception as e:

                scholarship_name = "Unknown"

                if isinstance(raw, dict):

                    scholarship_name = raw.get(
                        "scholarship_name",
                        "Unknown"
                    )

                error_message = (
                    f"{scholarship_name}: "
                    f"{str(e)[:300]}"
                )

                stats["errors"].append(
                    error_message
                )

                logger.exception(
                    f"[Sync] Error processing "
                    f"record #{index + 1}"
                )

        # ========================================================
        # STEP 7 — FINAL STATISTICS
        # ========================================================

        stats["ended_at"] = (
            datetime.utcnow().isoformat()
        )

        stats["db_total"] = (
            self.db.Scholarships.count_documents({})
        )

        logger.info(
            "[Sync] Complete | "
            f"Crawled={stats['crawled']} | "
            f"Validated={stats['validated']} | "
            f"Inserted={stats['inserted']} | "
            f"Updated={stats['updated']} | "
            f"Duplicates={stats['duplicates']} | "
            f"Rejected={stats['rejected']} | "
            f"DB Total={stats['db_total']}"
        )

        return stats

    # ============================================================
    # FIND EXISTING SCHOLARSHIP
    # ============================================================

    def _find_existing(self, scholarship):
        """
        Find an existing scholarship safely.

        IMPORTANT:
        We do NOT query with:

            scholarship_id = None

        or:

            application_url = None

        because that could match unrelated documents.
        """

        scholarship_id = scholarship.get(
            "scholarship_id"
        )

        application_url = scholarship.get(
            "application_url"
        )

        scholarship_name = scholarship.get(
            "scholarship_name"
        )

        provider = scholarship.get(
            "provider"
        )

        # --------------------------------------------------------
        # 1. Match by scholarship_id
        # --------------------------------------------------------

        if scholarship_id:

            existing = (
                self.db.Scholarships.find_one(
                    {
                        "scholarship_id":
                            scholarship_id
                    }
                )
            )

            if existing:
                return existing

        # --------------------------------------------------------
        # 2. Match by application URL
        # --------------------------------------------------------

        if application_url:

            existing = (
                self.db.Scholarships.find_one(
                    {
                        "application_url":
                            application_url
                    }
                )
            )

            if existing:
                return existing

        # --------------------------------------------------------
        # 3. Match by source URL
        # --------------------------------------------------------

        source_url = scholarship.get(
            "source_url"
        )

        if source_url:

            existing = (
                self.db.Scholarships.find_one(
                    {
                        "source_url":
                            source_url
                    }
                )
            )

            if existing:
                return existing

        # --------------------------------------------------------
        # 4. Match by scholarship name + provider
        #
        # This helps update old records which don't have
        # scholarship_id/application_url.
        # --------------------------------------------------------

        if scholarship_name and provider:

            existing = (
                self.db.Scholarships.find_one(
                    {
                        "scholarship_name":
                            scholarship_name,
                        "provider":
                            provider
                    }
                )
            )

            if existing:
                return existing

        # --------------------------------------------------------
        # Nothing found
        # --------------------------------------------------------

        return None

    # ============================================================
    # BUILD UPDATE DATA
    # ============================================================

    def _build_update_data(
        self,
        new_data,
        existing
    ):
        """
        Build a safe MongoDB $set object.

        Important rule:

        New empty values must NOT overwrite useful
        existing values.

        Example:

        Existing:
            amount = 50000

        New scraper:
            amount = None

        Result:
            amount remains 50000
        """

        update_data = {}

        for key, new_value in new_data.items():

            # ----------------------------------------------------
            # Ignore None
            # ----------------------------------------------------

            if new_value is None:
                continue

            # ----------------------------------------------------
            # Ignore empty strings
            # ----------------------------------------------------

            if isinstance(
                new_value,
                str
            ):

                if not new_value.strip():
                    continue

            # ----------------------------------------------------
            # Ignore empty lists
            # ----------------------------------------------------

            if isinstance(
                new_value,
                list
            ):

                if len(new_value) == 0:
                    continue

            # ----------------------------------------------------
            # Check existing value
            # ----------------------------------------------------

            old_value = existing.get(
                key
            )

            # ----------------------------------------------------
            # Add new value
            # ----------------------------------------------------

            if new_value != old_value:

                update_data[key] = new_value

        # --------------------------------------------------------
        # Always refresh last_updated if actual data changed.
        # --------------------------------------------------------

        if update_data:

            update_data["last_updated"] = (
                datetime.utcnow()
            )

        return update_data