from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import func
from echo_app.extensions import bcrypt, db


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    posts = db.relationship("Post", back_populates="author", cascade="all, delete-orphan", lazy="dynamic")

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    reading_time = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    author = db.relationship("User", back_populates="posts")
    tags = db.relationship("Tag", secondary=post_tags, back_populates="posts", lazy="selectin")
    interactions = db.relationship("PostInteraction", back_populates="post", cascade="all, delete-orphan", lazy="dynamic")
    versions = db.relationship(
        "PostVersion",
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="desc(PostVersion.edited_at)",
        lazy="selectin",
    )

    @property
    def tag_list(self) -> list[str]:
        return [tag.name for tag in self.tags]


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    posts = db.relationship("Post", secondary=post_tags, back_populates="tags", lazy="selectin")


class PostVersion(db.Model):
    __tablename__ = "post_versions"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    edited_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    post = db.relationship("Post", back_populates="versions")


class PostInteraction(db.Model):
    __tablename__ = "post_interactions"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False, index=True)
    kind = db.Column(db.String(32), nullable=False, default="view", index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    post = db.relationship("Post", back_populates="interactions")


def tag_cloud_rows():
    return (
        db.session.query(Tag, func.count(post_tags.c.post_id).label("post_count"))
        .join(post_tags, post_tags.c.tag_id == Tag.id)
        .group_by(Tag.id)
        .order_by(func.count(post_tags.c.post_id).desc(), Tag.name.asc())
        .all()
    )
