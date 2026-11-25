"""Flask extension objects.

Created here without an app and bound later in init_extensions(), so any
module can import them without causing circular imports.
"""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth


db = SQLAlchemy()
oauth = OAuth()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def init_extensions(app):
    """Bind every extension to the given app."""
    db.init_app(app)
    oauth.init_app(app)
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email"},
    )

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    csrf.init_app(app)
    migrate.init_app(app, db)
    # TODO: connect to MongoDB (see helpbot/nosql/__init__.py).
