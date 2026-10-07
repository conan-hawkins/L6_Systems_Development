"""Authentication blueprint: register, login and logout.

Passwords are hashed (never stored in plain text). Google OAuth login
can be added here as a second sign-in option.
"""

from flask import Blueprint, render_template

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/register", methods=["GET", "POST"])
def register():
    # TODO: validate form, hash password, create User in SQL database.
    return render_template("auth/register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    # TODO: verify password hash and call login_user().
    return render_template("auth/login.html")


@auth.route("/logout")
def logout():
    # TODO: call logout_user() and redirect.
    raise NotImplementedError
