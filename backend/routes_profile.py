from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from database import get_db

profile_bp = Blueprint("profile", __name__)

def profiles_col():
    return get_db()["profiles"]


REQUIRED_FIELDS = [
    "full_name", "phone", "state", "category", "gender",
    "annual_income", "course", "percentage"
]


@profile_bp.route("/api/profile/", methods=["GET", "POST", "OPTIONS"])
@jwt_required(optional=True)
def profile():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    
    user_id = get_jwt_identity()
    print(f"📥 [PROFILE {request.method}] user_id = {user_id}")
    
    if not user_id:
        return jsonify({"error": "Unauthorized - no token"}), 401
    
    if request.method == "GET":
        doc = profiles_col().find_one({"user_id": user_id}, {"_id": 0})
        return jsonify(doc or {}), 200
    
    # POST
    data = request.get_json(silent=True) or {}
    print(f"📥 [PROFILE POST] data = {data}")
    
    data["user_id"] = user_id
    data["updated_at"] = datetime.now()
    
    for field in ["annual_income", "percentage"]:
        if field in data and data[field] not in (None, ""):
            try:
                data[field] = float(data[field])
            except (ValueError, TypeError):
                pass
    
    result = profiles_col().update_one(
        {"user_id": user_id},
        {"$set": data},
        upsert=True
    )
    print(f"✅ [PROFILE POST] upserted={result.upserted_id} matched={result.matched_count}")
    
    saved = profiles_col().find_one({"user_id": user_id}, {"_id": 0})
    return jsonify({"message": "Profile saved", "profile": saved}), 200


@profile_bp.route("/api/profile/completion", methods=["GET", "OPTIONS"])
@jwt_required(optional=True)
def completion():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    doc = profiles_col().find_one({"user_id": user_id}, {"_id": 0}) or {}
    filled = [f for f in REQUIRED_FIELDS if doc.get(f) not in (None, "", [])]
    percent = int((len(filled) / len(REQUIRED_FIELDS)) * 100)
    
    return jsonify({
        "completion": percent,
        "filled": filled,
        "missing": [f for f in REQUIRED_FIELDS if f not in filled]
    }), 200