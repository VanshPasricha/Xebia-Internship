@echo off
setlocal
cd /d "%~dp0"

echo Building student portal static bundle...
call build_web_app.bat
if errorlevel 1 goto :error

echo Installing PyInstaller if needed...
python -m pip install -r requirements-packaging.txt
if errorlevel 1 goto :error

echo Building FACETRACK portal server executable...
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --name FACETRACK-Portal ^
  --add-data "web_app\\dist;web_app\\dist" ^
  --add-data "gui\\assets;gui\\assets" ^
  --add-data "data;data" ^
  api_server.py
if errorlevel 1 goto :error

echo.
echo Portal server executable created at:
echo dist\FACETRACK-Portal\FACETRACK-Portal.exe
pause
exit /b 0

:error
echo.
echo Portal executable build failed.
pause
exit /b 1
