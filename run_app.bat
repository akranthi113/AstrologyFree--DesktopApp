@echo off
setlocal
title Kundli Generator Runner

echo ==========================================
echo    Kundli Generator - Starter Script
echo ==========================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from python.org
    pause
    exit /b
)

:: Check for virtual environment
if not exist .venv (
    echo [INFO] Virtual environment not found. Creating one...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b
    )
)

:: Install/Update dependencies
echo [INFO] Verifying dependencies...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies failed to install. 
    echo Checking if the app can still run...
)

echo.
echo [SUCCESS] Starting the application...
echo.
echo [NOTE] The application is now running as a standalone desktop window.
echo [NOTE] Keep this window open while using the app.
echo [NOTE] Press CTRL+C or close the desktop window to stop.
echo.

:: Run the app via launcher
.venv\Scripts\python.exe -m backend.launcher

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The application crashed or failed to start.
    pause
)

endlocal
