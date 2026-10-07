# Cloud functions

Serverless functions deployed separately from the Flask app
(e.g. Google Cloud Functions). Each folder is one function with its own
main.py and requirements.txt.

- summarise_conversation/ - summarises a finished conversation with the
  OpenAI API and stores the summary, so the main app does not do slow work
  during a request.
