"""
Replit: Run Flask + Desktop App (Tkinter).
Set FORCE_DESKTOP=1 so the app launches the desktop window even when Replit sets PORT.
"""
import os

os.environ["FORCE_DESKTOP"] = "1"

from run_flask import main

if __name__ == "__main__":
    main()
