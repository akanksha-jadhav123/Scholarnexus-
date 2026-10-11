"""
Helper for creating notifications across the app.
"""
from datetime import datetime
from database import db


class NotificationService:

    @staticmethod
    def create(user_id, notif_type, message, deadline=None):
        db.Notifications.insert_one({
            "user_id": user_id,
            "type": notif_type,
            "message": message,
            "deadline": deadline,
            "read_status": False,
            "created_at": datetime.utcnow()
        })

    @staticmethod
    def new_match(user_id, count):
        NotificationService.create(
            user_id, "new_match",
            f"🎯 {count} new scholarships match your profile"
        )

    @staticmethod
    def deadline_reminder(user_id, scholarship_name, days_left, deadline):
        NotificationService.create(
            user_id, "deadline",
            f"⏰ {scholarship_name} deadline in {days_left} day(s)",
            deadline=deadline
        )

    @staticmethod
    def missing_document(user_id, scholarship_name, doc_name):
        NotificationService.create(
            user_id, "missing_doc",
            f"📄 Missing document: {doc_name} for {scholarship_name}"
        )

    @staticmethod
    def status_change(user_id, scholarship_name, new_status):
        NotificationService.create(
            user_id, "status_change",
            f"📋 {scholarship_name} — status: {new_status}"
        )