from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from services.chatbot_service import ChatbotService

chat_bp = Blueprint("chatbot", __name__)


@chat_bp.route("/ask", methods=["POST"])
def ask():
    data = request.get_json() or {}
    question = data.get("question", "")

    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except Exception:
        pass

    result = ChatbotService.answer(question, user_id=user_id)
    return jsonify(result), 200