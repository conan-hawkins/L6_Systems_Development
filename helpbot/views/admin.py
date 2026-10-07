"""Admin blueprint: usage overview and user management for staff."""

from flask import Blueprint, render_template

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/")
def index():
    # TODO: restrict to admin role.
    return render_template("admin/dashboard.html")
