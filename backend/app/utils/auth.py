from flask import Blueprint, request, jsonify, current_app
from app import db, bcrypt
from app.models import Professor
from flask_jwt_extended import create_access_token
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta

auth_bp = Blueprint("auth", __name__)

def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

# ------------------------------
# REGISTER
# ------------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    field = data.get("field")

    if not all([name, email, password, field]):
        return jsonify({"error": "All fields are required"}), 400

    if Professor.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    professor = Professor(name=name, email=email, password=hashed_pw, field=field, verified=True)
    db.session.add(professor)
    db.session.commit()

    # ✅ Fix: Pass string ID to identity, extra data in additional_claims
    token = create_access_token(
        identity=str(professor.id),
        additional_claims={"field": professor.field},
        expires_delta=timedelta(hours=2)
    )

    print(f"🟢 REGISTER: Generated token for Professor ID {professor.id}")
    print(f"🟢 Token payload: {{'sub': '{professor.id}', 'field': '{professor.field}'}}")

    return jsonify({
        "message": "Professor registered (dev auto-verified).",
        "user": {"id": professor.id, "name": professor.name, "field": professor.field},
        "token": token
    }), 201

# ------------------------------
# LOGIN
# ------------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"error": "Email and password required"}), 400

    professor = Professor.query.filter_by(email=email).first()
    if not professor or not bcrypt.check_password_hash(professor.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # ✅ Fix: Pass string ID to identity, extra data in additional_claims
    token = create_access_token(
        identity=str(professor.id),
        additional_claims={"field": professor.field},
        expires_delta=timedelta(hours=2)
    )

    print(f"🟢 LOGIN: Token generated for {professor.email} (ID {professor.id})")
    print(f"🟢 Access token expires in 2 hours, payload: {{'sub': '{professor.id}', 'field': '{professor.field}'}}")

    return jsonify({
        "message": "Login successful",
        "user": {"id": professor.id, "name": professor.name, "field": professor.field},
        "token": token
    }), 200
