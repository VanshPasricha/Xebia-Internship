# FACETRACK Backend API

Initial shared backend scaffold for running the desktop app and a future web app against the same business logic and database.

## Run

```bash
pip install -r backend_api/requirements.txt
python api_server.py
```

Run the command from the project root:

`C:\Users\DELL\OneDrive\Desktop\Sem4\DTI`

If `web_app/dist` exists, the backend will also serve the built web portal directly on the same port.

## Available Endpoints

- `GET /api/health`
- `POST /api/auth/login`
- `GET /api/faculty`
- `POST /api/faculty`
- `DELETE /api/faculty/{username}`
- `GET /api/students`
- `GET /api/students/encodings`
- `GET /api/students/{roll_no}`
- `GET /api/students/{roll_no}/attendance-summary`
- `POST /api/students`
- `PUT /api/students/{roll_no}`
- `DELETE /api/students/{roll_no}`
- `GET /api/timetable`
- `GET /api/timetable/today`
- `POST /api/timetable`
- `PUT /api/timetable/{entry_id}`
- `DELETE /api/timetable/{entry_id}`
- `GET /api/attendance`
- `POST /api/attendance/session/seed`
- `POST /api/attendance/mark`
- `GET /api/reports/late-flags`

## Notes

- The current scaffold reuses the existing `database/` and `services/` modules.
- The desktop app now prefers backend-backed login, summaries, reports, timetable reads, admin writes, student management, and attendance session writes when the backend is running.
- Local service fallback is still present so the desktop app remains usable if the backend is offline.
- This backend is now the primary integration path for the future web and mobile-facing layers.
