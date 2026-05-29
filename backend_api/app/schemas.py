"""Pydantic schemas for the FACETRACK backend API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FacultyOut(BaseModel):
    id: int
    username: str
    name: str
    role: str


class StudentOut(BaseModel):
    id: int
    roll_no: str
    name: str
    department: str
    year: int
    section: str
    red_flags: int
    created_at: str


class AttendanceSummaryOut(BaseModel):
    subject: str
    present: int
    total: int
    percentage: float
    late_flags: int


class StudentAttendanceSummaryResponse(BaseModel):
    roll_no: str
    overall_percentage: float
    subject_summaries: list[AttendanceSummaryOut]


class TimetableEntryOut(BaseModel):
    id: int
    subject: str
    faculty: str
    day: str
    start_time: str
    end_time: str
    section: str


class AttendanceRecordOut(BaseModel):
    id: int
    roll_no: str
    name: str
    subject: str
    date: str
    time: str
    status: str
    late_flags: int


class LateFlagReportRow(BaseModel):
    roll_no: str
    name: str
    section: str
    red_flags: int
    total_late_flags: int


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    role: str = Field(pattern="^(admin|faculty|student)$")


class AuthUserOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    username: str | None = None
    roll_no: str | None = None
    name: str
    role: str
    department: str | None = None
    year: int | None = None
    section: str | None = None
    red_flags: int | None = None


class LoginResponse(BaseModel):
    access_type: str
    user: AuthUserOut


class FacultyCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    role: str = Field(default="faculty", pattern="^(admin|faculty)$")


class FacultyMutationResponse(BaseModel):
    success: bool
    message: str


class TimetableCreateRequest(BaseModel):
    subject: str = Field(min_length=1)
    faculty: str = Field(min_length=1)
    day: str = Field(min_length=1)
    start_time: str = Field(min_length=1)
    end_time: str = Field(min_length=1)
    section: str = Field(min_length=1)


class TimetableUpdateRequest(TimetableCreateRequest):
    id: int


class TimetableMutationResponse(BaseModel):
    success: bool
    message: str


class StudentCreateRequest(BaseModel):
    roll_no: str = Field(min_length=1)
    name: str = Field(min_length=1)
    department: str = Field(min_length=1)
    year: int
    section: str = Field(min_length=1)
    password: str = Field(min_length=1)
    serialized_encoding: str = Field(min_length=1)
    face_image_dir: str = ""


class StudentUpdateRequest(BaseModel):
    roll_no: str = Field(min_length=1)
    name: str = Field(min_length=1)
    department: str = Field(min_length=1)
    year: int
    section: str = Field(min_length=1)
    password: str = ""


class StudentMutationResponse(BaseModel):
    success: bool
    message: str


class StudentEncodingOut(BaseModel):
    roll_no: str
    name: str
    section: str
    department: str
    year: int
    red_flags: int
    encodings: list[list[float]]


class AttendanceSeedRequest(BaseModel):
    timetable_id: int


class AttendanceMarkRequest(BaseModel):
    timetable_id: int
    roll_no: str = Field(min_length=1)


class AttendanceMutationResponse(BaseModel):
    success: bool
    message: str
