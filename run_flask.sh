#!/bin/bash
# Hospital Management System - Flask API Startup Script (Linux/Mac)

echo "============================================================"
echo "Hospital Management System - Flask API"
echo "============================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Check if Flask is installed
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Flask not found. Installing dependencies..."
    pip3 install flask flask-cors
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install Flask dependencies"
        exit 1
    fi
fi

echo "Starting Flask API Server..."
echo ""
echo "API will be available at: http://127.0.0.1:5000"
echo "API Health Check: http://127.0.0.1:5000/api/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Run Flask app
python3 run_flask.py



