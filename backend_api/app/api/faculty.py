"""Faculty management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend_api.app.dependencies import get_faculty_service
from backend_api.app.schemas import FacultyCreateRequest, FacultyMutationResponse, FacultyOut
from services.faculty_service import FacultyService

router = APIRouter(prefix="/faculty", tags=["faculty"])


@router.get("", response_model=list[FacultyOut])
def list_faculty(include_admin: bool = True, faculty_service: FacultyService = Depends(get_faculty_service)) -> list[FacultyOut]:
    return [
        FacultyOut(
            id=faculty.id,
            username=faculty.username,
            name=faculty.name,
            role=faculty.role,
        )
        for faculty in faculty_service.list_faculty(include_admin=include_admin)
    ]


@router.post("", response_model=FacultyMutationResponse)
def create_faculty(
    payload: FacultyCreateRequest,
    faculty_service: FacultyService = Depends(get_faculty_service),
) -> FacultyMutationResponse:
    success, message = faculty_service.create_faculty(
        name=payload.name,
        username=payload.username,
        password=payload.password,
        role=payload.role,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return FacultyMutationResponse(success=success, message=message)


@router.delete("/{username}", response_model=FacultyMutationResponse)
def delete_faculty(username: str, faculty_service: FacultyService = Depends(get_faculty_service)) -> FacultyMutationResponse:
    success, message = faculty_service.delete_faculty(username)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    return FacultyMutationResponse(success=success, message=message)
