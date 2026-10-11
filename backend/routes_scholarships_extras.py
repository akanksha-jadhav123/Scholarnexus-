from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from database import get_db, get_scholarship_collection

extras_bp = Blueprint("extras", __name__)

def bookmarks_col():
    return get_db()["bookmarks"]

def profiles_col():
    return get_db()["profiles"]


# ---------- RECOMMENDATIONS ----------
@extras_bp.route("/api/scholarships/recommendations", methods=["GET", "OPTIONS"])
@jwt_required(optional=True)
def recommendations():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    profile = profiles_col().find_one({"user_id": user_id}, {"_id": 0}) or {}
    scholarships = list(get_scholarship_collection().find({}, {"_id": 0}))
    
    scored = []
    for s in scholarships:
        score = 0
        reasons = []
        
        if profile.get("percentage") and s.get("minimum_percentage"):
            if profile["percentage"] >= s["minimum_percentage"]:
                score += 30
                reasons.append("Percentage satisfies requirement")
        
        if profile.get("annual_income") and s.get("max_income"):
            if profile["annual_income"] <= s["max_income"]:
                score += 25
                reasons.append("Income within limit")
        
        if profile.get("course") and s.get("course") and profile["course"] == s["course"]:
            score += 20
            reasons.append("Course matches")
        
        if profile.get("state") and s.get("state") and profile["state"] == s["state"]:
            score += 15
            reasons.append("State eligible")
        
        if profile.get("category") and s.get("category") and profile["category"] == s["category"]:
            score += 10
            reasons.append("Category matches")
        
        s["match_percentage"] = score
        s["match_reasons"] = reasons
        scored.append(s)
    
    scored.sort(key=lambda x: x["match_percentage"], reverse=True)
    return jsonify({"results": scored}), 200


# ---------- ELIGIBILITY ----------
@extras_bp.route("/api/scholarships/<scholarship_id>/eligibility", methods=["GET", "OPTIONS"])
@jwt_required(optional=True)
def eligibility(scholarship_id):
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    profile = profiles_col().find_one({"user_id": user_id}, {"_id": 0}) or {}
    s = get_scholarship_collection().find_one({"scholarship_id": scholarship_id}, {"_id": 0})
    if not s:
        return jsonify({"error": "Scholarship not found"}), 404
    
    checks = []
    eligible = True
    
    if s.get("minimum_percentage"):
        ok = (profile.get("percentage") or 0) >= s["minimum_percentage"]
        checks.append({"criterion": "Minimum Percentage", "required": s["minimum_percentage"], "you": profile.get("percentage"), "passed": ok})
        eligible = eligible and ok
    
    if s.get("max_income"):
        ok = (profile.get("annual_income") or 0) <= s["max_income"]
        checks.append({"criterion": "Max Income", "required": s["max_income"], "you": profile.get("annual_income"), "passed": ok})
        eligible = eligible and ok
    
    return jsonify({"eligible": eligible, "checks": checks}), 200


# ---------- BOOKMARKS ----------
@extras_bp.route("/api/scholarships/bookmark/<scholarship_id>", methods=["POST", "OPTIONS"])
@jwt_required(optional=True)
def toggle_bookmark(scholarship_id):
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    existing = bookmarks_col().find_one({"user_id": user_id, "scholarship_id": scholarship_id})
    
    if existing:
        bookmarks_col().delete_one({"_id": existing["_id"]})
        return jsonify({"bookmarked": False, "message": "Removed"}), 200
    
    bookmarks_col().insert_one({
        "user_id": user_id,
        "scholarship_id": scholarship_id,
        "created_at": datetime.now()
    })
    return jsonify({"bookmarked": True, "message": "Added"}), 200


@extras_bp.route("/api/scholarships/bookmarks", methods=["GET", "OPTIONS"])
@jwt_required(optional=True)
def get_bookmarks():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    marks = list(bookmarks_col().find({"user_id": user_id}, {"_id": 0}))
    ids = [m["scholarship_id"] for m in marks]
    schols = list(get_scholarship_collection().find(
        {"scholarship_id": {"$in": ids}}, {"_id": 0}
    ))
    return jsonify({"results": schols}), 200


# ---------- UPCOMING DEADLINES ----------
@extras_bp.route("/api/scholarships/upcoming-deadlines", methods=["GET", "OPTIONS"])
@jwt_required(optional=True)
def upcoming_deadlines():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    marks = list(bookmarks_col().find({"user_id": user_id}, {"_id": 0}))
    ids = [m["scholarship_id"] for m in marks]
    schols = list(get_scholarship_collection().find(
        {"scholarship_id": {"$in": ids}}, {"_id": 0}
    ).sort("application_deadline", 1))
    return jsonify({"results": schols}), 200


# ---------- COMPARE ----------
@extras_bp.route("/api/scholarships/compare", methods=["POST", "OPTIONS"])
def compare():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    
    data = request.get_json() or {}
    ids = data.get("scholarship_ids", [])
    if not ids:
        return jsonify({"results": []}), 200
    schols = list(get_scholarship_collection().find(
        {"scholarship_id": {"$in": ids}}, {"_id": 0}
    ))
    return jsonify({"results": schols}), 200