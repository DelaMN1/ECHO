from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlencode

import flask
from flask import Flask, g
from markupsafe import Markup
import werkzeug.urls

if not hasattr(flask, "Markup"):
    flask.Markup = Markup
if not hasattr(werkzeug.urls, "url_encode"):
    werkzeug.urls.url_encode = urlencode

from echo_app.auth import auth_bp
from echo_app.blog import blog_bp
from echo_app.config import BASE_DIR, config
from echo_app.extensions import bcrypt, csrf, db
from echo_app.utils import format_date, format_datetime, load_current_user


def create_app(config_name: str | None = None, test_config: dict | None = None) -> Flask:
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    selected_config = config_name or os.getenv("FLASK_ENV", "default")
    app.config.from_object(config[selected_config])
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(blog_bp)

    register_hooks(app)
    register_filters(app)

    with app.app_context():
        db.create_all()

    return app


def register_hooks(app: Flask) -> None:
    @app.before_request
    def load_request_user():
        load_current_user()

    @app.context_processor
    def inject_globals():
        return {
            "app_name": app.config["APP_NAME"],
            "current_user": getattr(g, "current_user", None),
        }


def register_filters(app: Flask) -> None:
    app.jinja_env.filters["dateonly"] = format_date
    app.jinja_env.filters["datetime"] = format_datetime
