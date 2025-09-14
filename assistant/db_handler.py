import os
import sqlite3
from typing import Optional

from assistant.class_user import User


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
            is_owner INTEGER DEFAULT 0,
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
        "SELECT id, user_telegram_id, googlesheet_key, is_owner, registered_at "
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

def add_googlesheet_key(user_telegram_id: int, googlesheet_key: str) -> None:
    """Update the googlesheet_key for a user in the users table."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET googlesheet_key = ? WHERE user_telegram_id = ?",
        (googlesheet_key, user_telegram_id),
    )
    conn.commit()
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
