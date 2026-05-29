"""Student management and authentication service."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any

import numpy as np

from database.db import db_manager
from database.models import AttendanceSummary, Student
from services.attendance_service import RED_FLAGS_PER_DEDUCTION
from utils.helpers import deserialize_encodings, hash_password, safe_percentage, serialize_encodings

LOGGER = logging.getLogger(__name__)


class StudentService:
    """Manage student records and student-facing queries."""

    def register_student_payload(self, student_data: dict[str, Any], serialized_encoding: str) -> tuple[bool, str]:
        """Insert a new student when encodings are already serialized upstream."""
        if not serialized_encoding:
            return False, "At least one face encoding is required."

        with db_manager.connection() as conn:
            exists = conn.execute("SELECT 1 FROM Students WHERE roll_no = ?", (student_data["roll_no"],)).fetchone()
            if exists:
                return False, "Roll number already exists."

            conn.execute(
                """
                INSERT INTO Students(roll_no, name, department, year, section, password_hash, encoding, face_image_dir)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    student_data["roll_no"],
                    student_data["name"],
                    student_data["department"],
                    student_data["year"],
                    student_data["section"],
                    hash_password(student_data["password"]),
                    serialized_encoding,
                    student_data.get("face_image_dir", ""),
                ),
            )
        LOGGER.info("Registered student %s via serialized payload", student_data["roll_no"])
        return True, "Student registered successfully."

    def register_student(self, student_data: dict[str, Any], encodings: list[np.ndarray]) -> tuple[bool, str]:
        """Insert a new student with pre-computed facial embeddings."""
        if not encodings:
            return False, "At least one face encoding is required."

        with db_manager.connection() as conn:
            exists = conn.execute("SELECT 1 FROM Students WHERE roll_no = ?", (student_data["roll_no"],)).fetchone()
            if exists:
                return False, "Roll number already exists."

            conn.execute(
                """
                INSERT INTO Students(roll_no, name, department, year, section, password_hash, encoding, face_image_dir)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    student_data["roll_no"],
                    student_data["name"],
                    student_data["department"],
                    student_data["year"],
                    student_data["section"],
                    hash_password(student_data["password"]),
                    serialize_encodings(encodings),
                    student_data.get("face_image_dir", ""),
                ),
            )
        LOGGER.info("Registered student %s", student_data["roll_no"])
        return True, "Student registered successfully."

    def update_student_profile(self, roll_no: str, updates: dict[str, Any]) -> tuple[bool, str]:
        """Update editable student profile fields without changing face encodings."""
        with db_manager.connection() as conn:
            existing = conn.execute("SELECT * FROM Students WHERE roll_no = ?", (roll_no,)).fetchone()
            if not existing:
                return False, "Student not found."

            new_roll_no = updates["roll_no"]
            if new_roll_no != roll_no:
                duplicate = conn.execute("SELECT 1 FROM Students WHERE roll_no = ?", (new_roll_no,)).fetchone()
                if duplicate:
                    return False, "New roll number already exists."

            password_hash_value = existing["password_hash"]
            if updates.get("password"):
                password_hash_value = hash_password(updates["password"])

            conn.execute(
                """
                UPDATE Students
                SET roll_no = ?, name = ?, department = ?, year = ?, section = ?, password_hash = ?
                WHERE roll_no = ?
                """,
                (
                    new_roll_no,
                    updates["name"],
                    updates["department"],
                    updates["year"],
                    updates["section"],
                    password_hash_value,
                    roll_no,
                ),
            )
            conn.execute("UPDATE Attendance SET roll_no = ?, name = ? WHERE roll_no = ?", (new_roll_no, updates["name"], roll_no))

            face_dir = existing["face_image_dir"]
            if face_dir and new_roll_no != roll_no:
                current_path = Path(face_dir)
                if current_path.exists():
                    target_path = current_path.parent / new_roll_no
                    current_path.rename(target_path)
                    conn.execute("UPDATE Students SET face_image_dir = ? WHERE roll_no = ?", (str(target_path), new_roll_no))

        LOGGER.info("Updated student profile %s -> %s", roll_no, updates["roll_no"])
        return True, "Student profile updated successfully."

    def delete_student(self, roll_no: str) -> tuple[bool, str]:
        """Delete a student record, related attendance, and saved face samples."""
        with db_manager.connection() as conn:
            existing = conn.execute("SELECT face_image_dir FROM Students WHERE roll_no = ?", (roll_no,)).fetchone()
            if not existing:
                return False, "Student not found."
            conn.execute("DELETE FROM Attendance WHERE roll_no = ?", (roll_no,))
            conn.execute("DELETE FROM Students WHERE roll_no = ?", (roll_no,))

        face_dir = existing["face_image_dir"]
        if face_dir:
            shutil.rmtree(face_dir, ignore_errors=True)
        LOGGER.info("Deleted student %s", roll_no)
        return True, "Student deleted successfully."

    def authenticate_student(self, roll_no: str, password: str) -> Student | None:
        """Authenticate a student using roll number and password."""
        with db_manager.connection() as conn:
            row = conn.execute(
                "SELECT * FROM Students WHERE roll_no = ? AND password_hash = ?",
                (roll_no, hash_password(password)),
            ).fetchone()
        return Student(**dict(row)) if row else None

    def get_student_by_roll(self, roll_no: str) -> Student | None:
        """Fetch a student record by roll number."""
        with db_manager.connection() as conn:
            row = conn.execute("SELECT * FROM Students WHERE roll_no = ?", (roll_no,)).fetchone()
        return Student(**dict(row)) if row else None

    def list_students(self) -> list[Student]:
        """Return all students ordered by roll number."""
        with db_manager.connection() as conn:
            rows = conn.execute("SELECT * FROM Students ORDER BY roll_no").fetchall()
        return [Student(**dict(row)) for row in rows]

    def get_all_student_encodings(self) -> list[dict[str, Any]]:
        """Return students plus their decoded embeddings for recognition."""
        students = self.list_students()
        return [
            {
                "roll_no": student.roll_no,
                "name": student.name,
                "section": student.section,
                "department": student.department,
                "year": student.year,
                "red_flags": student.red_flags,
                "encodings": deserialize_encodings(student.encoding),
            }
            for student in students
        ]

    def get_attendance_summary(self, roll_no: str) -> tuple[float, list[AttendanceSummary]]:
        """Return overall and subject-wise attendance percentages with red-flag deductions."""
        with db_manager.connection() as conn:
            student = conn.execute("SELECT section FROM Students WHERE roll_no = ?", (roll_no,)).fetchone()
            if not student:
                return 0.0, []
            section = student["section"]

            totals = conn.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COALESCE(SUM(CASE WHEN status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present,
                    COALESCE(SUM(late_flags), 0) AS total_late_flags
                FROM Attendance
                WHERE roll_no = ?
                """,
                (roll_no,),
            ).fetchone()
            subjects = conn.execute(
                """
                SELECT DISTINCT subject FROM Timetable WHERE section = ?
                UNION
                SELECT DISTINCT subject FROM Attendance WHERE roll_no = ?
                ORDER BY subject
                """,
                (section, roll_no),
            ).fetchall()

        subject_summaries = []
        for subject_row in subjects:
            subject_name = subject_row["subject"]
            with db_manager.connection() as conn:
                row = conn.execute(
                    """
                    SELECT
                        COUNT(*) AS total,
                        COALESCE(SUM(CASE WHEN status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present,
                        COALESCE(SUM(late_flags), 0) AS total_late_flags
                    FROM Attendance
                    WHERE roll_no = ? AND subject = ?
                    """,
                    (roll_no, subject_name),
                ).fetchone()
            deductions = row["total_late_flags"] // RED_FLAGS_PER_DEDUCTION
            adjusted_present = max(0, row["present"] - deductions)
            subject_summaries.append(
                AttendanceSummary(
                    subject=subject_name,
                    present=adjusted_present,
                    total=row["total"],
                    percentage=safe_percentage(adjusted_present, row["total"]),
                    late_flags=row["total_late_flags"],
                )
            )

        overall_deductions = totals["total_late_flags"] // RED_FLAGS_PER_DEDUCTION
        adjusted_present_total = max(0, totals["present"] - overall_deductions)
        overall = safe_percentage(adjusted_present_total, totals["total"])
        return overall, subject_summaries
