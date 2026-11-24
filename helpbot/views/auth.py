"""Authentication blueprint: register, login and logout.

Passwords are hashed (never stored in plain text). Google OAuth login
can be added here as a second sign-in option.
"""
from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user, login_required

from sqlalchemy.exc import IntegrityError

from helpbot.extensions import db
from helpbot.models.user import User
from helpbot.forms import RegistrationForm, LoginForm

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
