"""SQLite access layer and schema bootstrap."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from utils.config import (
    DATABASE_PATH,
    DATA_DIR,
    FACULTY_DEFAULT_NAME,
    FACULTY_DEFAULT_PASSWORD,
    FACULTY_DEFAULT_USERNAME,
    FACES_DIR,
)
from utils.helpers import hash_password, setup_logging


class DatabaseManager:
    """Small helper around sqlite connections."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Yield a configured sqlite connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


db_manager = DatabaseManager(DATABASE_PATH)


def _ensure_column(conn: sqlite3.Connection, table_name: str, column_name: str, definition: str) -> None:
    """Add a new column to an existing table only if it is missing."""
    existing_columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}
    if column_name not in existing_columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def init_database() -> None:
    """Create folders, schema, and a default admin account."""
    setup_logging()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FACES_DIR.mkdir(parents=True, exist_ok=True)

    with db_manager.connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS Faculty (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'faculty'
            );

            CREATE TABLE IF NOT EXISTS Students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_no TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                year INTEGER NOT NULL,
                section TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                encoding TEXT NOT NULL,
                face_image_dir TEXT,
                red_flags INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS Timetable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                faculty TEXT NOT NULL,
                day TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                section TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_no TEXT NOT NULL,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT NOT NULL,
                late_flags INTEGER DEFAULT 0,
                UNIQUE(roll_no, subject, date)
            );
            """
        )

        _ensure_column(conn, "Faculty", "role", "TEXT NOT NULL DEFAULT 'faculty'")
        _ensure_column(conn, "Students", "red_flags", "INTEGER DEFAULT 0")
        _ensure_column(conn, "Attendance", "late_flags", "INTEGER DEFAULT 0")

        exists = conn.execute("SELECT id FROM Faculty WHERE username = ?", (FACULTY_DEFAULT_USERNAME,)).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO Faculty(username, password, name, role) VALUES (?, ?, ?, ?)",
                (
                    FACULTY_DEFAULT_USERNAME,
                    hash_password(FACULTY_DEFAULT_PASSWORD),
                    FACULTY_DEFAULT_NAME,
                    "admin",
                ),
            )
        else:
            conn.execute(
                "UPDATE Faculty SET role = 'admin' WHERE username = ?",
                (FACULTY_DEFAULT_USERNAME,),
            )
