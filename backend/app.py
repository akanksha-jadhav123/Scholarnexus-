import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from database import get_scholarship_collection
from routes_auth import auth_bp
from routes_profile import profile_bp
from routes_scholarships_extras import extras_bp

load_dotenv()

app = Flask(__name__)

CORS(app, 
     origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev_secret")
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
jwt = JWTManager(app)

@jwt.unauthorized_loader
def missing_token(reason):
    return jsonify({"error": "Missing token", "reason": reason}), 401

@jwt.invalid_token_loader
def invalid_token(reason):
    return jsonify({"error": "Invalid token", "reason": reason}), 401

@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):
    return jsonify({"error": "Token expired"}), 401

@jwt.revoked_token_loader
def revoked_token(jwt_header, jwt_payload):
    return jsonify({"error": "Token revoked"}), 401

# ⭐ Handle OPTIONS preflight BEFORE JWT runs
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response


# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(extras_bp)


# ---------------- ROUTES ----------------

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "ScholarNexus API running 🚀", "status": "success"}), 200


@app.route('/health', methods=['GET'])
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


if __name__ == '__main__':
    port = int(os.getenv("FLASK_PORT", 5000))
    print(f"🚀 ScholarNexus Backend on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)