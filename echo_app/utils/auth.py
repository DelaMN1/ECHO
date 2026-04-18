from __future__ import annotations

from functools import wraps

from flask import flash, g, redirect, request, session, url_for

from echo_app.extensions import db
from echo_app.models import User


def load_current_user() -> None:
    g.current_user = None
    user_id = session.get("user_id")
    if user_id is None:
        return
    g.current_user = db.session.get(User, user_id)
    if g.current_user is None:
        session.clear()


def login_user(user: User) -> None:
    session.clear()
    session["user_id"] = user.id
    session["username"] = user.username
    session.permanent = True


def logout_user() -> None:
    session.clear()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if getattr(g, "current_user", None) is None:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("auth.login", next=request.full_path))
        return view(*args, **kwargs)

    return wrapped
