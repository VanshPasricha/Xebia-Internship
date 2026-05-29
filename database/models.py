"""Dataclass models used by the services and GUI layer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FacultyUser:
    id: int
    username: str
    name: str
    role: str


@dataclass(slots=True)
class Student:
    id: int
    roll_no: str
    name: str
    department: str
    year: int
    section: str
    password_hash: str
    encoding: str
    face_image_dir: str
    red_flags: int
    created_at: str


@dataclass(slots=True)
class TimetableEntry:
    id: int
    subject: str
    faculty: str
    day: str
    start_time: str
    end_time: str
    section: str


@dataclass(slots=True)
class AttendanceRecord:
    id: int
    roll_no: str
    name: str
    subject: str
    date: str
    time: str
    status: str
    late_flags: int


@dataclass(slots=True)
class AttendanceSummary:
    subject: str
    present: int
    total: int
    percentage: float
    late_flags: int
