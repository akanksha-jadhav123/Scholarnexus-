"""
Application tracking routes.
Statuses: Interested → Preparing → Documents Pending → Applied →
Under Review → Approved / Rejected / Expired
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from database import db

apps_bp = Blueprint("applications", __name__)

VALID_STATUSES = [
    "Interested",
    "Preparing",
    "Documents Pending",
    "Applied",
    "Under Review",
    "Approved",
    "Rejected",
    "Expired"
]


@apps_bp.route("/", methods=["GET"])
@jwt_required()
def list_applications():
    user_id = get_jwt_identity()
    apps = list(db.Applications.find({"user_id": user_id}, {"_id": 0}).sort("updated_at", -1))

    for app in apps:
        sc = db.Scholarships.find_one({"scholarship_id": app["scholarship_id"]}, {"_id": 0})
        if sc:
            app["scholarship_name"] = sc.get("scholarship_name")
            app["provider"] = sc.get("provider")
            app["application_deadline"] = sc.get("application_deadline")
            app["application_url"] = sc.get("application_url")
            app["scholarship_amount"] = sc.get("scholarship_amount")

    return jsonify(apps), 200


@apps_bp.route("/", methods=["POST"])
@jwt_required()
def create_or_update_application():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    sid = data.get("scholarship_id")
    status = data.get("status", "Interested")
    notes = data.get("notes", "")

    if not sid:
        return jsonify({"error": "scholarship_id required"}), 400
    if status not in VALID_STATUSES:
        return jsonify({"error": f"Invalid status. Use: {', '.join(VALID_STATUSES)}"}), 400

    if not db.Scholarships.find_one({"scholarship_id": sid}):
        return jsonify({"error": "Scholarship not found"}), 404

    now = datetime.utcnow()
    db.Applications.update_one(
        {"user_id": user_id, "scholarship_id": sid},
        {
            "$set": {
                "user_id": user_id,
                "scholarship_id": sid,
                "status": status,
                "notes": notes,
                "updated_at": now
            },
            "$setOnInsert": {
                "created_at": now
            }
        },
        upsert=True
    )

    return jsonify({
        "message": "Application saved",
        "scholarship_id": sid,
        "status": status
    }), 200


@apps_bp.route("/<scholarship_id>", methods=["GET"])
@jwt_required()
def get_application(scholarship_id):
    user_id = get_jwt_identity()
    app = db.Applications.find_one(
        {"user_id": user_id, "scholarship_id": scholarship_id},
        {"_id": 0}
    )
    return jsonify(app or {}), 200


@apps_bp.route("/<scholarship_id>", methods=["DELETE"])
@jwt_required()
def delete_application(scholarship_id):
    user_id = get_jwt_identity()
    db.Applications.delete_one({"user_id": user_id, "scholarship_id": scholarship_id})
    return jsonify({"message": "Application removed"}), 200