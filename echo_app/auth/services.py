from __future__ import annotations

from sqlalchemy.exc import IntegrityError

from echo_app.extensions import db
from echo_app.models import User


class RegistrationConflictError(Exception):
    def __init__(self, *, username_taken: bool = False, email_taken: bool = False) -> None:
        self.username_taken = username_taken
        self.email_taken = email_taken
        super().__init__("Registration data conflicts with an existing user.")


def _registration_conflicts(*, username: str, email: str) -> tuple[bool, bool]:
    username_taken = User.query.filter_by(username=username).first() is not None
    email_taken = User.query.filter_by(email=email).first() is not None
    return username_taken, email_taken


def register_user(*, username: str, email: str, password: str) -> User:
    normalized_username = username.strip()
    normalized_email = email.strip().lower()
    username_taken, email_taken = _registration_conflicts(username=normalized_username, email=normalized_email)
    if username_taken or email_taken:
        raise RegistrationConflictError(username_taken=username_taken, email_taken=email_taken)

    user = User(username=normalized_username, email=normalized_email)
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        username_taken, email_taken = _registration_conflicts(username=normalized_username, email=normalized_email)
        if username_taken or email_taken:
            raise RegistrationConflictError(username_taken=username_taken, email_taken=email_taken) from exc
        raise
    return user


def authenticate_user(*, username: str, password: str) -> User | None:
    user = User.query.filter_by(username=username.strip()).first()
    if user and user.check_password(password):
        return user
    return None
