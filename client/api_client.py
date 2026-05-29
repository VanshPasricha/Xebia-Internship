"""Minimal desktop HTTP client for the FACETRACK backend API."""

from __future__ import annotations

import json
from urllib import error, parse, request

from utils.config import BACKEND_API_BASE_URL, BACKEND_API_ENABLED, BACKEND_API_TIMEOUT_SECONDS


class BackendApiError(RuntimeError):
    """Raised when the backend API is unavailable or returns an error."""


class BackendApiClient:
    """Small JSON HTTP client used by the desktop app."""

    def __init__(self, base_url: str = BACKEND_API_BASE_URL, timeout: int = BACKEND_API_TIMEOUT_SECONDS) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.enabled = BACKEND_API_ENABLED

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict | list:
        if not self.enabled:
            raise BackendApiError("Backend API disabled for desktop runtime.")

        url = f"{self.base_url}{path}"
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = request.Request(url, data=body, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except error.HTTPError as exc:
            detail = exc.reason
            try:
                payload = json.loads(exc.read().decode("utf-8"))
                detail = payload.get("detail", detail)
            except Exception:
                pass
            raise BackendApiError(str(detail)) from exc
        except Exception as exc:
            raise BackendApiError(str(exc)) from exc

    def health(self) -> dict:
        return self._request("GET", "/health")

    def login(self, username: str, password: str, role: str) -> dict:
        return self._request("POST", "/auth/login", {"username": username, "password": password, "role": role})

    def list_faculty(self, include_admin: bool = True) -> list[dict]:
        query = parse.urlencode({"include_admin": str(include_admin).lower()})
        return self._request("GET", f"/faculty?{query}")

    def list_students(self) -> list[dict]:
        return self._request("GET", "/students")

    def list_student_encodings(self, section: str | None = None) -> list[dict]:
        query = f"?{parse.urlencode({'section': section})}" if section else ""
        return self._request("GET", f"/students/encodings{query}")

    def get_student(self, roll_no: str) -> dict:
        return self._request("GET", f"/students/{parse.quote(roll_no)}")

    def get_student_attendance_summary(self, roll_no: str) -> dict:
        return self._request("GET", f"/students/{parse.quote(roll_no)}/attendance-summary")

    def get_timetable(self, faculty: str | None = None, section: str | None = None, day: str | None = None) -> list[dict]:
        params = {}
        if faculty:
            params["faculty"] = faculty
        if section:
            params["section"] = section
        if day:
            params["day"] = day
        query = f"?{parse.urlencode(params)}" if params else ""
        return self._request("GET", f"/timetable{query}")

    def get_today_classes(self, faculty: str | None = None) -> list[dict]:
        query = f"?{parse.urlencode({'faculty': faculty})}" if faculty else ""
        return self._request("GET", f"/timetable/today{query}")

    def get_attendance_records(self, roll_no: str | None = None, subject: str | None = None) -> list[dict]:
        params = {}
        if roll_no:
            params["roll_no"] = roll_no
        if subject:
            params["subject"] = subject
        query = f"?{parse.urlencode(params)}" if params else ""
        return self._request("GET", f"/attendance{query}")

    def get_late_flag_report(self) -> list[dict]:
        return self._request("GET", "/reports/late-flags")

    def create_faculty(self, name: str, username: str, password: str, role: str = "faculty") -> dict:
        return self._request(
            "POST",
            "/faculty",
            {"name": name, "username": username, "password": password, "role": role},
        )

    def delete_faculty(self, username: str) -> dict:
        return self._request("DELETE", f"/faculty/{parse.quote(username)}")

    def create_student(self, payload: dict) -> dict:
        return self._request("POST", "/students", payload)

    def update_student(self, roll_no: str, payload: dict) -> dict:
        return self._request("PUT", f"/students/{parse.quote(roll_no)}", payload)

    def delete_student(self, roll_no: str) -> dict:
        return self._request("DELETE", f"/students/{parse.quote(roll_no)}")

    def create_timetable_entry(self, payload: dict) -> dict:
        return self._request("POST", "/timetable", payload)

    def update_timetable_entry(self, entry_id: int, payload: dict) -> dict:
        return self._request("PUT", f"/timetable/{entry_id}", payload)

    def delete_timetable_entry(self, entry_id: int) -> dict:
        return self._request("DELETE", f"/timetable/{entry_id}")

    def seed_attendance_session(self, timetable_id: int) -> dict:
        return self._request("POST", "/attendance/session/seed", {"timetable_id": timetable_id})

    def mark_attendance(self, timetable_id: int, roll_no: str) -> dict:
        return self._request("POST", "/attendance/mark", {"timetable_id": timetable_id, "roll_no": roll_no})
