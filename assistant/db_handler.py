import os
import sqlite3
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """Simple representation of a bot user."""

    id: int
    user_id: int
    googlesheet_key: Optional[str]
    is_owner: int
    registered_at: str


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
            user_id INTEGER UNIQUE,
            googlesheet_key TEXT,
            is_owner INTEGER DEFAULT 0,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qr_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            qr_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    conn.commit()
    conn.close()


def get_user(user_id: int) -> Optional[User]:
    """Retrieve a user from the database."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, googlesheet_key, is_owner, registered_at "
        "FROM users WHERE user_id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None


def add_user(user_id: int) -> None:
    """Insert a new user into the users table if it does not already exist."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,),
    )
    conn.commit()
    conn.close()
