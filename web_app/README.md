# FACETRACK Web App

Initial student-facing web portal for the FACETRACK shared architecture.

## Scope

This first web version is intentionally limited to the student portal:

- student login
- profile view
- subject-wise attendance summary
- attendance records
- timetable view
- red flag visibility

Attendance marking and live face recognition remain in the desktop app.

## Run

```bash
cd web_app
npm install
npm run dev
```

## Build For Single-Server Runtime

```bash
cd web_app
npm install
npm run build
```

After build, the FastAPI backend can serve the web app directly from `web_app/dist`.

## Backend Requirement

Start the backend API first:

```bash
pip install -r backend_api/requirements.txt
uvicorn backend_api.app.main:app --reload
```

The web app currently expects the backend at:

`http://127.0.0.1:8000`

The Vite dev server proxies `/api` to the backend automatically.
