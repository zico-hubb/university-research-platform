from . import db
from datetime import datetime

class Professor(db.Model):
    __tablename__ = "professors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    field = db.Column(db.String(100), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "field": self.field,
            "verified": self.verified,
            "created_at": self.created_at.isoformat()
        }

class ResearchPost(db.Model):
    __tablename__ = "research_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    field = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("professors.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    author = db.relationship("Professor", backref=db.backref("posts", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "field": self.field,
            "author_id": self.author_id,
            "author_name": self.author.name,
            "created_at": self.created_at.isoformat()
        }
