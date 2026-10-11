from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from datetime import datetime

documents_bp = Blueprint("documents", __name__)


@documents_bp.route("/<scholarship_id>", methods=["GET"])
@jwt_required()
def get_document_checklist(scholarship_id):
    user_id = get_jwt_identity()

    scholarship = db.Scholarships.find_one(
        {"scholarship_id": scholarship_id},
        {"_id": 0}
    )

    if not scholarship:
        return jsonify({"error": "Scholarship not found"}), 404

    required_documents = scholarship.get("required_documents", [])

    saved = db.DocumentChecklists.find_one(
        {
            "user_id": user_id,
            "scholarship_id": scholarship_id
        },
        {"_id": 0}
    )

    saved_documents = {}

    if saved:
        for doc in saved.get("checklist", []):
            saved_documents[doc["document_name"]] = doc.get(
                "status",
                "pending"
            )

    checklist = []

    for document_name in required_documents:
        checklist.append({
            "document_name": document_name,
            "status": saved_documents.get(
                document_name,
                "pending"
            )
        })

    completed = sum(
        1 for doc in checklist
        if doc["status"] == "completed"
    )

    return jsonify({
        "scholarship_id": scholarship_id,
        "scholarship_name": scholarship.get("scholarship_name"),
        "checklist": checklist,
        "completed": completed,
        "total": len(checklist)
    }), 200


@documents_bp.route("/<scholarship_id>", methods=["POST"])
@jwt_required()
def update_document(scholarship_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    document_name = data.get("document_name")
    status = data.get("status")

    if not document_name:
        return jsonify({
            "error": "document_name is required"
        }), 400

    if status not in ["pending", "completed"]:
        return jsonify({
            "error": "status must be pending or completed"
        }), 400

    scholarship = db.Scholarships.find_one(
        {"scholarship_id": scholarship_id}
    )

    if not scholarship:
        return jsonify({
            "error": "Scholarship not found"
        }), 404

    required_documents = scholarship.get(
        "required_documents",
        []
    )

    if document_name not in required_documents:
        return jsonify({
            "error": "Document is not part of this scholarship checklist"
        }), 400

    db.DocumentChecklists.update_one(
        {
            "user_id": user_id,
            "scholarship_id": scholarship_id
        },
        {
            "$set": {
                "user_id": user_id,
                "scholarship_id": scholarship_id,
                "updated_at": datetime.utcnow()
            },
            "$setOnInsert": {
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )

    db.DocumentChecklists.update_one(
        {
            "user_id": user_id,
            "scholarship_id": scholarship_id,
            "checklist.document_name": document_name
        },
        {
            "$set": {
                "checklist.$.status": status,
                "updated_at": datetime.utcnow()
            }
        }
    )

    result = db.DocumentChecklists.find_one({
        "user_id": user_id,
        "scholarship_id": scholarship_id
    })

    existing_names = [
        d["document_name"]
        for d in result.get("checklist", [])
    ]

    if document_name not in existing_names:
        db.DocumentChecklists.update_one(
            {
                "user_id": user_id,
                "scholarship_id": scholarship_id
            },
            {
                "$push": {
                    "checklist": {
                        "document_name": document_name,
                        "status": status
                    }
                }
            }
        )

    return jsonify({
        "message": "Document status updated",
        "document_name": document_name,
        "status": status
    }), 200