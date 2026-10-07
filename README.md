# HelpBot

An AI-powered help desk chatbot built with Flask. It talks to the OpenAI
API, stores users and conversations in a SQL database (Postgres on Neon)
and chat messages in a NoSQL database (MongoDB Atlas).

## Project structure

```
helpbot/              Flask application package
  __init__.py         application factory (create_app)
  config.py           configuration classes
  extensions.py       SQLAlchemy, login manager, CSRF
  views/              HTML page blueprints (main, auth, chat, admin)
  api/                REST API blueprint (/api/v1)
  models/             SQL models (SQLAlchemy)
  nosql/              MongoDB repositories
  services/           business logic and OpenAI wrapper
  templates/          Jinja templates
  static/             CSS and JavaScript
cloud_functions/      serverless functions deployed separately
tests/                pytest unit tests
docs/                 architecture, database, security and deployment docs
```

## Setup

Install the application before trying to run it.

```
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
copy .env.example .env          # then fill in your keys
```

## Run

The `--app` option tells Flask where to find the application factory:

```
flask --app helpbot run --debug
```

## Test

```
pytest
```

## AI use acknowledgement

AI (Claude) was used to generate the initial project structure, as
permitted under Tier 2 of the coursework brief.
