@echo off
setlocal
cd /d "%~dp0"

if exist "dist\FACETRACK-Portal\FACETRACK-Portal.exe" (
  call start_portal_exe.bat
  exit /b %errorlevel%
)

echo Portal executable not found. Start build_portal_exe.bat first.
pause
exit /b 1
