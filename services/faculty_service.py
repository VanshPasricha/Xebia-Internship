"""Faculty account management service."""

from __future__ import annotations

from database.db import db_manager
from database.models import FacultyUser
from utils.helpers import hash_password


class FacultyService:
    """CRUD-style operations for admin-managed faculty accounts."""

    def list_faculty(self, include_admin: bool = True) -> list[FacultyUser]:
        query = "SELECT id, username, name, role FROM Faculty"
        params: tuple[object, ...] = ()
        if not include_admin:
            query += " WHERE role = ?"
            params = ("faculty",)
        query += " ORDER BY CASE role WHEN 'admin' THEN 0 ELSE 1 END, name"

        with db_manager.connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [FacultyUser(**dict(row)) for row in rows]

    def create_faculty(self, name: str, username: str, password: str, role: str = "faculty") -> tuple[bool, str]:
        if not all([name.strip(), username.strip(), password.strip()]):
            return False, "All faculty fields are required."

        with db_manager.connection() as conn:
            exists = conn.execute("SELECT 1 FROM Faculty WHERE username = ?", (username.strip(),)).fetchone()
            if exists:
                return False, "This faculty username is already in use."
            conn.execute(
                "INSERT INTO Faculty(username, password, name, role) VALUES (?, ?, ?, ?)",
                (username.strip(), hash_password(password.strip()), name.strip(), role),
            )
        return True, "Faculty account created successfully."

    def delete_faculty(self, username: str) -> tuple[bool, str]:
        with db_manager.connection() as conn:
            row = conn.execute("SELECT role FROM Faculty WHERE username = ?", (username,)).fetchone()
            if not row:
                return False, "Faculty account not found."
            if row["role"] == "admin":
                return False, "The admin account cannot be deleted."

            conn.execute("DELETE FROM Faculty WHERE username = ?", (username,))
            conn.execute("DELETE FROM Timetable WHERE faculty = ?", (username,))
        return True, "Faculty account deleted."

    def count_faculty(self, include_admin: bool = True) -> int:
        with db_manager.connection() as conn:
            if include_admin:
                row = conn.execute("SELECT COUNT(*) AS total FROM Faculty").fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) AS total FROM Faculty WHERE role = 'faculty'").fetchone()
        return int(row["total"])
