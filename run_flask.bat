@echo off
REM Hospital Management System - Flask API Startup Script (Windows)

echo ============================================================
echo Hospital Management System - Flask API
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Flask not found. Installing dependencies...
    pip install flask flask-cors
    if errorlevel 1 (
        echo Error: Failed to install Flask dependencies
        pause
        exit /b 1
    )
)

echo Starting Flask API Server...
echo.
echo API will be available at: http://127.0.0.1:5000
echo API Health Check: http://127.0.0.1:5000/api/health
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Run Flask app
python run_flask.py

pause



