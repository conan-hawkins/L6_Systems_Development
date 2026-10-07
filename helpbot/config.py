"""Configuration classes, loaded by create_app().

Secrets are read from environment variables (see .env.example) and are
never committed to version control.
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Settings shared by every environment."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")

    # SQL database (e.g. Neon Postgres) - users, conversations metadata.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///helpbot.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # NoSQL database (e.g. MongoDB Atlas) - chat messages and transcripts.
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/helpbot")

    # OpenAI API.
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    # Session cookie hardening.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
