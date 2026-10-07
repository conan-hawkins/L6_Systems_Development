"""Versioned REST API, returning JSON.

All endpoints live under /api/v1 and are split into modules by resource.
"""

from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api/v1")

# Imported after the blueprint exists so the route modules can use it.
from helpbot.api import conversations, messages  # noqa: E402,F401
