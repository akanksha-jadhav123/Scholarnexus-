from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from bson import ObjectId
from datetime import datetime, timedelta
from database import db
from services.eligibility_service import check_eligibility
from services.recommendation_service import recommend_scholarships

sch_bp = Blueprint("scholarships", __name__)


def is_admin():
    return get_jwt().get("role") == "admin"


@sch_bp.route("/", methods=["GET"])
def list_scholarships():
    items = list(db.Scholarships.find({"status": "Active"}, {"_id": 0}).limit(200))
    return jsonify({"count": len(items), "results": items}), 200


@sch_bp.route("/search", methods=["GET"])
def search_scholarships():
    query = {"status": "Active"}
    args = request.args

    if args.get("q"):
        query["$or"] = [
            {"scholarship_name": {"$regex": args["q"], "$options": "i"}},
            {"provider": {"$regex": args["q"], "$options": "i"}},
        ]
    if args.get("course") and args["course"] != "All":
        query["course"] = {"$in": [args["course"], "All"]}
    if args.get("state") and args["state"] != "All":
        query["state"] = {"$in": [args["state"], "All"]}
    if args.get("category") and args["category"] != "All":
        query["category"] = {"$in": [args["category"], "All"]}
    if args.get("gender") and args["gender"] != "All":
        query["gender"] = {"$in": [args["gender"], "All"]}
    if args.get("max_income"):
        try:
            query["max_family_income"] = {"$gte": float(args["max_income"])}
        except ValueError:
            pass
    if args.get("min_percentage"):
        try:
            query["minimum_percentage"] = {"$lte": float(args["min_percentage"])}
        except ValueError:
            pass

    sort_field = args.get("sort_by", "application_deadline")
    sort_order = 1 if args.get("order", "asc") == "asc" else -1

    items = list(
        db.Scholarships.find(query, {"_id": 0})
        .sort(sort_field, sort_order)
        .limit(100)
    )
    return jsonify({"count": len(items), "results": items}), 200


@sch_bp.route("/<sid>", methods=["GET"])
def get_scholarship(sid):
    item = db.Scholarships.find_one({"scholarship_id": sid}, {"_id": 0})
    if not item:
        return jsonify({"error": "Scholarship not found"}), 404
    return jsonify(item), 200


@sch_bp.route("/<sid>/eligibility", methods=["GET"])
@jwt_required()
def eligibility(sid):
    user_id = get_jwt_identity()
    profile = db.StudentProfiles.find_one({"user_id": user_id}) or {}
    if not profile:
        return jsonify({"error": "Complete your profile first"}), 400
    scholarship = db.Scholarships.find_one({"scholarship_id": sid}, {"_id": 0})
    if not scholarship:
        return jsonify({"error": "Scholarship not found"}), 404
    result = check_eligibility(profile, scholarship)
    return jsonify(result), 200


@sch_bp.route("/recommendations", methods=["GET"])
@jwt_required()
def recommendations():
    user_id = get_jwt_identity()
    profile = db.StudentProfiles.find_one({"user_id": user_id}) or {}
    if not profile:
        return jsonify({"error": "Complete your profile first"}), 400
    scholarships = list(db.Scholarships.find({"status": "Active"}, {"_id": 0}))
    results = recommend_scholarships(profile, scholarships)
    return jsonify({
        "count": len(results),
        "recommendations": results[:20]
    }), 200


@sch_bp.route("/compare", methods=["POST"])
@jwt_required()
def compare():
    data = request.get_json() or {}
    ids = data.get("scholarship_ids", [])
    if len(ids) < 2:
        return jsonify({"error": "Provide at least 2 scholarship IDs"}), 400
    items = list(db.Scholarships.find({"scholarship_id": {"$in": ids}}, {"_id": 0}))
    return jsonify(items), 200


@sch_bp.route("/bookmark/<sid>", methods=["POST"])
@jwt_required()
def toggle_bookmark(sid):
    user_id = get_jwt_identity()
    user = db.Users.find_one({"_id": ObjectId(user_id)})
    bookmarks = user.get("bookmarks", [])
    if sid in bookmarks:
        db.Users.update_one({"_id": ObjectId(user_id)}, {"$pull": {"bookmarks": sid}})
        return jsonify({"message": "Removed from bookmarks", "bookmarked": False}), 200
    db.Users.update_one({"_id": ObjectId(user_id)}, {"$addToSet": {"bookmarks": sid}})
    return jsonify({"message": "Bookmarked", "bookmarked": True}), 200


@sch_bp.route("/bookmarks", methods=["GET"])
@jwt_required()
def get_bookmarks():
    user_id = get_jwt_identity()
    user = db.Users.find_one({"_id": ObjectId(user_id)})
    ids = user.get("bookmarks", [])
    items = list(db.Scholarships.find({"scholarship_id": {"$in": ids}}, {"_id": 0}))
    return jsonify(items), 200


@sch_bp.route("/upcoming-deadlines", methods=["GET"])
@jwt_required()
def upcoming_deadlines():
    user_id = get_jwt_identity()
    user = db.Users.find_one({"_id": ObjectId(user_id)})
    bookmarks = user.get("bookmarks", [])
    today = datetime.utcnow().date()
    in_30 = today + timedelta(days=30)

    items = list(
        db.Scholarships.find({
            "scholarship_id": {"$in": bookmarks},
            "status": "Active",
            "application_deadline": {
                "$gte": today.isoformat(),
                "$lte": in_30.isoformat()
            }
        }, {"_id": 0}).sort("application_deadline", 1)
    )
    for item in items:
        try:
            dl = datetime.fromisoformat(item["application_deadline"]).date()
            item["days_left"] = (dl - today).days
        except Exception:
            item["days_left"] = None
    return jsonify(items), 200


# ---------- ADMIN ----------

@sch_bp.route("/", methods=["POST"])
@jwt_required()
def add_scholarship():
    if not is_admin():
        return jsonify({"error": "Admin only"}), 403
    data = request.get_json() or {}
    required = ["scholarship_id", "scholarship_name", "provider", "application_deadline"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing: {', '.join(missing)}"}), 400
    if db.Scholarships.find_one({"scholarship_id": data["scholarship_id"]}):
        return jsonify({"error": "Duplicate scholarship_id"}), 409
    data["last_updated"] = datetime.utcnow().isoformat()
    data.setdefault("status", "Active")
    db.Scholarships.insert_one(data)
    return jsonify({"message": "Scholarship added"}), 201


@sch_bp.route("/<sid>", methods=["PUT"])
@jwt_required()
def update_scholarship(sid):
    if not is_admin():
        return jsonify({"error": "Admin only"}), 403
    data = request.get_json() or {}
    data["last_updated"] = datetime.utcnow().isoformat()
    result = db.Scholarships.update_one({"scholarship_id": sid}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Updated"}), 200


@sch_bp.route("/<sid>", methods=["DELETE"])
@jwt_required()
def deactivate_scholarship(sid):
    if not is_admin():
        return jsonify({"error": "Admin only"}), 403
    db.Scholarships.update_one({"scholarship_id": sid}, {"$set": {"status": "Inactive"}})
    return jsonify({"message": "Deactivated"}), 200