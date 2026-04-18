from __future__ import annotations

import math
import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload, selectinload

from echo_app.extensions import db
from echo_app.models import Post, PostInteraction, PostVersion, Tag, User, post_tags, tag_cloud_rows


def _slugify(value: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return base or "tag"


def _normalize_tags(raw_tags: str | None) -> list[tuple[str, str]]:
    if not raw_tags:
        return []
    seen_slugs: set[str] = set()
    cleaned: list[tuple[str, str]] = []
    for part in raw_tags.split(","):
        name = part.strip().lower()
        if not name:
            continue
        slug = _slugify(name)
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        cleaned.append((name, slug))
    return cleaned


def _summarize(content: str) -> str:
    sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", content.strip()) if segment.strip()]
    if not sentences:
        return ""
    if len(sentences) == 1:
        return sentences[0][:200] + ("..." if len(sentences[0]) > 200 else "")
    return " ".join(sentences[:2])


def _reading_time(content: str) -> int:
    word_count = len([part for part in content.split() if part.strip()])
    return max(1, math.ceil(word_count / 200))


def _load_tag_entities(tag_names: list[tuple[str, str]]) -> list[Tag]:
    if not tag_names:
        return []

    existing_by_slug = {
        tag.slug: tag
        for tag in Tag.query.filter(Tag.slug.in_([slug for _, slug in tag_names])).all()
    }
    tags: list[Tag] = []
    for name, slug in tag_names:
        tag = existing_by_slug.get(slug)
        if tag is None:
            tag = Tag(name=name, slug=slug)
            db.session.add(tag)
            existing_by_slug[slug] = tag
        tags.append(tag)
    return tags


def _post_query():
    return Post.query.options(joinedload(Post.author), selectinload(Post.tags), selectinload(Post.versions))


def _week_window(now: datetime | None = None) -> tuple[datetime, datetime]:
    current = now or datetime.now(timezone.utc)
    week_start = (current - timedelta(days=current.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    return week_start, week_start + timedelta(days=7)


def list_posts(*, page: int, per_page: int):
    pagination = _post_query().order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return pagination


def get_post(post_id: int) -> Post | None:
    return _post_query().filter_by(id=post_id).first()


def record_post_interaction(post: Post, *, kind: str = "view") -> None:
    db.session.add(PostInteraction(post=post, kind=kind))
    db.session.commit()


def create_post(*, author: User, title: str, content: str, tags_raw: str | None) -> Post:
    post = Post(
        author=author,
        title=title.strip(),
        content=content.strip(),
        summary=_summarize(content),
        reading_time=_reading_time(content),
    )
    db.session.add(post)
    post.tags = _load_tag_entities(_normalize_tags(tags_raw))
    db.session.commit()
    return post


def update_post(*, post: Post, title: str, content: str, tags_raw: str | None) -> Post:
    version = PostVersion(post=post, title=post.title, content=post.content)
    db.session.add(version)

    post.title = title.strip()
    post.content = content.strip()
    post.summary = _summarize(content)
    post.reading_time = _reading_time(content)
    post.tags = _load_tag_entities(_normalize_tags(tags_raw))

    db.session.commit()
    return post


def delete_post(post: Post) -> None:
    db.session.delete(post)
    db.session.commit()


def search_posts(query: str) -> list[Post]:
    query = query.strip()
    if not query:
        return []

    lookup = f"%{query}%"
    return (
        _post_query()
        .outerjoin(Post.tags)
        .filter(
            or_(
                Post.title.ilike(lookup),
                Post.content.ilike(lookup),
                Post.summary.ilike(lookup),
                Tag.name.ilike(lookup),
            )
        )
        .distinct()
        .order_by(Post.created_at.desc())
        .all()
    )


def posts_by_tag(slug: str) -> tuple[Tag | None, list[Post]]:
    tag = Tag.query.filter_by(slug=slug).first()
    if tag is None:
        return None, []
    posts = (
        _post_query()
        .join(Post.tags)
        .filter(Tag.id == tag.id)
        .order_by(Post.created_at.desc())
        .all()
    )
    return tag, posts


def weekly_digest(*, limit: int = 5) -> dict[str, object]:
    week_start, week_end = _week_window()
    interaction_count = func.count(PostInteraction.id).label("interaction_count")

    rows = (
        db.session.query(Post, interaction_count)
        .join(PostInteraction, PostInteraction.post_id == Post.id)
        .options(joinedload(Post.author), selectinload(Post.tags), selectinload(Post.versions))
        .filter(
            PostInteraction.kind == "view",
            PostInteraction.created_at >= week_start,
            PostInteraction.created_at < week_end,
        )
        .group_by(Post.id)
        .order_by(interaction_count.desc(), func.max(PostInteraction.created_at).desc(), Post.created_at.desc())
        .limit(limit)
        .all()
    )

    iso_year, iso_week, _ = week_start.isocalendar()
    return {
        "label": f"{iso_year}-W{iso_week:02d}",
        "week_start": week_start,
        "week_end": week_end,
        "limit": limit,
        "posts": [{"post": post, "interaction_count": count} for post, count in rows],
    }


def user_posts(user: User) -> list[Post]:
    return _post_query().filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()


def tag_cloud() -> list[dict[str, int | str]]:
    cloud = []
    for tag, count in tag_cloud_rows():
        cloud.append({"name": tag.name, "slug": tag.slug, "count": count})
    return cloud
