"""Public pages: landing page and error handlers."""

from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


# TODO: register 404/500 handlers with @main.app_errorhandler.
