@echo off
setlocal
cd /d "%~dp0"

echo Starting FACETRACK backend for local network access...
start "FACETRACK Mobile Server" cmd /k "set FACETRACK_SERVER_HOST=0.0.0.0 && python api_server.py"

timeout /t 3 /nobreak >nul

echo.
echo If the web app is already built, open one of these on your phone:
echo http://localhost:8000
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254*' } | Select-Object -ExpandProperty IPAddress"
echo.
echo Use the shown IPv4 address with :8000 on the same Wi-Fi.
echo Example: http://YOUR-IP:8000
pause
