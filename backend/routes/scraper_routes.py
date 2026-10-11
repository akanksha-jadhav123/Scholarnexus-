"""
DEPRECATED — This file is kept for backward compatibility only.
Use /api/crawler/* endpoints instead.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime
from database import db
from services.scholarship_sync import ScholarshipSync
from scraper.source_config import SOURCES, get_enabled_sources

scraper_bp = Blueprint("scraper", __name__)

_last_sync = {"at": None, "stats": None}


def is_admin():
    return get_jwt().get("role") == "admin"


@scraper_bp.route("/sources", methods=["GET"])
def list_sources():
    return jsonify({
        "all": SOURCES,
        "enabled": [s["name"] for s in get_enabled_sources()],
        "total": len(SOURCES)
    }), 200


@scraper_bp.route("/stats", methods=["GET"])
def stats():
    source_counts = {}
    for sc in db.Scholarships.find({}, {"source": 1}):
        s = sc.get("source") or "unknown"
        source_counts[s] = source_counts.get(s, 0) + 1

    return jsonify({
        "db_total": db.Scholarships.count_documents({}),
        "active": db.Scholarships.count_documents({"status": "Active"}),
        "auto_scraped": db.Scholarships.count_documents({"scholarship_id": {"$regex": "^AUTO"}}),
        "link_stats": {
            "active": db.Scholarships.count_documents({"link_status": "active"}),
            "broken": db.Scholarships.count_documents({"link_status": "broken"}),
            "pending": db.Scholarships.count_documents({"link_status": "pending"}),
        },
        "by_source": source_counts,
        "sources_registered": len(SOURCES),
        "last_run": _last_sync
    }), 200


@scraper_bp.route("/run", methods=["POST"])
@jwt_required()
def run_now():
    """DEPRECATED — forwards to the unified sync service."""
    if not is_admin():
        return jsonify({"error": "Admin only"}), 403

    sync = ScholarshipSync(db=db)
    result = sync.run()

    _last_sync["at"] = datetime.utcnow().isoformat()
    _last_sync["stats"] = result

    return jsonify({
        "message": "Sync completed (via unified pipeline)",
        "stats": result,
        "note": "Use POST /api/crawler/sync for the canonical endpoint"
    }), 200