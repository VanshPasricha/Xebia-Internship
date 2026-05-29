# FACETRACK

University Face Attendance System

FACETRACK is a desktop ERP-style identity and attendance system for faculty-driven student attendance using face recognition. Faculty controls student registration, timetable management, and attendance sessions. Students get read-only access to profile, timetable, and attendance analytics.

## Features

- Role-based login for admin, faculty, and students
- Admin-managed faculty registration and timetable assignment
- Faculty-controlled attendance sessions for assigned classes only
- Student registration with webcam face sample capture
- Embedding-based student recognition with Euclidean distance matching
- Weekly timetable creation and today-class attendance workflow
- Duplicate attendance prevention
- Faculty reports with CSV export
- Student dashboard with profile, timetable, and attendance percentage
- SQLite persistence and file logging

## Project Structure

```text
FACETRACK/
|-- main.py
|-- setup_database.py
|-- backend_api/
|   |-- app/
|   |-- requirements.txt
|   |-- README.md
|-- web_app/
|   |-- src/
|   |-- package.json
|   |-- README.md
|-- gui/
|   |-- login_window.py
|   |-- faculty_dashboard.py
|   |-- student_dashboard.py
|   |-- register_student.py
|   |-- attendance_page.py
|   |-- timetable_page.py
|-- face_engine/
|   |-- face_capture.py
|   |-- face_encode.py
|   |-- face_recognizer.py
|-- database/
|   |-- db.py
|   |-- models.py
|-- services/
|   |-- attendance_service.py
|   |-- timetable_service.py
|   |-- student_service.py
|   |-- faculty_service.py
|-- utils/
|   |-- config.py
|   |-- helpers.py
|-- data/
|   |-- faces/
|   |-- database.db
|-- requirements.txt
```

## Setup

1. Install Git LFS before cloning or pulling the repository assets:

```bash
git lfs install
```

If Git LFS is not installed on your machine yet, download it from [git-lfs.com](https://git-lfs.com/) and then run the command above once.

2. Clone the repository:

```bash
git clone https://github.com/Mohakkalra03/FaceTrack.git
cd FaceTrack
```

3. Create and activate a virtual environment.
4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Optional database bootstrap:

```bash
python setup_database.py
```

6. Run the application:

```bash
python main.py
```

7. Run the shared backend API from the project root if you want desktop + web integration:

```bash
python api_server.py
```

## One-Click Launchers

- Double-click [start_facetrack_desktop.bat](C:/Users/DELL/OneDrive/Desktop/Sem4/DTI/start_facetrack_desktop.bat) to start backend + desktop app together.
- Run [build_web_app.bat](C:/Users/DELL/OneDrive/Desktop/Sem4/DTI/build_web_app.bat) once to create the production web bundle.
- Double-click [start_facetrack_mobile.bat](C:/Users/DELL/OneDrive/Desktop/Sem4/DTI/start_facetrack_mobile.bat) to expose the built web portal on your local Wi-Fi.

## EXE Builds

- Run [build_desktop_exe.bat](C:/Users/DELL/OneDrive/Desktop/Sem4/DTI/build_desktop_exe.bat) to create `dist\FACETRACK\FACETRACK.exe`
- Run [build_portal_exe.bat](C:/Users/DELL/OneDrive/Desktop/Sem4/DTI/build_portal_exe.bat) to create `dist\FACETRACK-Portal\FACETRACK-Portal.exe`
- Run [start_portal_exe.bat](C:/Users/DELL/OneDrive/Desktop/Sem4/DTI/start_portal_exe.bat) after building the portal exe to serve the student portal for phone access on your local Wi-Fi

## Default Admin Login

- Username: `admin`
- Password: `admin123`

## Notes

- `face_recognition` is used when available. If it is not installed successfully on the local machine, FACETRACK falls back to a simplified OpenCV-based embedding mode so the application still runs for demonstration and testing.
- Attendance can only be started by faculty after selecting one of today's timetable classes.
- Student accounts cannot create attendance, alter timetable data, or modify institutional records.
- A shared backend scaffold now exists in [backend_api/README.md](C:/Users/DELL/OneDrive/Desktop/Sem4/DTI/backend_api/README.md) for future desktop + web architecture.
- A first student web portal scaffold now exists in [web_app/README.md](C:/Users/DELL/OneDrive/Desktop/Sem4/DTI/web_app/README.md).
- The desktop app now prefers backend API reads for login, dashboard summaries, reports, and read-only timetable/student views when the backend is running, and falls back to local services if the backend is unavailable.
- A permanent public website link is not something the local machine can create by itself; that requires external hosting or a domain. The current project now supports a one-click local-network mobile link from your laptop.
- The desktop executable and portal executable require PyInstaller, which is installed automatically by the provided build scripts.
