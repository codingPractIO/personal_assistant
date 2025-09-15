import os
import sqlite3
from typing import Optional

from assistant.class_user import User
from assistant.input_handler import extract_sheet_key


class GoogleSheetOwnershipError(ValueError):
    """Raised when a Google Sheet key is already owned by another user."""


def db_connect():
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect("db/bot.db")
    return conn

def table_init():
    conn = db_connect()
    cursor = conn.cursor()

    # Create tables if they do not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_telegram_id INTEGER UNIQUE,
            googlesheet_key TEXT,
            googlesheet_owner INTEGER DEFAULT 0,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_telegram_id INTEGER,
            receipt_number TEXT,       
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_telegram_id) REFERENCES users (user_telegram_id)
        )
    ''')

    conn.commit()
    conn.close()


def get_user(user_telegram_id: int) -> Optional[User]:
    """Retrieve a user from the database."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_telegram_id, googlesheet_key, googlesheet_owner, registered_at "
        "FROM users WHERE user_telegram_id = ?",
        (user_telegram_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None


def add_user(user_telegram_id: int) -> None:
    """Insert a new user into the users table if it does not already exist."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_telegram_id) VALUES (?)",
        (user_telegram_id,),
    )
    conn.commit()
    conn.close()


def construct_user(user_telegram_id: int) -> Optional[User]:
    """Ensure a user exists in the database and return it."""
    add_user(user_telegram_id)
    return get_user(user_telegram_id)

def add_googlesheet_key(user_telegram_id: int, url: str) -> str:
    """Update the googlesheet_key for a user, parsing it from a URL.

    The function also marks the requesting user as the sheet owner in the
    database by setting ``googlesheet_owner`` to ``1``.

    Raises:
        GoogleSheetOwnershipError: If the provided key is already owned by
            another user.
    """

    key = extract_sheet_key(url) or url
    conn = db_connect()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_telegram_id FROM users WHERE googlesheet_key = ? AND googlesheet_owner = 1",
            (key,),
        )
        owner_row = cursor.fetchone()
        if owner_row and owner_row[0] != user_telegram_id:
            raise GoogleSheetOwnershipError(
                "That Google Sheet key is already owned by another user."
            )

        cursor.execute(
            """
            INSERT INTO users (user_telegram_id, googlesheet_key, googlesheet_owner)
            VALUES (?, ?, 1)
            ON CONFLICT(user_telegram_id) DO UPDATE SET
                googlesheet_key = excluded.googlesheet_key,
                googlesheet_owner = 1
            """,
            (user_telegram_id, key),
        )
        conn.commit()
        return key
    finally:
        conn.close()

def get_googlesheet_key(user_telegram_id: int) -> str | None:
    """Retrieve the googlesheet_key for a user from the users table."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT googlesheet_key FROM users WHERE user_telegram_id = ?",
        (user_telegram_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return None


def add_processed_receipt(user_telegram_id: int, receipt_number: str) -> None:
    """Store a processed receipt number for the given user."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO processed_receipts (user_telegram_id, receipt_number) VALUES (?, ?)",
        (user_telegram_id, receipt_number),
    )
    conn.commit()
    conn.close()


def get_processed_receipts(user_telegram_id: int) -> set[str]:
    """Retrieve all processed receipt numbers for a given user."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT receipt_number FROM processed_receipts WHERE user_telegram_id = ?",
        (user_telegram_id,),
    )
    receipts = {row[0] for row in cursor.fetchall()}
    conn.close()
    return receipts
