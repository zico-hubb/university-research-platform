import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # Core Config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour

    # Mail Config
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    # CORS
    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # ✅ JWT Debug Logs — Catch token problems before route executes
    @jwt.unauthorized_loader
    def handle_missing_token(reason):
        print(f"❌ JWT Unauthorized Loader Triggered: {reason}")
        print("🧠 Request Headers:", dict(request.headers))
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    @jwt.invalid_token_loader
    def handle_invalid_token(reason):
        print(f"❌ JWT Invalid Token: {reason}")
        print("🧠 Request Headers:", dict(request.headers))
        return jsonify({"error": "Invalid token"}), 422

    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        print(f"❌ JWT Expired Token: {jwt_payload}")
        return jsonify({"error": "Token expired"}), 401

    @jwt.needs_fresh_token_loader
    def handle_non_fresh_token(jwt_header, jwt_payload):
        print(f"⚠️ Non-Fresh Token Access Attempt: {jwt_payload}")
        return jsonify({"error": "Fresh token required"}), 401

    # Blueprints
    from app.utils.auth import auth_bp
    from app.routes.research import research_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(research_bp, url_prefix="/api/research")

    with app.app_context():
        db.create_all()

    print("✅ Flask app initialized with JWT debugging enabled.")
    return app
