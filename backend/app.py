import os
import sys

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from database import get_scholarship_collection
from routes_auth import auth_bp
from routes_profile import profile_bp
from routes_scholarships_extras import extras_bp

load_dotenv()

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
    return jsonify({"status": "healthy"}), 200


@app.route('/api/scholarships/', methods=['GET'])
def list_scholarships():
    collection = get_scholarship_collection()
    results = list(collection.find({}, {"_id": 0}))
    return jsonify({"results": results, "count": len(results)}), 200


@app.route('/api/scholarships/search', methods=['GET'])
def search_scholarships():
    collection = get_scholarship_collection()
    q = request.args.get('q', '').strip()
    state = request.args.get('state')
    category = request.args.get('category')
    gender = request.args.get('gender')
    course = request.args.get('course')
    max_income = request.args.get('max_income')
    min_percentage = request.args.get('min_percentage')
    sort_by = request.args.get('sort_by', 'application_deadline')
    order = request.args.get('order', 'asc')
    
    query = {}
    if q:
        query["$or"] = [
            {"scholarship_name": {"$regex": q, "$options": "i"}},
            {"provider": {"$regex": q, "$options": "i"}}
        ]
    if state and state != "All": query["state"] = state
    if category and category != "All": query["category"] = category
    if gender and gender != "All": query["gender"] = gender
    if course and course != "All": query["course"] = course
    if max_income: query["max_income"] = {"$gte": int(max_income)}
    if min_percentage: query["minimum_percentage"] = {"$lte": int(min_percentage)}
    
    sort_dir = 1 if order == "asc" else -1
    results = list(collection.find(query, {"_id": 0}).sort(sort_by, sort_dir))
    return jsonify({"results": results, "count": len(results)}), 200


@app.route('/api/scholarships/<scholarship_id>', methods=['GET'])
def get_scholarship(scholarship_id):
    collection = get_scholarship_collection()
    doc = collection.find_one({"scholarship_id": scholarship_id}, {"_id": 0})
    if not doc:
        return jsonify({"error": "Not found"}), 404
    return jsonify(doc), 200


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
    app.run(host="0.0.0.0", port=Config.FLASK_PORT, debug=(Config.FLASK_ENV == "development"))