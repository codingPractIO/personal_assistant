import sqlite3
import os

import pytest

from assistant import db_handler


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


def test_processed_receipts_functions(tmp_path, monkeypatch):
    """Ensure processed receipts can be stored and retrieved per user."""
    monkeypatch.setattr(db_handler, "db_connect", lambda: _tmp_db(tmp_path))

    db_handler.table_init()
    db_handler.add_user(1)
    db_handler.add_processed_receipt(1, "123")
    db_handler.add_processed_receipt(1, "456")

    receipts = db_handler.get_processed_receipts(1)
    assert receipts == {"123", "456"}

    db_handler.add_user(2)
    assert db_handler.get_processed_receipts(2) == set()
