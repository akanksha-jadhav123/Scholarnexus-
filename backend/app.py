import os
import sys

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from config import Config
from database import client

app = Flask(__name__)
CORS(app, origins=Config.CORS_ORIGINS)

app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=Config.JWT_ACCESS_TOKEN_EXPIRES_HOURS)
jwt = JWTManager(app)

# ---------- Register Blueprints ----------
from routes.auth_routes import auth_bp
from routes.profile_routes import profile_bp
from routes.scholarship_routes import sch_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(profile_bp, url_prefix="/api/profile")
app.register_blueprint(sch_bp, url_prefix="/api/scholarships")


@app.route("/api/health", methods=["GET"])
def health():
    try:
        client.admin.command("ping")
        return jsonify({
            "app": Config.APP_NAME,
            "status": "ok",
            "db": "connected",
            "env": Config.FLASK_ENV
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "app": Config.APP_NAME,
        "message": "ScholarNexus API is running",
        "version": "1.0.0"
    }), 200


if __name__ == "__main__":
    print(f"🚀 Starting {Config.APP_NAME} backend on port {Config.FLASK_PORT}")
    app.run(host="0.0.0.0", port=Config.FLASK_PORT, debug=(Config.FLASK_ENV == "development"))