"""
db.py — tiny SQLite helper for Dearly.

Everything is saved to dearly.db, a single file that sits next to app.py.
It is created automatically the first time the server runs and is never
wiped — every signup, letter, journal entry and pen-pal request lives here
permanently, keyed by the user's id.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dearly.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # ---- tables below are created now so later phases (letters, journals,
    # pen pals) don't need a migration step — Phase 1 does not use them yet.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS letters (
            id TEXT PRIMARY KEY,
            owner_id TEXT,
            from_id TEXT,
            to_label TEXT,
            body TEXT NOT NULL,
            kind TEXT NOT NULL DEFAULT 'anonymous',
            mood TEXT,
            opened INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY(owner_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS journals (
            id TEXT PRIMARY KEY,
            owner_id TEXT NOT NULL,
            title TEXT,
            topic TEXT,
            body TEXT NOT NULL,
            visibility TEXT NOT NULL DEFAULT 'private',
            created_at TEXT NOT NULL,
            FOREIGN KEY(owner_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS penpal_requests (
            id TEXT PRIMARY KEY,
            from_id TEXT NOT NULL,
            to_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            FOREIGN KEY(from_id) REFERENCES users(id),
            FOREIGN KEY(to_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS penpals (
            user_id TEXT NOT NULL,
            penpal_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (user_id, penpal_id)
        )
    """)

    conn.commit()
    conn.close()
