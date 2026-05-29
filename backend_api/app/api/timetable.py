"""Timetable endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi import HTTPException, status

from backend_api.app.dependencies import get_timetable_service
from backend_api.app.schemas import (
    TimetableCreateRequest,
    TimetableEntryOut,
    TimetableMutationResponse,
    TimetableUpdateRequest,
)
from services.timetable_service import TimetableService

router = APIRouter(prefix="/timetable", tags=["timetable"])


def _serialize_entry(entry) -> TimetableEntryOut:
    return TimetableEntryOut(
        id=entry.id,
        subject=entry.subject,
        faculty=entry.faculty,
        day=entry.day,
        start_time=entry.start_time,
        end_time=entry.end_time,
        section=entry.section,
    )


@router.get("", response_model=list[TimetableEntryOut])
def list_timetable(
    faculty: str | None = None,
    section: str | None = None,
    day: str | None = None,
    timetable_service: TimetableService = Depends(get_timetable_service),
) -> list[TimetableEntryOut]:
    return [_serialize_entry(entry) for entry in timetable_service.list_entries(faculty=faculty, section=section, day=day)]


@router.get("/today", response_model=list[TimetableEntryOut])
def get_today_classes(
    faculty: str | None = None,
    timetable_service: TimetableService = Depends(get_timetable_service),
) -> list[TimetableEntryOut]:
    return [_serialize_entry(entry) for entry in timetable_service.get_today_classes(faculty=faculty)]


@router.post("", response_model=TimetableMutationResponse)
def create_timetable_entry(
    payload: TimetableCreateRequest,
    timetable_service: TimetableService = Depends(get_timetable_service),
) -> TimetableMutationResponse:
    success, message = timetable_service.create_entry(
        subject=payload.subject,
        faculty=payload.faculty,
        day=payload.day,
        start_time=payload.start_time,
        end_time=payload.end_time,
        section=payload.section,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return TimetableMutationResponse(success=success, message=message)


@router.put("/{entry_id}", response_model=TimetableMutationResponse)
def update_timetable_entry(
    entry_id: int,
    payload: TimetableUpdateRequest,
    timetable_service: TimetableService = Depends(get_timetable_service),
) -> TimetableMutationResponse:
    success, message = timetable_service.update_entry(
        entry_id=entry_id,
        subject=payload.subject,
        faculty=payload.faculty,
        day=payload.day,
        start_time=payload.start_time,
        end_time=payload.end_time,
        section=payload.section,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return TimetableMutationResponse(success=success, message=message)


@router.delete("/{entry_id}", response_model=TimetableMutationResponse)
def delete_timetable_entry(
    entry_id: int,
    timetable_service: TimetableService = Depends(get_timetable_service),
) -> TimetableMutationResponse:
    success, message = timetable_service.delete_entry(entry_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    return TimetableMutationResponse(success=success, message=message)
