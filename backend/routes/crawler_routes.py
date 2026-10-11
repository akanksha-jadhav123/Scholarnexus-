"""
Protected API endpoints to trigger and monitor sync operations.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime
from database import db
from services.scholarship_sync import ScholarshipSync
from scraper.source_config import SOURCES, get_enabled_sources
from middleware.rate_limit import rate_limit

crawler_bp = Blueprint("crawler", __name__)

_last_sync = {"at": None, "stats": None}


def is_admin():
    return get_jwt().get("role") == "admin"


@crawler_bp.route("/sources", methods=["GET"])
def list_sources():
    """Return list of source metadata — array only (frontend-safe)."""
    out = []
    for s in SOURCES:
        out.append({
            "name": s["name"],
            "url": s["base_url"],           # frontend expects 'url'
            "type": s.get("type", "Unknown"),
            "trust_score": s.get("trust_score", 5),
            "delay_seconds": 2,             # default
            "enabled": s.get("enabled", True),
        })
    return jsonify(out), 200


@crawler_bp.route("/stats", methods=["GET"])
def get_stats():
    source_counts = {}
    for sc in db.Scholarships.find({}, {"source": 1}):
        s = sc.get("source") or "unknown"
        source_counts[s] = source_counts.get(s, 0) + 1

    return jsonify({
        "db_total": db.Scholarships.count_documents({}),
        "by_source": source_counts,
        "by_category": _category_counts(),
        "last_sync": _last_sync,        # {at, stats:{crawled,saved,duplicates,rejected}}
    }), 200


def _category_counts():
    counts = {}
    for sc in db.Scholarships.find({}, {"category": 1}):
        c = sc.get("category") or "Unknown"
        counts[c] = counts.get(c, 0) + 1
    return counts


@crawler_bp.route("/sync", methods=["POST"])
@jwt_required()
def trigger_sync():
    if not is_admin():
        return jsonify({"error": "Admin only"}), 403

    sync = ScholarshipSync(db=db)
    result = sync.run()

    # Alias fields for frontend compatibility
    result["total_crawled"] = result.get("crawled", 0)
    result["total_saved"] = result.get("saved", 0)
    result["total_duplicates"] = result.get("duplicates", 0)
    result["total_rejected"] = result.get("rejected", 0)

    _last_sync["at"] = datetime.utcnow().isoformat()
    _last_sync["stats"] = result

    return jsonify({"message": "Sync complete", "stats": result}), 200