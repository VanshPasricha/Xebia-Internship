@echo off
setlocal
cd /d "%~dp0"

echo Installing PyInstaller if needed...
python -m pip install -r requirements-packaging.txt
if errorlevel 1 goto :error

echo Building FACETRACK desktop executable...
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --name FACETRACK ^
  --add-data "gui\\assets;gui\\assets" ^
  --add-data "data;data" ^
  main.py
if errorlevel 1 goto :error

echo.
echo Desktop executable created at:
echo dist\FACETRACK\FACETRACK.exe
pause
exit /b 0

:error
echo.
echo Desktop executable build failed.
pause
exit /b 1
