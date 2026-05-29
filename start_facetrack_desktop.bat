@echo off
setlocal
cd /d "%~dp0"

if exist "dist\FACETRACK\FACETRACK.exe" (
  echo Starting FACETRACK desktop executable...
  start "" "dist\FACETRACK\FACETRACK.exe"
  exit /b 0
)

echo Desktop executable not found. Falling back to Python runtime...
python main.py
