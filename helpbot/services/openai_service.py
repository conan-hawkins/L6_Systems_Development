"""Wrapper around the OpenAI API.

Keeping all OpenAI calls here means the rest of the app (and the tests)
never talk to the API directly, so it can be mocked or swapped.
"""

# TODO: get_completion(messages) -> str using the openai client.
