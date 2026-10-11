from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import os
from models import create_user, find_user_by_email, verify_password, find_user_by_id

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    user_id, error = create_user(name, email, password)
    if error:
        return jsonify({"error": error}), 400

    hours = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 24))
    token = create_access_token(identity=user_id, expires_delta=timedelta(hours=hours))

    return jsonify({
        "message": "Registration successful",
        "token": token,
        "user": {"id": user_id, "name": name, "email": email.lower()}
    }), 201


@auth_bp.route("/api/auth/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json() or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = find_user_by_email(email)
    if not user or not verify_password(password, user["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    hours = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 24))
    token = create_access_token(identity=str(user["_id"]), expires_delta=timedelta(hours=hours))

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {"id": str(user["_id"]), "name": user["name"], "email": user["email"]}
    }), 200


@auth_bp.route("/api/auth/me", methods=["GET", "OPTIONS"])
@jwt_required(optional=True)
def me():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = find_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"]
    }), 200