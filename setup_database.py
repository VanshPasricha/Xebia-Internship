"""Standalone database setup script for FACETRACK."""

from database.db import init_database


if __name__ == "__main__":
    init_database()
    print("FACETRACK database initialized.")
