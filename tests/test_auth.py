"""Tests for registration, login, logout and password hashing."""

import pytest
from sqlalchemy.exc import IntegrityError

from helpbot.extensions import db
from helpbot.models.user import User

EMAIL = "bob@example.com"
PASSWORD = "correct-horse-battery"  # this must be over the current minimum character length rule


# ---------- helpers ----------


def count_users():
    return db.session.scalar(db.select(db.func.count()).select_from(User))


def register(client, email=EMAIL, password=PASSWORD, confirm_password=None):
    return client.post(
        "/auth/register",
        data={
            "email": email,
            "password": password,
            "confirm_password": password if confirm_password is None else confirm_password,
        },
    )


def login(client, email=EMAIL, password=PASSWORD):
    return client.post("/auth/login", data={"email": email, "password": password})


def is_logged_in(client):
    with client.session_transaction() as sess:
        return "_user_id" in sess


@pytest.fixture
def registered_user(app):
    """A user saved straight to the database, so route tests skip the register form."""
    user = User(email=EMAIL)
    user.set_password(PASSWORD)
    db.session.add(user)
    db.session.commit()


# ---------- model tests ----------


def test_r1_password_is_hashed(app):
    user = User(email=EMAIL)
    user.set_password(PASSWORD)
    assert user.password_hash != PASSWORD
    assert user.password_hash.startswith("$argon2id$")


def test_r1_correct_password_accepted(app):
    user = User(email=EMAIL)
    user.set_password(PASSWORD)
    assert user.check_password(PASSWORD) is True


def test_r1_wrong_password_rejected(app):
    user = User(email=EMAIL)
    user.set_password(PASSWORD)
    assert user.check_password("not-the-password") is False


def test_r1_same_password_gives_different_hashes(app):
    a = User(email="a@example.com")
    b = User(email="b@example.com")
    a.set_password(PASSWORD)
    b.set_password(PASSWORD)
    assert a.password_hash != b.password_hash


def test_r1_database_rejects_uppercase_email(app):
    user = User(email="Bob@Example.com")
    user.set_password(PASSWORD)
    db.session.add(user)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


# ---------- registration ----------


def test_r1_register_creates_user(app, client):
    response = register(client, email="Bob@Example.com")
    assert response.status_code == 302
    users = db.session.scalars(db.select(User)).all()
    assert len(users) == 1
    assert users[0].email == "bob@example.com"


def test_r1_register_duplicate_email_rejected(app, client, registered_user):
    # registered_user saves the account without logging in, so the duplicate
    # check runs (a logged-in client would be redirected before reaching it).
    response = register(client, email=EMAIL.upper())
    assert response.status_code == 200
    assert b"Email already registered" in response.data
    assert count_users() == 1


def test_r1_register_short_password_rejected(app, client):
    response = register(client, password="a" * 11)
    assert response.status_code == 200
    assert count_users() == 0


def test_r1_register_mismatched_passwords_rejected(app, client):
    response = register(client, confirm_password="something-different-1")
    assert response.status_code == 200
    assert count_users() == 0


# ---------- login ----------


def test_r1_login_success(client, registered_user):
    response = login(client)
    assert response.status_code == 302
    assert is_logged_in(client)


def test_r1_login_is_case_insensitive(client, registered_user):
    response = login(client, email="BOB@Example.com")
    assert response.status_code == 302
    assert is_logged_in(client)


@pytest.mark.parametrize(
    "email, password",
    [
        (EMAIL, "wrong-password-123"),  # real account, wrong password
        ("nobody@example.com", PASSWORD),  # no such account
    ],
)
def test_r1_login_failure_same_message(client, registered_user, email, password):
    response = login(client, email=email, password=password)
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data
    assert not is_logged_in(client)


# ---------- logout ----------


def test_r1_logout_rejects_get(client):
    response = client.get("/auth/logout")
    assert response.status_code == 405


def test_r1_logout_logs_user_out(client, registered_user):
    login(client)
    assert is_logged_in(client)
    response = client.post("/auth/logout")
    assert response.status_code == 302
    assert not is_logged_in(client)


def test_r1_logout_requires_login(client):
    response = client.post("/auth/logout")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


# ---------- CSRF ----------


def test_r1_csrf_enforced_when_enabled(app, client):
    """The other tests run with CSRF off; this shows the protection works when it is on."""
    app.config["WTF_CSRF_ENABLED"] = True
    response = login(client)  # no CSRF token in the form data
    assert response.status_code == 400