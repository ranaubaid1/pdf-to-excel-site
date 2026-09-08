@echo off
title STATEXCEL - Bank Statement to Excel Converter
echo ===================================================
echo           STATEXCEL v2.0 Pro Startup
echo ===================================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ and check "Add Python to PATH".
    pause
    exit /b 1
)

echo Installing / Verifying requirements...
pip install -r requirements.txt

echo.
echo Starting STATEXCEL Server on http://localhost:5000 ...
echo Press Ctrl+C in this window to stop the server.
echo.

start http://localhost:5000
python backend/app.py
pause
