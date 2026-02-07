#!/bin/bash
# Hospital Management System - Startup Script

echo "Starting Hospital Management System..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Run the application
python3 app.py

