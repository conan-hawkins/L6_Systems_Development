"""User model: account details, password hash."""

from flask import current_app
from flask_login import UserMixin
from argon2 import PasswordHasher
from argon2 import exceptions

from helpbot.extensions import db, login_manager

ph = PasswordHasher()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = (db.CheckConstraint("email = lower(email)", name="ck_users_email_lowercase"),)

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())

    def set_password(self, password):
        """Hash the password and set password_hash."""
        try:
            self.password_hash = ph.hash(password)

        except exceptions.HashingError:
            current_app.logger.warning("An error occurred while hashing the password.")
            raise

        except exceptions.UnsupportedParametersError:
            current_app.logger.warning("The parameters used for hashing are not supported.")
            raise

    def check_password(self, password):
        """Verify the password against the stored hash."""
        try:
            return ph.verify(self.password_hash, password)

        except exceptions.VerifyMismatchError:
            current_app.logger.info("Failed password check for user id %s", self.id)
            return False
            
        except exceptions.VerificationError:
            current_app.logger.warning("An error occurred while verifying the password.")
            return False
            
        except exceptions.InvalidHashError:
            current_app.logger.error("The hash is invalid.")
            return False
            

@login_manager.user_loader
def load_user(user_id):
    """Tell Flask-Login how to reload a user from the id stored in the session."""
    return db.session.get(User, int(user_id))
