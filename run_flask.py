"""
Hospital Management System - Flask API Entry Point
Run this file to start the Flask web server
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.api import app
from utils.logger import log_info

if __name__ == '__main__':
    log_info("=" * 60)
    log_info("Starting Hospital Management System - Flask Server")
    log_info("Web Interface: http://127.0.0.1:5000")
    log_info("API Endpoints: http://127.0.0.1:5000/api/")
    log_info("Health Check: http://127.0.0.1:5000/api/health")
    log_info("=" * 60)
    
    # Run Flask app
    # Set debug=False for production
    app.run(host='127.0.0.1', port=5000, debug=True)

