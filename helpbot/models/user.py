"""User model: account details, password hash and role."""

from flask_login import UserMixin

from helpbot.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    # TODO: email, password_hash, role, created_at,
    # set_password() / check_password() helpers.


@login_manager.user_loader
def load_user(user_id):
    """Tell Flask-Login how to reload a user from the id stored in the session."""
    return db.session.get(User, int(user_id))
