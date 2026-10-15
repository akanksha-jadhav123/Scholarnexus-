"""
Admin manual scholarship entry — POST /api/admin/scholarships

Wraps the existing Normalizer + Validator so manually-entered records
match the exact schema produced by the scraper pipeline.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime
from bson import ObjectId

from database import db
from scraper.normalizer import Normalizer
from scraper.validator import Validator

manual_bp = Blueprint("manual", __name__)


def _is_admin():
    return get_jwt().get("role") == "admin"


def _missing(required, data):
    """Return list of field names that are missing or empty."""
    return [f for f in required if data.get(f) in (None, "", [])]


@manual_bp.route("/scholarships", methods=["POST", "OPTIONS"])
@jwt_required()
def create_scholarship():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    if not _is_admin():
        return jsonify({"error": "Admin only"}), 403

    data = request.get_json(silent=True) or {}

    # ---------- REQUIRED FIELDS ----------
    required = [
        "scholarship_id",
        "scholarship_name",
        "provider",
        "application_deadline",
    ]
    missing = _missing(required, data)
    if missing:
        return jsonify({
            "error": f"Missing required fields: {', '.join(missing)}",
            "missing": missing,
        }), 400

    # ---------- DUPLICATE CHECK ----------
    if db.Scholarships.find_one({"scholarship_id": data["scholarship_id"]}):
        return jsonify({
            "error": f"Scholarship ID '{data['scholarship_id']}' already exists",
        }), 409

    # ---------- COERCE NUMERIC FIELDS ----------
    numeric_fields = [
        "scholarship_amount",
        "amount_min",
        "amount_max",
        "minimum_percentage",
        "max_family_income",
    ]
    for field in numeric_fields:
        val = data.get(field)
        if val in (None, ""):
            data[field] = None
            continue
        try:
            data[field] = float(val)
        except (ValueError, TypeError):
            return jsonify({
                "error": f"Field '{field}' must be a number",
                "got": val,
            }), 400

    # ---------- VALIDATE PERCENTAGE RANGE ----------
    pct = data.get("minimum_percentage")
    if pct is not None and not (0 <= pct <= 100):
        return jsonify({
            "error": "minimum_percentage must be between 0 and 100",
        }), 400

    income = data.get("max_family_income")
    if income is not None and income < 0:
        return jsonify({
            "error": "max_family_income must be positive",
        }), 400

    amount = data.get("scholarship_amount")
    if amount is not None and amount < 0:
        return jsonify({
            "error": "scholarship_amount must be positive",
        }), 400

    # ---------- VALIDATE URL FORMAT ----------
    for url_field in ("application_url", "official_source"):
        url = data.get(url_field)
        if url and not url.startswith(("http://", "https://")):
            return jsonify({
                "error": f"{url_field} must start with http:// or https://",
            }), 400

    # ---------- HANDLE required_documents ----------
    docs = data.get("required_documents")
    if isinstance(docs, str):
        docs = [d.strip() for d in docs.split(",") if d.strip()]
    elif not isinstance(docs, list):
        docs = []
    data["required_documents"] = docs

    # ---------- SOURCE TRACKING ----------
    data.setdefault("source", "manual")
    data.setdefault("source_type", "Manual")
    data.setdefault("source_trust_score", 9)   # high — admin entered
    data.setdefault("status", "Active")
    data.setdefault("link_status", "pending")
    data.setdefault("official_source", data.get("application_url") or "")

    # ---------- NORMALIZE (same schema as scraper) ----------
    try:
        normalized = Normalizer.normalize(data)
    except Exception as e:
        return jsonify({
            "error": f"Normalization failed: {str(e)}",
        }), 500

    # Preserve the admin-chosen scholarship_id (normalizer may regenerate)
    normalized["scholarship_id"] = data["scholarship_id"]

    # ---------- VALIDATE (same rules as scraper) ----------
    is_valid, errors = Validator.validate(normalized)
    if not is_valid:
        return jsonify({
            "error": "Validation failed",
            "errors": errors,
        }), 400

    # ---------- MARK AS VERIFIED ----------
    normalized["verified"] = True
    normalized["verified_at"] = datetime.utcnow()
    normalized["verified_by"] = "admin_manual"

    # ---------- SAVE ----------
    try:
        result = db.Scholarships.insert_one(normalized)
        return jsonify({
            "message": "Scholarship created",
            "scholarship_id": normalized["scholarship_id"],
            "_id": str(result.inserted_id),
        }), 201
    except Exception as e:
        return jsonify({
            "error": f"Failed to save: {str(e)}",
        }), 500


@manual_bp.route("/scholarships/<scholarship_id>", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_scholarship(scholarship_id):
    """Admin-only update — more permissive than the scraper upsert."""
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    if not _is_admin():
        return jsonify({"error": "Admin only"}), 403

    data = request.get_json(silent=True) or {}
    data.pop("_id", None)             # never allow _id overwrite
    data.pop("scholarship_id", None)  # don't allow ID change

    # Coerce numerics if present
    for field in ["scholarship_amount", "amount_min", "amount_max",
                  "minimum_percentage", "max_family_income"]:
        if field in data and data[field] not in (None, ""):
            try:
                data[field] = float(data[field])
            except (ValueError, TypeError):
                return jsonify({"error": f"{field} must be numeric"}), 400

    if "required_documents" in data and isinstance(data["required_documents"], str):
        data["required_documents"] = [
            d.strip() for d in data["required_documents"].split(",") if d.strip()
        ]

    data["last_updated"] = datetime.utcnow().isoformat()
    data["updated_by"] = "admin_manual"

    result = db.Scholarships.update_one(
        {"scholarship_id": scholarship_id},
        {"$set": data},
    )

    if result.matched_count == 0:
        return jsonify({"error": "Scholarship not found"}), 404

    return jsonify({
        "message": "Scholarship updated",
        "scholarship_id": scholarship_id,
        "modified": result.modified_count,
    }), 200


@manual_bp.route("/scholarships/<scholarship_id>", methods=["DELETE", "OPTIONS"])
@jwt_required()
def delete_scholarship(scholarship_id):
    """Hard delete — use with caution. Admin-only."""
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    if not _is_admin():
        return jsonify({"error": "Admin only"}), 403

    result = db.Scholarships.delete_one({"scholarship_id": scholarship_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Scholarship not found"}), 404

    return jsonify({
        "message": "Scholarship deleted",
        "scholarship_id": scholarship_id,
    }), 200