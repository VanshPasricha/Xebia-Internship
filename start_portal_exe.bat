@echo off
setlocal
cd /d "%~dp0"

if not exist "dist\FACETRACK-Portal\FACETRACK-Portal.exe" (
  echo Portal executable not found. Build it first with build_portal_exe.bat
  pause
  exit /b 1
)

start "FACETRACK Portal" cmd /k "set FACETRACK_SERVER_HOST=0.0.0.0 && dist\FACETRACK-Portal\FACETRACK-Portal.exe"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8000"
echo.
echo FACETRACK portal server started.
echo Open on laptop: http://127.0.0.1:8000
echo Open on phone using your Wi-Fi IPv4: http://YOUR-IP:8000
pause
