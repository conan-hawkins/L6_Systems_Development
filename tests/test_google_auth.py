"""Google sign-in tests. Google is replaced with a fake, so nothing leaves the test run."""

import pytest
from authlib.integrations.base_client import OAuthError
from sqlalchemy.exc import IntegrityError

from helpbot.extensions import db, oauth
from helpbot.models.user import User

EMAIL = "bob@example.com"
PASSWORD = "correct-horse-battery"
SUB = "google-sub-123"
CALLBACK = "/auth/google/callback"


# ---------- helpers ----------


def fake_google(monkeypatch, userinfo):
    """Make the Google token exchange return the given userinfo."""
    monkeypatch.setattr(
        oauth.google, "authorize_access_token", lambda: {"userinfo": userinfo}
    )


def fake_google_cancelled(monkeypatch):
    """Make the Google token exchange fail the way it does when the user clicks Cancel."""

    def cancelled():
        raise OAuthError(error="access_denied")

    monkeypatch.setattr(oauth.google, "authorize_access_token", cancelled)


def userinfo(email=EMAIL, sub=SUB, verified=True):
    return {"sub": sub, "email": email, "email_verified": verified}


def count_users():
    return db.session.scalar(db.select(db.func.count()).select_from(User))


def is_logged_in(client):
    with client.session_transaction() as sess:
        return "_user_id" in sess


@pytest.fixture
def registered_user(app):
    """A password account saved straight to the database."""
    user = User(email=EMAIL)
    user.set_password(PASSWORD)
    db.session.add(user)
    db.session.commit()


# ---------- callback tests ----------


def test_google_new_user_created(app, client, monkeypatch):
    fake_google(monkeypatch, userinfo(email="Bob@Example.com"))
    response = client.get(CALLBACK)
    assert response.status_code == 302
    users = db.session.scalars(db.select(User)).all()
    assert len(users) == 1
    assert users[0].email == "bob@example.com"
    assert users[0].google_sub == SUB
    assert users[0].password_hash is None
    assert is_logged_in(client)


def test_google_returning_user(app, client, monkeypatch):
    fake_google(monkeypatch, userinfo())
    client.get(CALLBACK)
    client.post("/auth/logout")
    assert not is_logged_in(client)

    client.get(CALLBACK)
    assert count_users() == 1
    assert is_logged_in(client)


def test_google_links_password_account(app, client, registered_user, monkeypatch):
    fake_google(monkeypatch, userinfo(email=EMAIL))
    response = client.get(CALLBACK)
    assert response.status_code == 302
    assert count_users() == 1
    user = db.session.scalar(db.select(User))
    assert user.password_hash is not None
    assert user.google_sub == SUB


def test_google_unverified_email_rejected(app, client, monkeypatch):
    fake_google(monkeypatch, userinfo(verified=False))
    response = client.get(CALLBACK)
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
    assert count_users() == 0
    assert not is_logged_in(client)


def test_google_cancel(app, client, monkeypatch):
    fake_google_cancelled(monkeypatch)
    response = client.get(CALLBACK)
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
    assert not is_logged_in(client)


# ---------- model tests ----------


def test_google_user_cannot_use_password_login(app):
    user = User(email=EMAIL, google_sub=SUB)  # no password_hash
    assert user.check_password("anything") is False


def test_database_requires_a_login_method(app):
    user = User(email=EMAIL)  # neither password_hash nor google_sub
    db.session.add(user)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()