from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db

notifications_bp = Blueprint(
    "notifications",
    __name__
)


@notifications_bp.route("/", methods=["GET"])
@jwt_required()
def list_notifications():
    user_id = get_jwt_identity()

    notifications = list(
        db.Notifications.find(
            {"user_id": user_id},
            {"_id": 0}
        )
        .sort("created_at", -1)
        .limit(100)
    )

    for notification in notifications:
        if notification.get("created_at"):
            notification["created_at"] = (
                notification["created_at"].isoformat()
            )

    unread = db.Notifications.count_documents({
        "user_id": user_id,
        "read_status": False
    })

    return jsonify({
        "notifications": notifications,
        "unread": unread
    }), 200


@notifications_bp.route(
    "/<notification_id>/read",
    methods=["POST"]
)
@jwt_required()
def mark_notification_read(notification_id):
    user_id = get_jwt_identity()

    from bson import ObjectId

    try:
        oid = ObjectId(notification_id)
    except Exception:
        return jsonify({
            "error": "Invalid notification ID"
        }), 400

    result = db.Notifications.update_one(
        {
            "_id": oid,
            "user_id": user_id
        },
        {
            "$set": {
                "read_status": True
            }
        }
    )

    if result.matched_count == 0:
        return jsonify({
            "error": "Notification not found"
        }), 404

    return jsonify({
        "message": "Notification marked as read"
    }), 200


@notifications_bp.route(
    "/read-all",
    methods=["POST"]
)
@jwt_required()
def mark_all_notifications_read():
    user_id = get_jwt_identity()

    result = db.Notifications.update_many(
        {
            "user_id": user_id,
            "read_status": False
        },
        {
            "$set": {
                "read_status": True
            }
        }
    )

    return jsonify({
        "message": "All notifications marked as read",
        "updated": result.modified_count
    }), 200