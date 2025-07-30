import os
import sqlite3


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
            googlesheet_key TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qr_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            qr_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    conn.commit()
    conn.close()


def add_user(user_id: int):
    """Insert a new user into the users table if it does not already exist."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()
    conn.close()
