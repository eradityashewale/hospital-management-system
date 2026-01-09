"""
Hospital Management System - Main Entry Point
Run this file to start the application
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the main application
from frontend.main import main

if __name__ == "__main__":
    main()
