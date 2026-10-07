"""Smoke tests for the application factory."""


def test_app_is_testing(app):
    assert app.config["TESTING"]


def test_index_page(client):
    assert client.get("/").status_code == 200
