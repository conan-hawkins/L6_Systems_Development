"""Chat blueprint: the main chatbot interface for logged-in users."""

from flask import Blueprint, render_template

chat = Blueprint("chat", __name__, url_prefix="/chat")


@chat.route("/")
def index():
    # TODO: protect with @login_required and list the user's conversations.
    return render_template("chat/chat.html")
