"""Flask extension objects.

Created here without an app and bound later in init_extensions(), so any
module can import them without causing circular imports.
"""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def init_extensions(app):
    """Bind every extension to the given app."""
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    csrf.init_app(app)

    # TODO: connect to MongoDB (see helpbot/nosql/__init__.py).
