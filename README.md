# Hospital Management System

A comprehensive Hospital Management System supporting both **offline desktop** and **online web** modes.

## 🏗️ Project Structure

```
hospital-management-system/
├── backend/              # Shared backend (used by both modes)
│   ├── database.py       # Core database logic
│   └── api.py            # Flask REST API
│
├── frontend/             # Desktop application (Offline mode)
│   ├── main.py          # Tkinter main application
│   ├── login_window.py
│   └── modules/         # Desktop UI modules
│
├── web/                  # Web frontend (Online mode)
│   ├── index.html       # Main web page
│   └── js/              # JavaScript files
│
├── utils/                # Shared utilities
│   ├── logger.py
│   └── helpers.py
│
├── scripts/              # Utility scripts
├── docs/                 # Documentation
│
├── app.py               # Desktop app entry point
└── run_flask.py         # Web API entry point
```

## 🚀 Quick Start

### Desktop Mode (Offline)

**Windows:**
```bash
python app.py
```
or double-click `run.bat`

**Linux/Mac:**
```bash
python3 app.py
```
or `./run.sh`

**Default Login:**
- Username: `admin`
- Password: `admin`

### Web Mode (Online)

**Step 1: Install Flask dependencies**
```bash
pip install flask flask-cors
```

**Step 2: Start Flask API server**
```bash
# Windows
python run_flask.py
# or double-click run_flask.bat

# Linux/Mac
python3 run_flask.py
# or ./run_flask.sh
```

**Step 3: Open web interface**
- Open `web/index.html` in your browser
- API available at: `http://127.0.0.1:5000`

**For detailed instructions, see [HOW_TO_RUN.md](docs/HOW_TO_RUN.md)**

## 📚 Documentation

See the `docs/` folder for detailed documentation:

- **CODE_ORGANIZATION_GUIDE.md** - Code structure and organization
- **ARCHITECTURE_EXPLANATION.md** - System architecture details
- **FLASK_API_README.md** - Flask API documentation
- **WEB_FRONTEND_OPTIONS.md** - Web frontend options
- **REACT_OR_NOT_SUMMARY.md** - React vs Plain JavaScript guide
- **QUICK_DECISION_GUIDE.md** - Quick reference guide

## ✨ Features

### Both Modes Support:
- ✅ Patient Management
- ✅ Doctor Management
- ✅ Appointment Scheduling
- ✅ Prescription Management
- ✅ Billing System
- ✅ Statistics & Reports

### Desktop Mode:
- ✅ Offline operation
- ✅ Tkinter GUI
- ✅ Direct database access
- ✅ Standalone executable support

### Web Mode:
- ✅ REST API (Flask)
- ✅ Web browser interface
- ✅ Cross-platform access
- ✅ Same database as desktop

## 🗄️ Database

Both modes use the same SQLite database (`backend/hospital.db`), ensuring data consistency across platforms.

## 🛠️ Technology Stack

- **Backend**: Python, SQLite
- **Desktop UI**: Tkinter
- **Web API**: Flask
- **Web Frontend**: HTML, JavaScript

## 📝 License

[Your License Here]

## 👥 Contributors

[Your Name/Team]

