"""HelpBot - an AI-powered help desk chatbot built with Flask.

Uses the application factory pattern so that different configurations
(development, testing, production) can create separate app instances.
https://flask.palletsprojects.com/en/latest/patterns/appfactories/
"""

from flask import Flask

__version__ = "0.1.0"


def create_app(config_name="development"):
    """Create and configure a Flask application instance."""
    app = Flask(__name__)

    from helpbot.config import config_by_name
    app.config.from_object(config_by_name[config_name])

    # Initialise extensions (SQL database, MongoDB, login manager, CSRF).
    from helpbot.extensions import init_extensions
    init_extensions(app)

    # Import models so SQLAlchemy and Flask-Login know about them.
    from helpbot import models  # noqa: F401

    # Blueprints are imported inside the factory to avoid circular imports.
    # https://flask.palletsprojects.com/en/latest/patterns/packages/
    from helpbot.views.main import main
    from helpbot.views.auth import auth
    from helpbot.views.chat import chat
    from helpbot.views.admin import admin
    from helpbot.api import api

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(chat)
    app.register_blueprint(admin)
    app.register_blueprint(api)

    return app
