# Flask API Documentation

## Overview

The Flask API provides a RESTful web interface to the Hospital Management System. It uses the same `Database` class as the desktop application, so both modes share the same data.

## Quick Start

### 1. Install Dependencies

```bash
pip install flask flask-cors
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Start the Flask Server

**Windows:**
```bash
run_flask.bat
```

**Linux/Mac:**
```bash
chmod +x run_flask.sh
./run_flask.sh
```

**Or directly:**
```bash
python run_flask.py
```

### 3. Access the API

The API will be available at: `http://127.0.0.1:5000`

## API Endpoints

### Health Check
- **GET** `/api/health` - Check API status

### Authentication
- **POST** `/api/auth/login` - User login
  ```json
  {
    "username": "admin",
    "password": "admin"
  }
  ```

### Patients
- **GET** `/api/patients` - Get all patients (optional: `?search=query`)
- **GET** `/api/patients/<patient_id>` - Get patient by ID
- **POST** `/api/patients` - Add new patient
- **PUT** `/api/patients/<patient_id>` - Update patient

### Doctors
- **GET** `/api/doctors` - Get all doctors
- **GET** `/api/doctors/<doctor_id>` - Get doctor by ID
- **POST** `/api/doctors` - Add new doctor
- **PUT** `/api/doctors/<doctor_id>` - Update doctor
- **DELETE** `/api/doctors/<doctor_id>` - Delete doctor

### Appointments
- **GET** `/api/appointments` - Get all appointments
  - Filters: `?date=YYYY-MM-DD`, `?status=Scheduled`, `?patient_name=John`
- **GET** `/api/appointments/<appointment_id>` - Get appointment by ID
- **POST** `/api/appointments` - Add new appointment
- **PUT** `/api/appointments/<appointment_id>` - Update appointment

### Prescriptions
- **GET** `/api/prescriptions` - Get all prescriptions
  - Filters: `?date=YYYY-MM-DD`, `?patient_id=xxx`, `?patient_name=John`
- **GET** `/api/prescriptions/<prescription_id>` - Get prescription by ID
- **POST** `/api/prescriptions` - Add new prescription (with items)
  ```json
  {
    "prescription": { ... },
    "items": [ ... ]
  }
  ```
- **PUT** `/api/prescriptions/<prescription_id>` - Update prescription

### Billing
- **GET** `/api/bills` - Get all bills
  - Filters: `?date=YYYY-MM-DD`, `?status=Paid`, `?patient_name=John`
- **GET** `/api/bills/<bill_id>` - Get bill by ID
- **POST** `/api/bills` - Add new bill
- **PUT** `/api/bills/<bill_id>` - Update bill
- **DELETE** `/api/bills/<bill_id>` - Delete bill

### Medicines
- **GET** `/api/medicines` - Get all medicines (paginated)
  - Query params: `?search=query`, `?page=1`, `?limit=50`
- **GET** `/api/medicines/autocomplete` - Get medicine names for autocomplete
- **GET** `/api/medicines/<medicine_name>/dosages` - Get dosages for medicine

### Statistics
- **GET** `/api/statistics` - Get system statistics
  - Query params: `?filter_type=all|daily|monthly|yearly`, `?filter_date=YYYY-MM-DD`
  - Or: `?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD`
- **GET** `/api/appointments/today` - Get today's appointments
- **GET** `/api/activities/recent` - Get recent activities (`?limit=10`)

## Example Usage

### Using curl

```bash
# Health check
curl http://127.0.0.1:5000/api/health

# Get all patients
curl http://127.0.0.1:5000/api/patients

# Search patients
curl http://127.0.0.1:5000/api/patients?search=John

# Add a patient
curl -X POST http://127.0.0.1:5000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "gender": "Male",
    "phone": "1234567890"
  }'

# Login
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }'
```

### Using Python

```python
import requests

base_url = "http://127.0.0.1:5000/api"

# Get all patients
response = requests.get(f"{base_url}/patients")
patients = response.json()

# Add a patient
patient_data = {
    "patient_id": "P001",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "gender": "Male"
}
response = requests.post(f"{base_url}/patients", json=patient_data)
result = response.json()
```

### Using JavaScript (Fetch API)

```javascript
// Get all patients
fetch('http://127.0.0.1:5000/api/patients')
  .then(response => response.json())
  .then(data => console.log(data));

// Add a patient
fetch('http://127.0.0.1:5000/api/patients', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    patient_id: 'P001',
    first_name: 'John',
    last_name: 'Doe',
    date_of_birth: '1990-01-01',
    gender: 'Male'
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## Response Format

All API responses follow this format:

**Success:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error:**
```json
{
  "error": "Error message",
  "success": false
}
```

## Notes

1. **Same Database**: The Flask API uses the same SQLite database file as the desktop application. Both modes share the same data.

2. **CORS Enabled**: CORS is enabled for cross-origin requests, so you can use this API from web browsers.

3. **Development Mode**: The Flask server runs in debug mode by default. Change `debug=True` to `debug=False` in `run_flask.py` for production.

4. **Authentication**: Basic authentication is implemented. You can enhance it with JWT tokens or sessions for production use.

5. **Port**: Default port is 5000. Change it in `run_flask.py` if needed.

## Running Both Modes

You can run both the desktop application and Flask API simultaneously:
- They both use the same database file
- SQLite handles concurrent access (readers ok, one writer at a time)
- Perfect for gradual migration or hybrid setups

## Troubleshooting

1. **Port Already in Use**: Change the port in `run_flask.py` from 5000 to another port (e.g., 5001)

2. **Module Not Found**: Make sure you're running from the project root directory

3. **Database Locked**: If you get database locking errors, make sure only one process is writing at a time (multiple readers are fine)

