from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from datetime import datetime
import bcrypt
from database import db
from utils.validators import is_valid_email, is_valid_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "student")

    if not name or not email or not password:
        return jsonify({"error": "Name, email, password required"}), 400
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    if not is_valid_password(password):
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if db.Users.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 409

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    db.Users.insert_one({
        "name": name,
        "email": email,
        "password_hash": hashed,
        "role": role,
        "bookmarks": [],
        "created_at": datetime.utcnow()
    })
    return jsonify({"message": f"Welcome to ScholarNexus, {name}!"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = db.Users.find_one({"email": email})
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(
        identity=str(user["_id"]),
        additional_claims={
            "role": user["role"],
            "email": user["email"],
            "name": user["name"]
        }
    )
    return jsonify({
        "token": token,
        "role": user["role"],
        "name": user["name"],
        "email": user["email"],
        "app": "ScholarNexus"
    }), 200