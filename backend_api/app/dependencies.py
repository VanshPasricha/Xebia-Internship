"""Shared backend dependencies and service factories."""

from __future__ import annotations

from services.attendance_service import AttendanceService
from services.faculty_service import FacultyService
from services.student_service import StudentService
from services.timetable_service import TimetableService


def get_student_service() -> StudentService:
    return StudentService()


def get_faculty_service() -> FacultyService:
    return FacultyService()


def get_timetable_service() -> TimetableService:
    return TimetableService()


def get_attendance_service() -> AttendanceService:
    return AttendanceService()
