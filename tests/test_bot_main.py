import sqlite3
import types
import sys
import os
import pytest

# Ensure the parent directory is on the path for importing project modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Provide dummy modules to satisfy imports in bot_main dependencies
sys.modules.setdefault("cv2", types.SimpleNamespace())
sys.modules.setdefault("pyzbar", types.SimpleNamespace())
sys.modules.setdefault("pyzbar.pyzbar", types.SimpleNamespace(decode=lambda *args, **kwargs: []))
sys.modules.setdefault("assistant.qr_reader", types.SimpleNamespace(read_qr=lambda *args, **kwargs: None))

from assistant import db_handler
from bot_main import sheet_key_command, store_google_sheet_key


class DummyMessage:
    def __init__(self):
        self.text = None
    async def reply_text(self, text, **kwargs):
        self.text = text


class DummyUpdate:
    def __init__(self, user_id: int):
        self.effective_user = types.SimpleNamespace(id=user_id)
        self.message = DummyMessage()


class DummyContext:
    def __init__(self):
        self.user_data = {}
import asyncio


def test_sheet_key_command_outputs_key(tmp_path, monkeypatch):
    monkeypatch.setattr(db_handler, "db_connect", lambda: sqlite3.connect(tmp_path / "test.db"))
    db_handler.table_init()
    db_handler.add_user(1)
    db_handler.add_googlesheet_key(1, "sheet123")

    update = DummyUpdate(1)
    context = DummyContext()
    context.user_data["user"] = db_handler.get_user(1)

    asyncio.run(sheet_key_command(update, context))

    assert update.message.text == "Your Google Sheet key: sheet123"


def test_sheet_key_command_requires_start(tmp_path, monkeypatch):
    """Ensure the command prompts users to run /start before use."""
    monkeypatch.setattr(db_handler, "db_connect", lambda: sqlite3.connect(tmp_path / "test.db"))
    db_handler.table_init()

    update = DummyUpdate(1)
    context = DummyContext()

    asyncio.run(sheet_key_command(update, context))

    assert update.message.text == "Please run /start first to initialize your account."


def test_store_google_sheet_key_extracts_key_from_link(tmp_path, monkeypatch):
    monkeypatch.setattr(db_handler, "db_connect", lambda: sqlite3.connect(tmp_path / "test.db"))
    db_handler.table_init()
    db_handler.add_user(1)
    update = DummyUpdate(1)
    context = DummyContext()
    context.user_data["user"] = db_handler.get_user(1)

    url = (
        "https://docs.google.com/spreadsheets/d/10s_m17fznodfg0uosbZ0LFbqX8zUxLlMkF__0oOsxpo"
        "/edit?pli=1&gid=1#gid=1"
    )
    update.message.text = url
    asyncio.run(store_google_sheet_key(update, context))

    user = db_handler.get_user(1)
    assert user.googlesheet_key == "10s_m17fznodfg0uosbZ0LFbqX8zUxLlMkF__0oOsxpo"
