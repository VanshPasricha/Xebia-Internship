"""Timetable creation and retrieval service."""

from __future__ import annotations

from database.db import db_manager
from database.models import TimetableEntry
from utils.helpers import current_day_name


class TimetableService:
    """CRUD-style operations for timetable records."""

    def create_entry(
        self,
        subject: str,
        faculty: str,
        day: str,
        start_time: str,
        end_time: str,
        section: str,
    ) -> tuple[bool, str]:
        """Create a timetable slot after basic duplicate validation."""
        with db_manager.connection() as conn:
            duplicate = conn.execute(
                """
                SELECT 1 FROM Timetable
                WHERE faculty = ? AND day = ? AND start_time = ? AND section = ?
                """,
                (faculty, day, start_time, section),
            ).fetchone()
            if duplicate:
                return False, "A timetable slot already exists for this faculty, day, time, and batch."

            conn.execute(
                """
                INSERT INTO Timetable(subject, faculty, day, start_time, end_time, section)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (subject, faculty, day, start_time, end_time, section),
            )
        return True, "Timetable entry created."

    def update_entry(
        self,
        entry_id: int,
        subject: str,
        faculty: str,
        day: str,
        start_time: str,
        end_time: str,
        section: str,
    ) -> tuple[bool, str]:
        """Update an existing timetable entry."""
        with db_manager.connection() as conn:
            current = conn.execute("SELECT id FROM Timetable WHERE id = ?", (entry_id,)).fetchone()
            if not current:
                return False, "Timetable entry not found."
            duplicate = conn.execute(
                """
                SELECT 1 FROM Timetable
                WHERE faculty = ? AND day = ? AND start_time = ? AND section = ? AND id != ?
                """,
                (faculty, day, start_time, section, entry_id),
            ).fetchone()
            if duplicate:
                return False, "Another timetable slot already uses this faculty, day, time, and batch."
            conn.execute(
                """
                UPDATE Timetable
                SET subject = ?, faculty = ?, day = ?, start_time = ?, end_time = ?, section = ?
                WHERE id = ?
                """,
                (subject, faculty, day, start_time, end_time, section, entry_id),
            )
        return True, "Timetable entry updated."

    def delete_entry(self, entry_id: int) -> tuple[bool, str]:
        """Delete a timetable entry."""
        with db_manager.connection() as conn:
            exists = conn.execute("SELECT 1 FROM Timetable WHERE id = ?", (entry_id,)).fetchone()
            if not exists:
                return False, "Timetable entry not found."
            conn.execute("DELETE FROM Timetable WHERE id = ?", (entry_id,))
        return True, "Timetable entry deleted."

    def get_entry_by_id(self, entry_id: int) -> TimetableEntry | None:
        """Return a timetable entry by primary key."""
        with db_manager.connection() as conn:
            row = conn.execute("SELECT * FROM Timetable WHERE id = ?", (entry_id,)).fetchone()
        return TimetableEntry(**dict(row)) if row else None

    def list_entries(self, faculty: str | None = None, section: str | None = None, day: str | None = None) -> list[TimetableEntry]:
        """Fetch timetable entries filtered by faculty, section, or day."""
        query = "SELECT * FROM Timetable WHERE 1=1"
        params: list[str] = []
        if faculty:
            query += " AND faculty = ?"
            params.append(faculty)
        if section:
            query += " AND section = ?"
            params.append(section)
        if day:
            query += " AND day = ?"
            params.append(day)
        query += " ORDER BY CASE day WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 ELSE 7 END, start_time"

        with db_manager.connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [TimetableEntry(**dict(row)) for row in rows]

    def get_today_classes(self, faculty: str | None = None) -> list[TimetableEntry]:
        """Return today's timetable entries, optionally filtered to a faculty account."""
        day = current_day_name()
        return self.list_entries(faculty=faculty, day=day)
