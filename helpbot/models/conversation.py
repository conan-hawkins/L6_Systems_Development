"""Conversation model: metadata for a chat session owned by a user.

The messages themselves live in MongoDB and are linked by conversation id.
"""

from helpbot.extensions import db


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    # TODO: user_id (FK -> users.id), title, created_at, updated_at.
