"""
Admin analytics + user management endpoints.
Handles lists, strings, datetime, and null values safely.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timedelta
from database import db
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)


def is_admin():
    return get_jwt().get("role") == "admin"


def _to_str_list(value):
    """Normalize any value into a list of strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if v not in (None, "")]
    return [str(value).strip()]


@admin_bp.route("/analytics", methods=["GET"])
@jwt_required()
def analytics():
    try:
        if not is_admin():
            return jsonify({"error": "Admin only"}), 403

        # --- USERS ---
        total_users = db.Users.count_documents({"role": "student"})
        total_admins = db.Users.count_documents({"role": "admin"})
        total_profiles = db.StudentProfiles.count_documents({})
        total_users_all = db.Users.count_documents({})

        # --- SCHOLARSHIPS ---
        total_scholarships = db.Scholarships.count_documents({})
        active_scholarships = db.Scholarships.count_documents({"status": "Active"})
        auto_scraped = db.Scholarships.count_documents({"scholarship_id": {"$regex": "^AUTO"}})

        # --- BY SOURCE (safe) ---
        sources = {}
        try:
            for sc in db.Scholarships.find({}, {"source": 1}):
                s = sc.get("source") or "unknown"
                if isinstance(s, list):
                    s = s[0] if s else "unknown"
                s = str(s)
                sources[s] = sources.get(s, 0) + 1
        except Exception as e:
            logger.warning(f"by_source failed: {e}")

        # --- BY CATEGORY (handles list, string, None) ---
        categories = {}
        try:
            for sc in db.Scholarships.find({}, {"category": 1, "eligible_categories": 1}):
                # Try both fields — category may be string, eligible_categories may be list
                values = []
                if sc.get("category"):
                    values.extend(_to_str_list(sc["category"]))
                if sc.get("eligible_categories"):
                    values.extend(_to_str_list(sc["eligible_categories"]))

                if not values:
                    values = ["Unknown"]

                # Deduplicate within a single record
                for v in set(values):
                    categories[v] = categories.get(v, 0) + 1
        except Exception as e:
            logger.warning(f"by_category failed: {e}")

        # --- APPLICATIONS (safe) ---
        total_applications = db.Applications.count_documents({})
        app_by_status = {}
        try:
            for a in db.Applications.find({}, {"status": 1}):
                s = a.get("status") or "Unknown"
                if isinstance(s, list):
                    s = s[0] if s else "Unknown"
                s = str(s)
                app_by_status[s] = app_by_status.get(s, 0) + 1
        except Exception as e:
            logger.warning(f"app_by_status failed: {e}")

        # --- BOOKMARKS (safe) ---
        bookmarks = 0
        try:
            for u in db.Users.find({}, {"bookmarks": 1}):
                b = u.get("bookmarks") or []
                if isinstance(b, list):
                    bookmarks += len(b)
        except Exception as e:
            logger.warning(f"bookmarks failed: {e}")

        # --- LINK HEALTH (safe) ---
        try:
            link_stats = {
                "active": db.Scholarships.count_documents({"link_status": "active"}),
                "broken": db.Scholarships.count_documents({"link_status": "broken"}),
                "pending": db.Scholarships.count_documents({"link_status": "pending"}),
            }
        except Exception as e:
            logger.warning(f"link_stats failed: {e}")
            link_stats = {"active": 0, "broken": 0, "pending": 0}

        # --- RECENT SIGNUPS (safe — only count, no datetime comparison) ---
        recent_signups = 0
        try:
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_signups = db.Users.count_documents({
                "created_at": {"$gte": week_ago}
            })
        except Exception:
            # If created_at is stored as string, this fails gracefully
            recent_signups = 0

        return jsonify({
            "users": {
                "students": total_users,
                "admins": total_admins,
                "total": total_users_all,
                "profiles_completed": total_profiles,
                "recent_signups_7d": recent_signups
            },
            "scholarships": {
                "total": total_scholarships,
                "active": active_scholarships,
                "auto_scraped": auto_scraped,
                "by_source": sources,
                "by_category": categories
            },
            "applications": {
                "total": total_applications,
                "by_status": app_by_status
            },
            "bookmarks": bookmarks,
            "link_health": link_stats,
            "generated_at": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.exception("Analytics endpoint crashed")
        return jsonify({
            "error": "Analytics failed",
            "detail": str(e),
            "type": type(e).__name__
        }), 500


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    try:
        if not is_admin():
            return jsonify({"error": "Admin only"}), 403

        users = list(db.Users.find({}, {"password_hash": 0}).sort("created_at", -1).limit(200))
        for u in users:
            u["_id"] = str(u["_id"])
            if "created_at" in u and u["created_at"]:
                if isinstance(u["created_at"], datetime):
                    u["created_at"] = u["created_at"].isoformat()
                else:
                    u["created_at"] = str(u["created_at"])
        return jsonify(users), 200
    except Exception as e:
        logger.exception("list_users crashed")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/users/<user_id>/role", methods=["PUT"])
@jwt_required()
def update_user_role(user_id):
    try:
        if not is_admin():
            return jsonify({"error": "Admin only"}), 403

        data = request.get_json() or {}
        new_role = data.get("role")
        if new_role not in ["student", "admin"]:
            return jsonify({"error": "Invalid role"}), 400

        from bson import ObjectId
        db.Users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": new_role, "updated_at": datetime.utcnow()}}
        )
        return jsonify({"message": f"Role updated to {new_role}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400