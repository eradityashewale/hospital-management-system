#!/bin/bash
# Test script for Hospital Management System Buttons

echo "=========================================="
echo "Hospital Management System - Button Test"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Run headless button test
echo "Running headless button test..."
echo ""
python3 test_buttons.py --headless

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All button tests passed!"
else
    echo ""
    echo "❌ Some button tests failed. Check the output above for details."
    exit 1
fi

