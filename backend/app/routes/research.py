from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from app import db
from app.models import ResearchPost, Professor

research_bp = Blueprint("research", __name__)

# ------------------------------
# CREATE POST
# ------------------------------
@research_bp.route("/", methods=["POST"])
@jwt_required()
def create_post():
    print("\n📥 [DEBUG] Incoming POST /api/research request")
    print("📄 Headers:", dict(request.headers))
    try:
        verify_jwt_in_request()
        identity = get_jwt_identity()  # now a string (professor ID)
        claims = get_jwt()             # JWT claims (contains field)
        print("🟢 CREATE_POST -> JWT Identity:", identity)
        print("🟢 CREATE_POST -> JWT Claims:", claims)
    except Exception as e:
        print("❌ CREATE_POST JWT error:", str(e))
        return jsonify({"error": "Invalid or missing token"}), 422

    prof = Professor.query.get(int(identity))
    print("👤 Professor Lookup Result:", prof)

    if not prof:
        print("❌ Professor not found for ID:", identity)
        return jsonify({"error": "Professor not found"}), 404

    try:
        data = request.get_json() or {}
        print("🧩 Request JSON Data:", data)
    except Exception as e:
        print("❌ JSON Parse Error:", str(e))
        return jsonify({"error": "Invalid JSON"}), 400

    title = data.get("title")
    content = data.get("content")

    if not all([title, content]):
        print("⚠️ Missing required fields: title or content")
        return jsonify({"error": "Title and content required"}), 400

    try:
        post = ResearchPost(
            title=title,
            content=content,
            field=claims.get("field", prof.field),
            author_id=prof.id
        )
        db.session.add(post)
        db.session.commit()
        print("✅ Post created successfully:", post.to_dict())
    except Exception as e:
        db.session.rollback()
        print("❌ DB Commit Error:", str(e))
        return jsonify({"error": "Database error"}), 500

    return jsonify({"message": "Post created", "post": post.to_dict()}), 201


# ------------------------------
# GET POSTS
# ------------------------------
@research_bp.route("/", methods=["GET"])
@jwt_required()
def get_posts():
    print("\n🔍 [DEBUG] Incoming GET /api/research request")
    print("📄 Headers:", dict(request.headers))
    print("🔢 Query Params:", request.args)

    try:
        verify_jwt_in_request()
        identity = get_jwt_identity()  # string ID
        claims = get_jwt()             # JWT claims
        print("🟢 JWT Identity (GET /research):", identity)
        print("🟢 JWT Claims (GET /research):", claims)
    except Exception as e:
        print("❌ JWT verification failed:", str(e))
        return jsonify({"error": "Invalid or expired token"}), 422

    prof = Professor.query.get(int(identity))
    print("👤 Professor Lookup Result:", prof)

    if not prof:
        print("❌ Professor not found for ID:", identity)
        return jsonify({"error": "Professor not found"}), 404

    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        print(f"📄 Pagination -> Page: {page}, Per Page: {per_page}")

        posts_paginated = (
            ResearchPost.query.filter_by(field=claims.get("field", prof.field))
            .order_by(ResearchPost.created_at.desc())
            .paginate(page=page, per_page=per_page)
        )

        print("✅ Posts retrieved:", len(posts_paginated.items))
    except Exception as e:
        print("❌ DB Query Error:", str(e))
        return jsonify({"error": "Database query failed"}), 500

    return jsonify({
        "posts": [p.to_dict() for p in posts_paginated.items],
        "total": posts_paginated.total,
        "page": posts_paginated.page,
        "pages": posts_paginated.pages
    }), 200
