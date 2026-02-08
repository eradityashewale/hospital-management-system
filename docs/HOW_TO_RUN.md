# How to Run the Hospital Management System

This guide explains how to run the system in both **Desktop (Offline)** and **Web (Online)** modes.

---

## 📋 Prerequisites

- **Python 3.7+** installed
- For Desktop mode: Python with Tkinter (usually included)
- For Web mode: Flask and flask-cors

---

## 🖥️ Option 1: Desktop Mode (Offline)

The desktop application runs locally on your computer with a Tkinter GUI.

### Quick Start:

**Windows:**
```bash
python app.py
```
or double-click:
```bash
run.bat
```

**Linux/Mac:**
```bash
python3 app.py
```
or:
```bash
chmod +x run.sh
./run.sh
```

### What Happens:
1. ✅ Database initializes automatically (`backend/hospital.db`)
2. ✅ Login window appears
3. ✅ Default credentials: `admin` / `admin`
4. ✅ Main dashboard opens after login

### Features:
- ✅ Works completely offline
- ✅ No internet connection needed
- ✅ Direct database access
- ✅ Full Tkinter GUI

---

## 🌐 Option 2: Web Mode (Online)

The web application provides a REST API and web interface.

### Step 1: Install Flask Dependencies

```bash
pip install flask flask-cors
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### Step 2: Start Flask API Server

**Windows:**
```bash
python run_flask.py
```
or:
```bash
run_flask.bat
```

**Linux/Mac:**
```bash
python3 run_flask.py
```
or:
```bash
chmod +x run_flask.sh
./run_flask.sh
```

### Step 3: Access the Web Interface

**Option A: Open Web Frontend**
1. Open `web/index.html` in your browser
2. The page will connect to `http://127.0.0.1:5000`

**Option B: Use API Directly**
- API is available at: `http://127.0.0.1:5000`
- Health check: `http://127.0.0.1:5000/api/health`
- API endpoints: See `docs/FLASK_API_README.md`

### What You'll See:

**Terminal Output:**
```
============================================================
Starting Hospital Management System - Flask API
API will be available at: http://127.0.0.1:5000
API Health Check: http://127.0.0.1:5000/api/health
============================================================
 * Running on http://127.0.0.1:5000
```

**In Browser:**
- Open `web/index.html` to see the web interface
- Or test API at `http://127.0.0.1:5000/api/health`

---

## 🔄 Running Both Modes Simultaneously

You can run both desktop and web modes at the same time!

1. **Start Desktop App** (Terminal 1):
   ```bash
   python app.py
   ```

2. **Start Web API** (Terminal 2):
   ```bash
   python run_flask.py
   ```

Both will use the same database file (`backend/hospital.db`), so data is shared! ✅

**Note:** SQLite handles multiple readers, but only one writer at a time. This works fine for most use cases.

---

## 🚀 Quick Start Commands

### Desktop Only (Offline):
```bash
# Windows
python app.py

# Linux/Mac
python3 app.py
```

### Web Only (Online):
```bash
# Install dependencies first
pip install flask flask-cors

# Start server
python run_flask.py  # or python3 run_flask.py

# Open web/index.html in browser
```

### Both Modes:
```bash
# Terminal 1 - Desktop
python app.py

# Terminal 2 - Web API
python run_flask.py
```

---

## 🔍 Verification

### Desktop Mode Verification:
✅ Login window appears  
✅ Can login with `admin` / `admin`  
✅ Main dashboard shows up  
✅ Database file created at `backend/hospital.db`

### Web Mode Verification:
✅ Flask server starts without errors  
✅ Visit `http://127.0.0.1:5000/api/health`  
✅ Should return: `{"status": "healthy", ...}`  
✅ `web/index.html` loads and connects

---

## ⚠️ Troubleshooting

### Desktop Mode Issues:

**Problem: "No module named 'tkinter'"**
- **Solution:** Install tkinter:
  - Ubuntu/Debian: `sudo apt-get install python3-tk`
  - Windows/Mac: Usually included with Python

**Problem: Database errors**
- **Solution:** Check write permissions in `backend/` folder

### Web Mode Issues:

**Problem: "Port 5000 already in use"**
- **Solution:** Change port in `run_flask.py`:
  ```python
  app.run(host='127.0.0.1', port=5001)  # Use different port
  ```

**Problem: "Module not found: flask"**
- **Solution:** Install Flask:
  ```bash
  pip install flask flask-cors
  ```

**Problem: CORS errors in browser**
- **Solution:** Flask-CORS should handle this, make sure it's installed:
  ```bash
  pip install flask-cors
  ```

**Problem: Web page can't connect to API**
- **Solution:** 
  1. Make sure Flask server is running
  2. Check API URL in `web/js/api.js` (should be `http://127.0.0.1:5000/api`)
  3. Try accessing API directly: `http://127.0.0.1:5000/api/health`

---

## 📝 Default Credentials

**Desktop Login:**
- Username: `admin`
- Password: `admin`

**Web API:**
- No authentication required (for now)
- Can add authentication later if needed

---

## 🎯 Next Steps

1. **Desktop Mode:** Start managing patients, doctors, appointments, etc.
2. **Web Mode:** 
   - Explore the web interface
   - Or use the API with tools like Postman/curl
   - See `docs/FLASK_API_README.md` for API documentation

---

## 📚 More Information

- **Architecture:** See `docs/ARCHITECTURE_EXPLANATION.md`
- **API Documentation:** See `docs/FLASK_API_README.md`
- **Code Structure:** See `docs/STRUCTURE.md`

---

## 💡 Tips

1. **Development:** Use both modes together to test features
2. **Production Desktop:** Build executable using `build_exe.bat`
3. **Production Web:** Run Flask with `debug=False` in `run_flask.py`
4. **Data Backup:** Backup `backend/hospital.db` regularly

Happy coding! 🎉




