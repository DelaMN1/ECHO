from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from echo_app.models import User


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=30)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match.")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, field) -> None:
        existing = User.query.filter_by(username=field.data.strip()).first()
        if existing:
            raise ValidationError("Username already exists. Please choose a different one.")

    def validate_email(self, field) -> None:
        existing = User.query.filter_by(email=field.data.strip().lower()).first()
        if existing:
            raise ValidationError("Email already registered. Please use a different email.")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=30)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
