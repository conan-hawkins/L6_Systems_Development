# Container image for the Flask app, served by gunicorn.
FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY helpbot ./helpbot
RUN pip install --no-cache-dir .

ENV PORT=8080
CMD gunicorn --bind 0.0.0.0:$PORT "helpbot:create_app('production')"
