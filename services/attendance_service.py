"""Attendance workflow and reporting service."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from database.db import db_manager
from database.models import AttendanceRecord, TimetableEntry
from utils.helpers import now_time_str, today_date_str

GRACE_PERIOD_MINUTES = 5
RED_FLAGS_PER_DEDUCTION = 60


def _parse_clock_value(value: str) -> datetime:
    """Parse HH:MM or HH:MM:SS into a datetime object for same-day comparison."""
    fmt = "%H:%M:%S" if len(value.split(":")) == 3 else "%H:%M"
    return datetime.strptime(value, fmt)


def calculate_red_flags(class_start_time: str, arrival_time: str) -> int:
    """Return late flags after a 5-minute grace period."""
    class_start = _parse_clock_value(class_start_time)
    arrival = _parse_clock_value(arrival_time)
    late_minutes = int((arrival - class_start).total_seconds() // 60)
    if late_minutes <= GRACE_PERIOD_MINUTES:
        return 0
    return late_minutes - GRACE_PERIOD_MINUTES


class AttendanceService:
    """Handle attendance writes, lookups, exports, and late-flag penalties."""

    def ensure_session_records(self, timetable_entry: TimetableEntry, students: list[dict[str, str]]) -> None:
        """Seed absent records for the selected section so percentages are meaningful."""
        date_str = today_date_str()
        with db_manager.connection() as conn:
            for student in students:
                if student["section"] != timetable_entry.section:
                    continue
                exists = conn.execute(
                    "SELECT 1 FROM Attendance WHERE roll_no = ? AND subject = ? AND date = ?",
                    (student["roll_no"], timetable_entry.subject, date_str),
                ).fetchone()
                if exists:
                    continue
                conn.execute(
                    """
                    INSERT INTO Attendance(roll_no, name, subject, date, time, status, late_flags)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        student["roll_no"],
                        student["name"],
                        timetable_entry.subject,
                        date_str,
                        now_time_str(),
                        "ABSENT",
                        0,
                    ),
                )

    def mark_attendance(self, student: dict[str, str], timetable_entry: TimetableEntry) -> tuple[bool, str]:
        """Record attendance once per student per subject per date, including late flags."""
        if timetable_entry.section != student["section"]:
            return False, "Student section does not match the selected class."

        date_str = today_date_str()
        arrival_time = now_time_str()
        late_flags = calculate_red_flags(timetable_entry.start_time, arrival_time)

        with db_manager.connection() as conn:
            existing = conn.execute(
                "SELECT status FROM Attendance WHERE roll_no = ? AND subject = ? AND date = ?",
                (student["roll_no"], timetable_entry.subject, date_str),
            ).fetchone()
            if existing and existing["status"] == "PRESENT":
                return False, f"{student['roll_no']} already marked for this subject today."

            current_flags = conn.execute(
                "SELECT red_flags FROM Students WHERE roll_no = ?",
                (student["roll_no"],),
            ).fetchone()
            updated_flags_total = (current_flags["red_flags"] if current_flags else 0) + late_flags
            remaining_flags = updated_flags_total % RED_FLAGS_PER_DEDUCTION
            conn.execute(
                "UPDATE Students SET red_flags = ? WHERE roll_no = ?",
                (remaining_flags, student["roll_no"]),
            )

            if existing:
                conn.execute(
                    """
                    UPDATE Attendance
                    SET name = ?, time = ?, status = 'PRESENT', late_flags = ?
                    WHERE roll_no = ? AND subject = ? AND date = ?
                    """,
                    (
                        student["name"],
                        arrival_time,
                        late_flags,
                        student["roll_no"],
                        timetable_entry.subject,
                        date_str,
                    ),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO Attendance(roll_no, name, subject, date, time, status, late_flags)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        student["roll_no"],
                        student["name"],
                        timetable_entry.subject,
                        date_str,
                        arrival_time,
                        "PRESENT",
                        late_flags,
                    ),
                )

        if late_flags > 0:
            return True, f"Attendance marked for {student['name']} with {late_flags} red flag(s)."
        return True, f"Attendance marked for {student['name']}."

    def get_records(self, roll_no: str | None = None, subject: str | None = None) -> list[AttendanceRecord]:
        """Fetch attendance records using optional filters."""
        query = "SELECT * FROM Attendance WHERE 1=1"
        params: list[str] = []
        if roll_no:
            query += " AND roll_no = ?"
            params.append(roll_no)
        if subject:
            query += " AND subject = ?"
            params.append(subject)
        query += " ORDER BY date DESC, time DESC"

        with db_manager.connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [AttendanceRecord(**dict(row)) for row in rows]

    def get_late_student_report(self) -> list[dict[str, object]]:
        """Return red-flag totals for the faculty dashboard."""
        with db_manager.connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    s.roll_no,
                    s.name,
                    s.section,
                    s.red_flags,
                    COALESCE(SUM(a.late_flags), 0) AS total_late_flags
                FROM Students s
                LEFT JOIN Attendance a ON a.roll_no = s.roll_no
                GROUP BY s.roll_no, s.name, s.section, s.red_flags
                HAVING s.red_flags > 0 OR total_late_flags > 0
                ORDER BY total_late_flags DESC, s.roll_no
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def export_to_csv(self, destination: str | Path, records: list[AttendanceRecord]) -> Path:
        """Export the provided attendance records to CSV."""
        output = Path(destination)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Roll Number", "Name", "Subject", "Date", "Time", "Status", "Late Flags"])
            for record in records:
                writer.writerow([
                    record.roll_no,
                    record.name,
                    record.subject,
                    record.date,
                    record.time,
                    record.status,
                    record.late_flags,
                ])
        return output

    def count_total_records(self) -> int:
        """Return the total number of attendance entries."""
        with db_manager.connection() as conn:
            return conn.execute("SELECT COUNT(*) AS total FROM Attendance").fetchone()["total"]
