from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from services.chatbot_service import ChatbotService
from middleware.rate_limit import rate_limit

chat_bp = Blueprint("chatbot", __name__)


@chat_bp.route("/ask", methods=["POST", "OPTIONS"])
@rate_limit(max_per_minute=20)
def ask():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except Exception:
        pass

    result = ChatbotService.answer(question, user_id=user_id)
    return jsonify(result), 200