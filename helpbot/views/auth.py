"""Authentication blueprint: register, login and logout.

Passwords are hashed (never stored in plain text). Google OAuth login is also available.
"""
from flask import Blueprint, redirect, render_template, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required

from sqlalchemy.exc import IntegrityError

from helpbot.extensions import db, oauth
from helpbot.models.user import User
from helpbot.forms import RegistrationForm, LoginForm

from authlib.integrations.base_client import OAuthError

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/register", methods=["GET", "POST"])
def register():
    """Create an account and log the user in."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Normalize the email and check if the email is already registered
        email = form.email.data.strip().lower()
        user = db.session.scalar(db.select(User).filter_by(email=email))

        if user:
            form.email.errors.append("Email already registered.")
            
        else:
            # Create a new user
            user = User(email=email)
            user.set_password(form.password.data)
            db.session.add(user)

            try:
                # Commit the new user to the database and log them in
                db.session.commit()
                login_user(user)
                return redirect(url_for("main.index"))
            
            except IntegrityError:
                # Handle the case where the email is already registered due to a race condition
                db.session.rollback()
                form.email.errors.append("Email already registered.")
            

    return render_template("auth/register.html", form=form)
    

@auth.route("/login", methods=["GET", "POST"])
def login():
    """Log the user in."""
    # If the user is already logged in, redirect them to the main index page
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        # Normalize the email and check if the user exists
        email = form.email.data.strip().lower()
        user = db.session.scalar(db.select(User).filter_by(email=email))

        if user and user.check_password(form.password.data):
            # Log the user in and redirect to the main index page
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for("main.index"))
        
        else:
            # If the user does not exist or the password is incorrect, add an error message
            form.email.errors.append("Invalid email or password.")

    return render_template("auth/login.html", form=form)


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    """Log the user out."""
    logout_user()
    return redirect(url_for("main.index"))


@auth.route("/google" , methods=["GET"])
def google_login():
    """Redirect the user to Google's OAuth 2.0 login page."""
    redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth.route("/google/callback", methods=["GET"])
def google_callback():
    """Handle the callback from Google's OAuth 2.0 login."""
    try:
        token = oauth.google.authorize_access_token()

    except OAuthError:
        flash("Google sign-in was cancelled or failed.")
        return redirect(url_for("auth.login"))

    user_info = token["userinfo"]

    if not user_info.get("email_verified"):
        flash("Your Google email address is not verified.")
        return redirect(url_for("auth.login"))

    google_sub = user_info["sub"]
    email = user_info["email"].strip().lower()

    # Check if the google_sub already exists in the database
    user = db.session.scalar(db.select(User).filter_by(google_sub=google_sub))

    if not user:
        # Check if the email already exists in the database
        user = db.session.scalar(db.select(User).filter_by(email=email))
        if user is not None:
            user.google_sub = google_sub      # existing password account: link it

        else:
            user = User(email=email, google_sub=google_sub)
            db.session.add(user)

        try:
            db.session.commit()

        except IntegrityError:
            # Handles a race where two requests create the same user at once
            db.session.rollback()
            flash("Could not sign in with Google. Please try again.")
            return redirect(url_for("auth.login"))

    login_user(user)
    return redirect(url_for("main.index"))