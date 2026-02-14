"""
Hospital Management System - Flask API + Desktop App Entry Point

- Local: run_flask.py starts Flask in background + opens same desktop app as app.py
- Deploy (e.g. Render): set PORT in env → runs Flask only (no GUI) on 0.0.0.0:PORT
"""
import sys
import os
import threading
import time

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.api import app
from utils.logger import log_info

# Render (and similar hosts) set PORT. No display on cloud → run Flask only.
# Set FORCE_DESKTOP=1 (e.g. on Replit) to run Flask + Tkinter even when PORT is set.
DEPLOY_PORT = os.environ.get("PORT")
FORCE_DESKTOP = os.environ.get("FORCE_DESKTOP", "").lower() in ("1", "true", "yes")
IS_DEPLOYED = DEPLOY_PORT is not None and not FORCE_DESKTOP


def run_flask():
    """Run Flask server (host/port from env on Render/Replit)."""
    # Use 0.0.0.0 when deployed or when PORT is set (e.g. Replit webview)
    host = "0.0.0.0" if (IS_DEPLOYED or (FORCE_DESKTOP and DEPLOY_PORT)) else "127.0.0.1"
    port = int(DEPLOY_PORT) if DEPLOY_PORT else 5000
    app.run(host=host, port=port, debug=not IS_DEPLOYED, use_reloader=False)


def main():
    if IS_DEPLOYED:
        log_info("=" * 60)
        log_info("Hospital Management System - Flask Server (deployed)")
        log_info(f"Listening on 0.0.0.0:{DEPLOY_PORT}")
        log_info("=" * 60)
        run_flask()
    else:
        log_info("=" * 60)
        log_info("Starting Hospital Management System - Flask Server + Desktop App")
        log_info("Web Interface: http://127.0.0.1:5000")
        log_info("API Endpoints: http://127.0.0.1:5000/api/")
        log_info("Opening same desktop app as app.py...")
        log_info("=" * 60)
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        time.sleep(1)
        from frontend.main import main as run_desktop
        run_desktop()


if __name__ == "__main__":
    main()

