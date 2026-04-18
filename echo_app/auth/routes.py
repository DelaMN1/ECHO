from __future__ import annotations

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from echo_app.auth.forms import LoginForm, RegistrationForm
from echo_app.auth.services import RegistrationConflictError, authenticate_user, register_user
from echo_app.utils.auth import login_user, logout_user


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if getattr(g, "current_user", None):
        return redirect(url_for("blog.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            register_user(username=form.username.data, email=form.email.data, password=form.password.data)
        except RegistrationConflictError as exc:
            if exc.username_taken:
                form.username.errors.append("Username already exists. Please choose a different one.")
            if exc.email_taken:
                form.email.errors.append("Email already registered. Please use a different email.")
        else:
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if getattr(g, "current_user", None):
        return redirect(url_for("blog.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = authenticate_user(username=form.username.data, password=form.password.data)
        if user is None:
            flash("Invalid username or password.", "error")
        else:
            login_user(user)
            flash("Login successful.", "success")
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)
            return redirect(url_for("blog.index"))
    return render_template("auth/login.html", form=form)


@auth_bp.post("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("blog.index"))
