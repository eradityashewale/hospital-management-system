@echo off
REM Build script for Hospital Management System executable
REM This script creates a standalone .exe file that can be distributed

echo ========================================
echo Hospital Management System - Build EXE
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

echo Step 1: Installing PyInstaller...
python -m pip install --upgrade pip
python -m pip install pyinstaller

if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo Step 2: Installing optional dependencies (reportlab for PDF generation)...
python -m pip install reportlab

echo.
echo Step 3: Building executable...
echo This may take a few minutes...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

REM Build using the spec file
pyinstaller --clean hospital_management.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Your executable is located in: dist\HospitalManagementSystem.exe
echo.
echo You can now distribute this .exe file to your colleagues.
echo Note: The .exe file is standalone and doesn't require Python to run.
echo.
echo The database (hospital.db) will be created automatically when the app runs.
echo.
pause

