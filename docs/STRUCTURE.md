# Project Structure

This document shows the current organization of the codebase.

## 📁 Current Structure

```
hospital-management-system/          (Main Git Repository)
├── README.md                        ✅ Main project documentation
├── requirements.txt                 ✅ All dependencies
├── .gitignore                       ✅ Git ignore rules
│
├── backend/                         ✅ SHARED - Used by both modes
│   ├── __init__.py
│   ├── database.py                 (Shared database logic)
│   └── api.py                      (Flask API - for online mode)
│
├── frontend/                        ✅ Desktop - Offline mode
│   ├── __init__.py
│   ├── main.py                     (Tkinter main app)
│   ├── login_window.py
│   └── modules/
│       ├── patient_module.py
│       ├── doctor_module.py
│       ├── appointment_module.py
│       ├── prescription_module.py
│       ├── billing_module.py
│       └── reports_module.py
│
├── web/                             ✅ Web Frontend - Online mode
│   ├── index.html                   (Main web page)
│   └── js/
│       ├── api.js                  (API client)
│       ├── patients.js
│       ├── doctors.js
│       └── app.js
│
├── utils/                           ✅ SHARED utilities
│   ├── __init__.py
│   ├── logger.py
│   └── helpers.py
│
├── scripts/                         ✅ Utility scripts
│   ├── import_medicines.py
│   ├── generate_fake_data.py
│   └── ...
│
├── docs/                            ✅ Documentation
│   ├── CODE_ORGANIZATION_GUIDE.md
│   ├── ARCHITECTURE_EXPLANATION.md
│   ├── FLASK_API_README.md
│   ├── WEB_FRONTEND_OPTIONS.md
│   └── ...
│
├── app.py                           ✅ Desktop entry point
├── run_flask.py                     ✅ Web API entry point
├── run.bat                          (Desktop startup - Windows)
├── run.sh                           (Desktop startup - Linux/Mac)
├── run_flask.bat                    (Web API startup - Windows)
└── run_flask.sh                     (Web API startup - Linux/Mac)
```

## ✅ Structure Verification

- [x] **Backend** (`backend/`) - Shared code for both modes
- [x] **Frontend** (`frontend/`) - Desktop Tkinter application
- [x] **Web** (`web/`) - Web frontend (HTML/JS)
- [x] **Utils** (`utils/`) - Shared utilities
- [x] **Scripts** (`scripts/`) - Utility scripts
- [x] **Docs** (`docs/`) - All documentation
- [x] **Entry Points** - `app.py` (desktop) and `run_flask.py` (web)

## 🎯 Key Points

1. **Single Repository**: Everything in one codebase
2. **Shared Backend**: `backend/database.py` used by both desktop and web
3. **Separate Frontends**: Desktop (`frontend/`) and Web (`web/`)
4. **Clear Entry Points**: `app.py` for desktop, `run_flask.py` for web
5. **Organized Docs**: All documentation in `docs/` folder

This structure follows the recommended monorepo pattern and makes it easy to maintain both offline and online modes! ✅




