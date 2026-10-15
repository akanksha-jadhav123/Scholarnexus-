import os
import sys
import logging

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from datetime import timedelta
from config import Config
from database import client, ensure_indexes

app = Flask(__name__)


# ======================================================
# CORS — manual, permissive for dev
# ======================================================
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        origin = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-Requested-With, Accept, Origin"
        )
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        )
        response.headers["Access-Control-Max-Age"] = "86400"
        return response


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-Requested-With, Accept, Origin"
        )
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        )
        response.headers["Access-Control-Expose-Headers"] = (
            "Content-Type, Authorization"
        )
    return response


# ======================================================
# JWT
# ======================================================
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
    hours=Config.JWT_ACCESS_TOKEN_EXPIRES_HOURS
)
jwt = JWTManager(app)


# ======================================================
# BLUEPRINT REGISTRATION
# ======================================================
def _register(name, module_path, attr, prefix):
    try:
        mod = __import__(module_path, fromlist=[attr])
        bp = getattr(mod, attr)
        app.register_blueprint(bp, url_prefix=prefix)
        print(f"✅ {name} registered at {prefix}")
        return True
    except ImportError as e:
        print(f"⚠️  {name} skipped: {e}")
        return False
    except Exception as e:
        print(f"❌ {name} failed: {e}")
        return False


_register("auth",          "routes.auth_routes",          "auth_bp",    "/api/auth")
_register("profile",       "routes.profile_routes",       "profile_bp", "/api/profile")
_register("scholarships",  "routes.scholarship_routes",   "sch_bp",     "/api/scholarships")
_register("admin",         "routes.admin_routes",         "admin_bp",   "/api/admin")
_register("applications",  "routes.applications_routes",  "apps_bp",    "/api/applications")
_register("chatbot",       "routes.chatbot_routes",       "chat_bp",    "/api/chatbot")
_register("crawler",       "routes.crawler_routes",       "crawler_bp", "/api/crawler")
_register("scraper",       "routes.scraper_routes",       "scraper_bp", "/api/scraper")
_register("documents",     "routes.documents_routes",     "docs_bp",    "/api/documents")
_register("notifications", "routes.notifications_routes", "notif_bp",   "/api/notifications")
_register("manual", "routes.manual_routes", "manual_bp", "/api/admin")

print("✅ Blueprint registration complete")


# ======================================================
# HEALTH + ROOT
# ======================================================
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
        "message": "ScholarNexus API is running"
    }), 200


# ======================================================
# BOOT
# ======================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure indexes on startup
ensure_indexes()
logger.info("✅ MongoDB indexes ensured")

# Optional scheduler — only if env var is set
if os.getenv("DISABLE_SCHEDULER", "true").lower() != "true":
    try:
        from jobs.scheduler import start_scheduler
        start_scheduler(interval_hours=24)
        logger.info("✅ Scheduler started")
    except Exception as e:
        logger.warning(f"⚠️ Scheduler skipped: {e}")


if __name__ == "__main__":
    print(f"🚀 Starting {Config.APP_NAME} on port {Config.FLASK_PORT}")
    app.run(host="0.0.0.0", port=Config.FLASK_PORT, debug=False)