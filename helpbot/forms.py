"""Forms for user registration and login."""

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            Length(max=255),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=12, max=128, message="Password must be between 12 and 128 characters long"),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            Length(max=255),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
        ],
    )
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")