@echo off
title STATEXCEL - Bank Statement Converter

:: Always set current directory to the folder where start.bat lives
cd /d "%~dp0"

echo ===================================================
echo           STATEXCEL v2.0 Pro Startup
echo ===================================================
echo Working Directory: %CD%
echo.

:: 1. Detect Python executable
set "PYTHON_CMD="

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :PYTHON_FOUND
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    goto :PYTHON_FOUND
)

:: Search common installation paths
for %%P in ("%LOCALAPPDATA%\Programs\Python\Python3*\python.exe" "C:\Program Files\Python3*\python.exe" "C:\Python3*\python.exe") do (
    if exist "%%~P" (
        set "PYTHON_CMD=%%~P"
        goto :PYTHON_FOUND
    )
)

:PYTHON_NOT_FOUND
echo [ERROR] Python was not found on this computer!
echo.
echo Please install Python 3.10+ from: https://www.python.org/downloads/
echo (IMPORTANT: Check the box "Add Python to PATH" during installation)
echo.
pause
exit /b 1

:PYTHON_FOUND
echo Python detected:
%PYTHON_CMD% --version
echo.

:: 2. Install / verify dependencies
echo Checking required packages...
%PYTHON_CMD% -m pip install -r requirements.txt --quiet

:: 3. Launching Server & Browser
echo.
echo ===================================================
echo Starting STATEXCEL Server on http://localhost:5000
echo (Please keep this window open while using the app)
echo ===================================================
echo.

start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:5000"

%PYTHON_CMD% backend/app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server encountered an issue and stopped.
    pause
)
