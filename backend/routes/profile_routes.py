from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from database import db

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    profile = db.StudentProfiles.find_one({"user_id": user_id}, {"_id": 0})
    return jsonify(profile or {}), 200


@profile_bp.route("/", methods=["POST", "PUT"])
@jwt_required()
def save_profile():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    required = ["state", "category", "gender", "income", "course", "percentage"]
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        data["income"] = float(data["income"])
        data["percentage"] = float(data["percentage"])
    except (ValueError, TypeError):
        return jsonify({"error": "Income and percentage must be numbers"}), 400

    if not (0 <= data["percentage"] <= 100):
        return jsonify({"error": "Percentage must be between 0 and 100"}), 400
    if data["income"] < 0:
        return jsonify({"error": "Income must be positive"}), 400

    data["user_id"] = user_id
    data["updated_at"] = datetime.utcnow()

    db.StudentProfiles.update_one(
        {"user_id": user_id},
        {"$set": data},
        upsert=True
    )
    return jsonify({"message": "Profile saved successfully"}), 200


@profile_bp.route("/completion", methods=["GET"])
@jwt_required()
def completion():
    user_id = get_jwt_identity()
    profile = db.StudentProfiles.find_one({"user_id": user_id}) or {}
    fields = ["state", "category", "gender", "income", "course",
              "branch", "year", "percentage", "college"]
    filled = sum(1 for f in fields if profile.get(f) not in (None, ""))
    percent = int((filled / len(fields)) * 100)
    return jsonify({
        "completion": percent,
        "filled": filled,
        "total": len(fields)
    }), 200