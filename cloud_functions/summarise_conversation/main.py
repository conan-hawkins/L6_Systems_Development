"""Cloud function: summarise a conversation.

Triggered over HTTP (or on a schedule). Reads the conversation's messages
from MongoDB, asks the OpenAI API for a short summary, and saves it.
"""

import functions_framework


@functions_framework.http
def summarise_conversation(request):
    # TODO: read conversation_id, fetch messages, call OpenAI, save summary.
    return {"status": "not implemented"}, 501
