from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from app import create_app
from echo_app.auth.services import RegistrationConflictError
from echo_app.extensions import db
from echo_app.models import Post, PostInteraction, User


@pytest.fixture
def app():
    tmp_dir = Path.cwd() / ".tmp-tests" / uuid4().hex
    tmp_dir.mkdir(parents=True, exist_ok=True)
    db_path = tmp_dir / "test.db"
    app = create_app(
        "testing",
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path.as_posix()}",
            "POSTS_PER_PAGE": 5,
        },
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    with app.app_context():
        record = User(username="writer", email="writer@example.com")
        record.set_password("Password123")
        db.session.add(record)
        db.session.commit()
        return record.id


def register(client, username="writer", email="writer@example.com", password="Password123"):
    return client.post(
        "/auth/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=False,
    )


def login(client, username="writer", password="Password123"):
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )


def create_post(client, title="Test Post", content="This is enough content to make a valid blog post.", tags="flask, testing"):
    return client.post(
        "/create",
        data={"title": title, "content": content, "tags": tags},
        follow_redirects=False,
    )


def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ECHO" in response.data


def test_register_and_login_flow(client, app):
    response = register(client)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/login")

    with app.app_context():
        user = User.query.filter_by(username="writer").first()
        assert user is not None
        assert user.email == "writer@example.com"

    login_response = login(client)
    assert login_response.status_code == 302
    assert login_response.headers["Location"].endswith("/")


def test_register_route_handles_service_conflicts(client, monkeypatch):
    def fail_register(**_kwargs):
        raise RegistrationConflictError(username_taken=True, email_taken=True)

    monkeypatch.setattr("echo_app.auth.routes.register_user", fail_register)
    response = register(client, username="writer", email="writer@example.com")

    assert response.status_code == 200
    assert b"Username already exists" in response.data
    assert b"Email already registered" in response.data


def test_logout_uses_post_and_clears_session(client, user):
    login(client)
    response = client.post("/auth/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    protected = client.get("/my-posts", follow_redirects=False)
    assert protected.status_code == 302
    assert "/auth/login" in protected.headers["Location"]


def test_create_post_requires_login(client):
    response = client.get("/create", follow_redirects=False)
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_create_post_persists_summary_tags_and_reading_time(client, app, user):
    login(client)
    response = create_post(client)
    assert response.status_code == 302

    with app.app_context():
        post = Post.query.one()
        assert post.summary
        assert post.reading_time >= 1
        assert [tag.name for tag in post.tags] == ["flask", "testing"]


def test_create_post_deduplicates_colliding_tag_slugs(client, app, user):
    login(client)
    response = create_post(client, title="Slug Collision", content="This post has enough content to validate correctly.", tags="c++, c")
    assert response.status_code == 302

    with app.app_context():
        post = Post.query.filter_by(title="Slug Collision").one()
        assert [tag.name for tag in post.tags] == ["c++"]
        assert [tag.slug for tag in post.tags] == ["c"]


def test_edit_post_creates_version_history(client, app, user):
    login(client)
    create_post(client, title="Original", content="Original content for the first version.", tags="flask")

    with app.app_context():
        post = Post.query.one()
        post_id = post.id

    response = client.post(
        f"/edit/{post_id}",
        data={
            "title": "Updated",
            "content": "Updated content for the new version of the post.",
            "tags": "flask, refactor",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302

    with app.app_context():
        post = db.session.get(Post, post_id)
        assert post.title == "Updated"
        assert len(post.versions) == 1
        assert post.versions[0].title == "Original"


def test_post_ownership_is_enforced(client, app, user):
    with app.app_context():
        owner = db.session.get(User, user)
        post = Post(author=owner, title="Owned", content="Owned content for editing access.", summary="Owned content", reading_time=1)
        db.session.add(post)
        intruder = User(username="intruder", email="intruder@example.com")
        intruder.set_password("Password123")
        db.session.add(intruder)
        db.session.commit()
        post_id = post.id

    login(client, username="intruder")
    response = client.post(
        f"/edit/{post_id}",
        data={"title": "Nope", "content": "Nope nope nope nope", "tags": ""},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_search_tag_and_digest_views(client, app, user):
    login(client)
    create_post(client, title="Flask Search", content="Flask makes testing easier with a small app.", tags="flask, python")
    create_post(client, title="Design Notes", content="Architecture decisions matter for clean codebases.", tags="architecture")

    with app.app_context():
        post = Post.query.filter_by(title="Flask Search").first()
        first_tag = post.tags[0].slug

    search_response = client.get("/search?query=testing")
    assert search_response.status_code == 200
    assert b"Flask Search" in search_response.data

    tag_response = client.get(f"/tags/{first_tag}")
    assert tag_response.status_code == 200
    assert b"Flask Search" in tag_response.data

    client.get(f"/post/{post.id}")
    client.get(f"/post/{post.id}")

    digest_response = client.get("/digest")
    assert digest_response.status_code == 200
    assert b"Top 5 Blogs of the Week" in digest_response.data
    assert b"Flask Search" in digest_response.data


def test_weekly_digest_ranks_top_five_by_interactions(client, app, user):
    login(client)
    for index in range(1, 7):
        create_post(
            client,
            title=f"Post {index}",
            content=f"Post {index} has enough content to be valid and rankable in the weekly digest.",
            tags="ranking",
        )

    with app.app_context():
        posts = {post.title: post for post in Post.query.all()}
        interaction_counts = {
            "Post 1": 1,
            "Post 2": 4,
            "Post 3": 3,
            "Post 4": 6,
            "Post 5": 2,
            "Post 6": 5,
        }
        for title, count in interaction_counts.items():
            for _ in range(count):
                db.session.add(PostInteraction(post=posts[title], kind="view"))
        db.session.commit()

    response = client.get("/digest")
    assert response.status_code == 200

    page = response.get_data(as_text=True)
    assert "Post 1" not in page
    assert page.index("Post 4") < page.index("Post 6") < page.index("Post 2") < page.index("Post 3") < page.index("Post 5")
