"""Reporting endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend_api.app.dependencies import get_attendance_service
from backend_api.app.schemas import LateFlagReportRow
from services.attendance_service import AttendanceService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/late-flags", response_model=list[LateFlagReportRow])
def late_flag_report(attendance_service: AttendanceService = Depends(get_attendance_service)) -> list[LateFlagReportRow]:
    rows = attendance_service.get_late_student_report()
    return [LateFlagReportRow(**row) for row in rows]
