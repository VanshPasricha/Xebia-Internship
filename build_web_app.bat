@echo off
setlocal
cd /d "%~dp0web_app"
call npm install
if errorlevel 1 goto :error
call npm run build
if errorlevel 1 goto :error
echo.
echo FACETRACK web app build completed.
echo Static files are ready for serving from the backend.
pause
exit /b 0

:error
echo.
echo Web app build failed.
pause
exit /b 1
