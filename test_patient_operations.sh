#!/bin/bash
# Test script for Hospital Management System Patient Operations

echo "=========================================="
echo "Hospital Management System - Patient Operations Test"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Run headless patient operations test
echo "Running headless patient operations test..."
echo ""
python3 test_patient_operations.py --headless

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All patient operation tests passed!"
else
    echo ""
    echo "❌ Some patient operation tests failed. Check the output above for details."
    exit 1
fi

