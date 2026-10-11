import os
import sys
import logging

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from config import Config
from database import client

app = Flask(__name__)

# ---------- CORS (covers successful responses) ----------
cors_origins = Config.CORS_ORIGINS or ["http://localhost:3000"]
allowed_origins = list(set(
    cors_origins + [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://172.19.139.8:3000",
    ]
))

CORS(
    app,
    origins=allowed_origins,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    supports_credentials=True,
    expose_headers=["Content-Type", "Authorization"],
    max_age=3600,
    automatic_options=True,
)

# ---------- JWT ----------
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=Config.JWT_ACCESS_TOKEN_EXPIRES_HOURS)
jwt = JWTManager(app)

# ---------- FORCE CORS on every response ----------
@app.after_request
def force_cors(response):
    origin = request.headers.get("Origin")
    if origin:
        # Overwrite regardless of what flask_cors set
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Max-Age"] = "3600"
    return response

# ---------- Register Blueprints ----------
from routes.auth_routes import auth_bp
from routes.profile_routes import profile_bp
from routes.scholarship_routes import sch_bp
from routes.scraper_routes import scraper_bp
from routes.crawler_routes import crawler_bp
from routes.admin_routes import admin_bp
from routes.applications_routes import apps_bp
from routes.chatbot_routes import chat_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(profile_bp, url_prefix="/api/profile")
app.register_blueprint(sch_bp, url_prefix="/api/scholarships")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(apps_bp, url_prefix="/api/applications")
app.register_blueprint(chat_bp, url_prefix="/api/chatbot")
app.register_blueprint(scraper_bp, url_prefix="/api/scraper")
app.register_blueprint(crawler_bp, url_prefix="/api/crawler")

print("✅ Blueprints registered: auth, profile, scholarships, admin, applications, chatbot, scraper, crawler")


# ---------- Health check ----------
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


# ---------- Background scraper scheduler ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if os.getenv("DISABLE_SCHEDULER", "false").lower() != "true":
    try:
        from jobs.scheduler import start_scheduler
        start_scheduler(interval_hours=24)
        logger.info("✅ Background scraper scheduler started")
    except Exception as e:
        logger.warning(f"⚠️ Scheduler failed to start: {e}")


if __name__ == "__main__":
    print(f"🚀 Starting {Config.APP_NAME} backend on port {Config.FLASK_PORT}")
    app.run(
        host="0.0.0.0",
        port=Config.FLASK_PORT,
        debug=(Config.FLASK_ENV == "development")
    )