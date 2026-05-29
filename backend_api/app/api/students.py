"""Student endpoints for desktop/web clients."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend_api.app.dependencies import get_student_service
from backend_api.app.schemas import (
    StudentAttendanceSummaryResponse,
    StudentCreateRequest,
    StudentEncodingOut,
    StudentMutationResponse,
    StudentOut,
    StudentUpdateRequest,
)
from services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=list[StudentOut])
def list_students(student_service: StudentService = Depends(get_student_service)) -> list[StudentOut]:
    return [
        StudentOut(
            id=student.id,
            roll_no=student.roll_no,
            name=student.name,
            department=student.department,
            year=student.year,
            section=student.section,
            red_flags=student.red_flags,
            created_at=student.created_at,
        )
        for student in student_service.list_students()
    ]


@router.get("/encodings", response_model=list[StudentEncodingOut])
def list_student_encodings(
    section: str | None = None,
    student_service: StudentService = Depends(get_student_service),
) -> list[StudentEncodingOut]:
    rows = student_service.get_all_student_encodings()
    if section:
        rows = [row for row in rows if row["section"] == section]
    return [
        StudentEncodingOut(
            roll_no=row["roll_no"],
            name=row["name"],
            section=row["section"],
            department=row["department"],
            year=row["year"],
            red_flags=row["red_flags"],
            encodings=[encoding.astype(float).tolist() for encoding in row["encodings"]],
        )
        for row in rows
    ]


@router.get("/{roll_no}", response_model=StudentOut)
def get_student(roll_no: str, student_service: StudentService = Depends(get_student_service)) -> StudentOut:
    student = student_service.get_student_by_roll(roll_no.upper())
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return StudentOut(
        id=student.id,
        roll_no=student.roll_no,
        name=student.name,
        department=student.department,
        year=student.year,
        section=student.section,
        red_flags=student.red_flags,
        created_at=student.created_at,
    )


@router.get("/{roll_no}/attendance-summary", response_model=StudentAttendanceSummaryResponse)
def get_student_attendance_summary(
    roll_no: str,
    student_service: StudentService = Depends(get_student_service),
) -> StudentAttendanceSummaryResponse:
    student = student_service.get_student_by_roll(roll_no.upper())
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    overall, subject_summaries = student_service.get_attendance_summary(student.roll_no)
    return StudentAttendanceSummaryResponse(
        roll_no=student.roll_no,
        overall_percentage=overall,
        subject_summaries=[
            {
                "subject": item.subject,
                "present": item.present,
                "total": item.total,
                "percentage": item.percentage,
                "late_flags": item.late_flags,
            }
            for item in subject_summaries
        ],
    )


@router.post("", response_model=StudentMutationResponse)
def create_student(
    payload: StudentCreateRequest,
    student_service: StudentService = Depends(get_student_service),
) -> StudentMutationResponse:
    success, message = student_service.register_student_payload(
        {
            "roll_no": payload.roll_no.upper(),
            "name": payload.name,
            "department": payload.department,
            "year": payload.year,
            "section": payload.section.upper(),
            "password": payload.password,
            "face_image_dir": payload.face_image_dir,
        },
        payload.serialized_encoding,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return StudentMutationResponse(success=success, message=message)


@router.put("/{roll_no}", response_model=StudentMutationResponse)
def update_student(
    roll_no: str,
    payload: StudentUpdateRequest,
    student_service: StudentService = Depends(get_student_service),
) -> StudentMutationResponse:
    success, message = student_service.update_student_profile(
        roll_no.upper(),
        {
            "roll_no": payload.roll_no.upper(),
            "name": payload.name,
            "department": payload.department,
            "year": payload.year,
            "section": payload.section.upper(),
            "password": payload.password,
        },
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return StudentMutationResponse(success=success, message=message)


@router.delete("/{roll_no}", response_model=StudentMutationResponse)
def delete_student(roll_no: str, student_service: StudentService = Depends(get_student_service)) -> StudentMutationResponse:
    success, message = student_service.delete_student(roll_no.upper())
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    return StudentMutationResponse(success=success, message=message)
