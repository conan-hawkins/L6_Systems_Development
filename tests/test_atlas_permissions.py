"""Check the helpbot-app MongoDB user has only the access docs/security.md says.

These tests connect to the real Atlas cluster, so they only run when MONGO_URI
logs in as helpbot-app. They are skipped in CI, which has no .env and is not
on the Atlas IP Access List, and skipped for any other user (such as
helpbot-ingest), which really is allowed to make the writes tested below.
"""

import os
from pathlib import Path

import pytest
from dotenv import dotenv_values
from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError

APP_USER = "helpbot-app"
# Self-hosted MongoDB rejects with code 13 (Unauthorized). Atlas uses its own
# generic code 8000 (AtlasError), so the message is checked as well.
UNAUTHORIZED_CODES = {13, 8000}
# Matches no real document, so a wrongly allowed update or delete changes nothing.
NO_MATCH = {"_id": "permission-test-no-match"}


def assert_permission_denied(error):
    assert error.code in UNAUTHORIZED_CODES
    assert "not allowed" in str(error) or "not authorized" in str(error)


@pytest.fixture(scope="module")
def mongo_db():
    # Read .env without loading it into os.environ, so other tests aren't affected.
    env_file = Path(__file__).resolve().parent.parent / ".env"
    uri = os.environ.get("MONGO_URI") or dotenv_values(env_file).get("MONGO_URI")
    if not uri:
        pytest.skip("MONGO_URI is not set")

    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        status = client.get_default_database().command("connectionStatus")
        users = [u["user"] for u in status["authInfo"]["authenticatedUsers"]]
        if users != [APP_USER]:
            pytest.skip(f"MONGO_URI must log in as {APP_USER}, not {users}")
        yield client.get_default_database()
    except PyMongoError as exc:
        pytest.skip(f"Cannot reach Atlas: {exc}")
    finally:
        client.close()


def test_can_read_manual_sections(mongo_db):
    assert mongo_db["manual_sections"].find_one({}, {"_id": 1}) is not None


@pytest.mark.parametrize(
    "write",
    [
        lambda c: c.insert_one(dict(NO_MATCH)),
        lambda c: c.update_one(NO_MATCH, {"$set": {"permission_test": True}}),
        lambda c: c.delete_one(NO_MATCH),
    ],
    ids=["insert", "update", "delete"],
)
def test_cannot_change_manual_sections(mongo_db, write):
    with pytest.raises(OperationFailure) as exc:
        write(mongo_db["manual_sections"])
    assert_permission_denied(exc.value)


def test_can_write_conversations(mongo_db):
    conversations = mongo_db["conversations"]
    doc_id = conversations.insert_one({"permission_test": True}).inserted_id
    try:
        conversations.update_one({"_id": doc_id}, {"$set": {"checked": True}})
        assert conversations.find_one({"_id": doc_id})["checked"] is True
    finally:
        conversations.delete_one({"_id": doc_id})
    assert conversations.find_one({"_id": doc_id}) is None


def test_cannot_read_other_collections(mongo_db):
    with pytest.raises(OperationFailure) as exc:
        mongo_db["permission_test"].find_one()
    assert_permission_denied(exc.value)
