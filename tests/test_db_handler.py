import sqlite3
import os

import pytest

from assistant import db_handler


OWNERSHIP_MESSAGE = (
    "This Google Sheet key is already linked to another account. "
    "Please ask the current owner to release it or choose a different sheet."
)

JOIN_MESSAGE = (
    "This Google Sheet key is not registered to any owner. Please ask the owner to add it first."
)


def _tmp_db(tmp_path):
    """Return a connection to a temporary database inside tmp_path."""
    db_file = tmp_path / "test.db"
    return sqlite3.connect(db_file)


def test_get_user_returns_dataclass_after_add(tmp_path, monkeypatch):
    """add_user shouldn't return anything but get_user should return User."""
    monkeypatch.setattr(db_handler, "db_connect", lambda: _tmp_db(tmp_path))

    db_handler.table_init()

    result = db_handler.add_user(42)
    assert result is None

    user = db_handler.get_user(42)
    assert isinstance(user, db_handler.User)
    assert user.user_id == 42


def test_add_googlesheet_key_sets_owner_and_blocks_duplicates(tmp_path, monkeypatch):
    monkeypatch.setattr(db_handler, "db_connect", lambda: _tmp_db(tmp_path))

    db_handler.table_init()
    db_handler.add_user(1)
    db_handler.add_user(2)

    key = db_handler.add_googlesheet_key(1, "sheet123")
    assert key == "sheet123"

    owner = db_handler.get_user(1)
    assert owner.googlesheet_key == "sheet123"
    assert owner.googlesheet_owner == 1

    with pytest.raises(db_handler.GoogleSheetOwnershipError) as excinfo:
        db_handler.add_googlesheet_key(2, "sheet123")

    assert str(excinfo.value) == OWNERSHIP_MESSAGE

    non_owner = db_handler.get_user(2)
    assert non_owner.googlesheet_key is None
    assert non_owner.googlesheet_owner == 0


def test_add_googlesheet_key_creates_user_with_owner_flag(tmp_path, monkeypatch):
    monkeypatch.setattr(db_handler, "db_connect", lambda: _tmp_db(tmp_path))

    db_handler.table_init()

    # The helper should upsert the user and mark them as the sheet owner.
    key = db_handler.add_googlesheet_key(99, "sheet99")
    assert key == "sheet99"

    created = db_handler.get_user(99)
    assert created is not None
    assert created.googlesheet_key == "sheet99"
    assert created.googlesheet_owner == 1


def test_join_googlesheet_key_adds_existing_key(tmp_path, monkeypatch):
    monkeypatch.setattr(db_handler, "db_connect", lambda: _tmp_db(tmp_path))

    db_handler.table_init()
    db_handler.add_user(1)
    db_handler.add_user(2)

    db_handler.add_googlesheet_key(1, "sheet123")

    joined = db_handler.join_googlesheet_key(2, "https://docs.google.com/spreadsheets/d/sheet123/edit")
    assert joined == "sheet123"

    owner = db_handler.get_user(1)
    assert owner.googlesheet_owner == 1

    joined_user = db_handler.get_user(2)
    assert joined_user.googlesheet_key == "sheet123"
    assert joined_user.googlesheet_owner == 0


def test_join_googlesheet_key_requires_existing_owner(tmp_path, monkeypatch):
    monkeypatch.setattr(db_handler, "db_connect", lambda: _tmp_db(tmp_path))

    db_handler.table_init()
    db_handler.add_user(2)

    with pytest.raises(db_handler.GoogleSheetJoinError) as excinfo:
        db_handler.join_googlesheet_key(2, "sheet123")

    assert str(excinfo.value) == JOIN_MESSAGE

    user = db_handler.get_user(2)
    assert user.googlesheet_key is None
    assert user.googlesheet_owner == 0


def test_processed_receipts_functions(tmp_path, monkeypatch):
    """Ensure processed receipts can be stored and retrieved per user."""
    monkeypatch.setattr(db_handler, "db_connect", lambda: _tmp_db(tmp_path))

    db_handler.table_init()
    db_handler.add_user(1)
    db_handler.add_googlesheet_key(1, "sheet123")
    db_handler.add_processed_receipt(1, "123")
    db_handler.add_processed_receipt(1, "456")

    receipts = db_handler.get_processed_receipts("sheet123")
    assert receipts == {"123", "456"}

    # ensure the googlesheet_key column is populated alongside the telegram id
    conn = db_handler.db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT googlesheet_key FROM processed_receipts WHERE user_telegram_id = ?",
        (1,),
    )
    stored_keys = {row[0] for row in cursor.fetchall()}
    conn.close()
    assert stored_keys == {"sheet123"}

    assert db_handler.get_processed_receipts("missing-key") == set()
