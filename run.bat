@echo off
REM Hospital Management System - Startup Script for Windows

echo Starting Hospital Management System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Run the application
python main.py

pause

