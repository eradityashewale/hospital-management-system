"""
Flask API for Hospital Management System
REST API wrapper around the Database class
"""
from flask import Flask, jsonify, request, send_from_directory, send_file

# Try to import CORS, but make it optional
try:
    from flask_cors import CORS
    cors_available = True
except ImportError:
    cors_available = False
    print("Warning: flask-cors not installed. CORS support disabled.")
from functools import wraps
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.database import Database
from utils.logger import log_info, log_error

# Initialize Flask app
# Set static folder to serve web frontend
app = Flask(__name__, 
            static_folder=os.path.join(project_root, 'web'),
            static_url_path='/web')

# Enable CORS if available
if cors_available:
    CORS(app)  # Enable CORS for cross-origin requests

# Initialize database instance
db = Database()

# ============================================================================
# Authentication Middleware (Optional - can be enhanced with JWT)
# ============================================================================

def require_auth(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, we'll skip auth check - can be added later
        # You can check session, JWT token, etc.
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

# ============================================================================
# Web Frontend Routes - Serve HTML pages
# ============================================================================

@app.route('/')
def index():
    """Serve the main web frontend page"""
    web_dir = os.path.join(project_root, 'web')
    return send_file(os.path.join(web_dir, 'index.html'))

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files"""
    return send_from_directory(os.path.join(project_root, 'web', 'js'), filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files (so web UI has styles when deployed e.g. Render)"""
    return send_from_directory(os.path.join(project_root, 'web', 'css'), filename)

# ============================================================================
# Health Check
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Hospital Management System API',
        'database': 'connected'
    })

# ============================================================================
# Authentication Routes
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        user = db.authenticate_user(username, password)
        if user:
            # Remove password hash from response
            user_dict = dict(user)
            user_dict.pop('password', None)
            return jsonify({'success': True, 'user': user_dict}), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        log_error("Login error", e)
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Patient Routes
# ============================================================================

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Get all patients"""
    try:
        search_query = request.args.get('search', '')
        if search_query:
            patients = db.search_patients(search_query)
        else:
            patients = db.get_all_patients()
        return jsonify({'success': True, 'patients': patients}), 200
    except Exception as e:
        log_error("Get patients error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get patient by ID"""
    try:
        patient = db.get_patient_by_id(patient_id)
        if patient:
            return jsonify({'success': True, 'patient': patient}), 200
        else:
            return jsonify({'error': 'Patient not found'}), 404
    except Exception as e:
        log_error(f"Get patient error: {patient_id}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients', methods=['POST'])
def add_patient():
    """Add a new patient"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        success = db.add_patient(data)
        if success:
            return jsonify({'success': True, 'message': 'Patient added successfully'}), 201
        else:
            return jsonify({'error': 'Failed to add patient'}), 400
    except Exception as e:
        log_error("Add patient error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update patient information"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        success = db.update_patient(patient_id, data)
        if success:
            return jsonify({'success': True, 'message': 'Patient updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update patient'}), 400
    except Exception as e:
        log_error(f"Update patient error: {patient_id}", e)
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Admission (IPD) Routes - Admissions + Day-wise Notes
# ============================================================================

@app.route('/api/patients/<patient_id>/admissions', methods=['GET'])
def get_patient_admissions(patient_id):
    """Get all admissions for a patient"""
    try:
        admissions = db.get_admissions_by_patient(patient_id)
        return jsonify({'success': True, 'admissions': admissions}), 200
    except Exception as e:
        log_error(f"Get patient admissions error: {patient_id}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<patient_id>/admissions/active', methods=['GET'])
def get_patient_active_admission(patient_id):
    """Get active admission for a patient (if any)"""
    try:
        admission = db.get_active_admission_by_patient(patient_id)
        return jsonify({'success': True, 'admission': admission}), 200
    except Exception as e:
        log_error(f"Get active admission error: {patient_id}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/admissions', methods=['GET'])
def get_all_admissions():
    """Get all admissions with optional status filter"""
    try:
        status = request.args.get('status')  # Optional: 'Admitted', 'Discharged', or None for all
        
        # Get all patients and their admissions
        all_patients = db.get_all_patients()
        all_admissions = []
        
        for patient in all_patients:
            patient_admissions = db.get_admissions_by_patient(patient['patient_id'])
            for admission in patient_admissions:
                # Apply status filter if provided
                if status and admission.get('status') != status:
                    continue
                
                admission['patient_name'] = f"{patient['first_name']} {patient['last_name']}"
                admission['patient_id'] = patient['patient_id']
                all_admissions.append(admission)
        
        # Sort by admission date (newest first)
        all_admissions.sort(key=lambda x: x.get('admission_date', ''), reverse=True)
        
        return jsonify({'success': True, 'admissions': all_admissions}), 200
    except Exception as e:
        log_error("Get all admissions error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/admissions/active', methods=['GET'])
def get_active_admissions():
    """Get all currently active admissions"""
    try:
        active_admissions = db.get_all_active_admissions()
        return jsonify({'success': True, 'admissions': active_admissions}), 200
    except Exception as e:
        log_error("Get active admissions error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/admissions', methods=['POST'])
def create_admission():
    """Create a new admission"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required = ['admission_id', 'patient_id', 'admission_date']
        for r in required:
            if not data.get(r):
                return jsonify({'error': f'{r} is required'}), 400

        success = db.add_admission(data)
        if success:
            return jsonify({'success': True, 'message': 'Admission created successfully'}), 201
        return jsonify({'error': 'Failed to create admission'}), 400
    except Exception as e:
        log_error("Create admission error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/admissions/<admission_id>/discharge', methods=['PUT'])
def discharge_admission(admission_id):
    """Discharge an admission"""
    try:
        data = request.get_json() or {}
        discharge_date = data.get('discharge_date')
        discharge_summary = data.get('discharge_summary', '')

        success = db.discharge_admission(admission_id, discharge_date=discharge_date, discharge_summary=discharge_summary)
        if success:
            return jsonify({'success': True, 'message': 'Admission discharged successfully'}), 200
        return jsonify({'error': 'Failed to discharge admission'}), 400
    except Exception as e:
        log_error(f"Discharge admission error: {admission_id}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/admissions/<admission_id>/notes', methods=['GET'])
def get_admission_notes(admission_id):
    """Get day-wise notes for an admission"""
    try:
        notes = db.get_admission_notes(admission_id)
        return jsonify({'success': True, 'notes': notes}), 200
    except Exception as e:
        log_error(f"Get admission notes error: {admission_id}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/admissions/<admission_id>/notes', methods=['POST'])
def add_admission_note(admission_id):
    """Add a day-wise note for an admission"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required = ['note_id', 'note_date', 'note_text']
        for r in required:
            if not data.get(r):
                return jsonify({'error': f'{r} is required'}), 400

        payload = dict(data)
        payload['admission_id'] = admission_id

        success = db.add_admission_note(payload)
        if success:
            return jsonify({'success': True, 'message': 'Admission note added successfully'}), 201
        return jsonify({'error': 'Failed to add admission note'}), 400
    except Exception as e:
        log_error(f"Add admission note error: {admission_id}", e)
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Doctor Routes
# ============================================================================

@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    """Get all doctors"""
    try:
        doctors = db.get_all_doctors()
        return jsonify({'success': True, 'doctors': doctors}), 200
    except Exception as e:
        log_error("Get doctors error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/doctors/<doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    """Get doctor by ID"""
    try:
        doctor = db.get_doctor_by_id(doctor_id)
        if doctor:
            return jsonify({'success': True, 'doctor': doctor}), 200
        else:
            return jsonify({'error': 'Doctor not found'}), 404
    except Exception as e:
        log_error(f"Get doctor error: {doctor_id}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/doctors', methods=['POST'])
def add_doctor():
    """Add a new doctor"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        success = db.add_doctor(data)
        if success:
            return jsonify({'success': True, 'message': 'Doctor added successfully'}), 201
        else:
            return jsonify({'error': 'Failed to add doctor'}), 400
    except Exception as e:
        log_error("Add doctor error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/doctors/<doctor_id>', methods=['PUT'])
def update_doctor(doctor_id):
    """Update doctor information"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        success = db.update_doctor(doctor_id, data)
        if success:
            return jsonify({'success': True, 'message': 'Doctor updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update doctor'}), 400
    except Exception as e:
        log_error(f"Update doctor error: {doctor_id}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/doctors/<doctor_id>', methods=['DELETE'])
def delete_doctor(doctor_id):
    """Delete a doctor"""
    try:
        success = db.delete_doctor(doctor_id)
        if success:
            return jsonify({'success': True, 'message': 'Doctor deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete doctor'}), 400
    except Exception as e:
        log_error(f"Delete doctor error: {doctor_id}", e)
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Appointment Routes
# ============================================================================

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    """Get all appointments with optional filters"""
    try:
        date = request.args.get('date')
        status = request.args.get('status')
        patient_name = request.args.get('patient_name')
        
        if patient_name and date and status:
            appointments = db.get_appointments_by_patient_name_date_and_status(patient_name, date, status)
        elif patient_name and date:
            appointments = db.get_appointments_by_patient_name_and_date(patient_name, date)
        elif patient_name and status:
            appointments = db.get_appointments_by_patient_name_and_status(patient_name, status)
        elif patient_name:
            appointments = db.get_appointments_by_patient_name(patient_name)
        elif date and status:
            appointments = db.get_appointments_by_date_and_status(date, status)
        elif date:
            appointments = db.get_appointments_by_date(date)
        elif status:
            appointments = db.get_appointments_by_status(status)
        else:
            appointments = db.get_all_appointments()
        
        return jsonify({'success': True, 'appointments': appointments}), 200
    except Exception as e:
        log_error("Get appointments error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointments/<appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    """Get appointment by ID"""
    try:
        appointment = db.get_appointment_by_id(appointment_id)
        if appointment:
            return jsonify({'success': True, 'appointment': appointment}), 200
        else:
            return jsonify({'error': 'Appointment not found'}), 404
    except Exception as e:
        log_error(f"Get appointment error: {appointment_id}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointments', methods=['POST'])
def add_appointment():
    """Add a new appointment"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        success = db.add_appointment(data)
        if success:
            return jsonify({'success': True, 'message': 'Appointment added successfully'}), 201
        else:
            return jsonify({'error': 'Failed to add appointment'}), 400
    except Exception as e:
        log_error("Add appointment error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointments/<appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    """Update an appointment"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        success = db.update_appointment(appointment_id, data)
        if success:
            return jsonify({'success': True, 'message': 'Appointment updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update appointment'}), 400
    except Exception as e:
        log_error(f"Update appointment error: {appointment_id}", e)
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Prescription Routes
# ============================================================================

@app.route('/api/prescriptions', methods=['GET'])
def get_prescriptions():
    """Get all prescriptions with optional filters"""
    try:
        date = request.args.get('date')
        patient_id = request.args.get('patient_id')
        patient_name = request.args.get('patient_name')
        
        if patient_id:
            prescriptions = db.get_prescriptions_by_patient(patient_id)
        elif patient_name:
            prescriptions = db.get_prescriptions_by_patient_name(patient_name)
        elif date:
            prescriptions = db.get_prescriptions_by_date(date)
        else:
            prescriptions = db.get_all_prescriptions()
        
        # Add prescription items to each prescription
        for prescription in prescriptions:
            prescription_id = prescription.get('prescription_id')
            if prescription_id:
                prescription['items'] = db.get_prescription_items(prescription_id)
        
        return jsonify({'success': True, 'prescriptions': prescriptions}), 200
    except Exception as e:
        log_error("Get prescriptions error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/prescriptions/<prescription_id>', methods=['GET'])
def get_prescription(prescription_id):
    """Get prescription by ID"""
    try:
        prescription = db.get_prescription_by_id(prescription_id)
        if prescription:
            prescription['items'] = db.get_prescription_items(prescription_id)
            return jsonify({'success': True, 'prescription': prescription}), 200
        else:
            return jsonify({'error': 'Prescription not found'}), 404
    except Exception as e:
        log_error(f"Get prescription error: {prescription_id}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/prescriptions', methods=['POST'])
def add_prescription():
    """Add a new prescription with items"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        prescription_data = data.get('prescription', {})
        items = data.get('items', [])
        
        success = db.add_prescription(prescription_data, items)
        if success:
            return jsonify({'success': True, 'message': 'Prescription added successfully'}), 201
        else:
            return jsonify({'error': 'Failed to add prescription'}), 400
    except Exception as e:
        log_error("Add prescription error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/prescriptions/<prescription_id>', methods=['PUT'])
def update_prescription(prescription_id):
    """Update a prescription with items"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        prescription_data = data.get('prescription', {})
        items = data.get('items', [])
        
        success = db.update_prescription(prescription_id, prescription_data, items)
        if success:
            return jsonify({'success': True, 'message': 'Prescription updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update prescription'}), 400
    except Exception as e:
        log_error(f"Update prescription error: {prescription_id}", e)
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Billing Routes
# ============================================================================

@app.route('/api/bills', methods=['GET'])
def get_bills():
    """Get all bills with optional filters"""
    try:
        date = request.args.get('date')
        status = request.args.get('status')
        patient_name = request.args.get('patient_name')
        
        if patient_name and date and status:
            bills = db.get_bills_by_patient_name_date_and_status(patient_name, date, status)
        elif patient_name and date:
            bills = db.get_bills_by_patient_name_and_date(patient_name, date)
        elif patient_name and status:
            bills = db.get_bills_by_patient_name_and_status(patient_name, status)
        elif patient_name:
            bills = db.get_bills_by_patient_name(patient_name)
        elif date and status:
            bills = db.get_bills_by_date_and_status(date, status)
        elif date:
            bills = db.get_bills_by_date(date)
        elif status:
            bills = db.get_bills_by_status(status)
        else:
            bills = db.get_all_bills()
        
        return jsonify({'success': True, 'bills': bills}), 200
    except Exception as e:
        log_error("Get bills error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/bills/<bill_id>', methods=['GET'])
def get_bill(bill_id):
    """Get bill by ID"""
    try:
        bill = db.get_bill_by_id(bill_id)
        if bill:
            return jsonify({'success': True, 'bill': bill}), 200
        else:
            return jsonify({'error': 'Bill not found'}), 404
    except Exception as e:
        log_error(f"Get bill error: {bill_id}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/bills', methods=['POST'])
def add_bill():
    """Add a new bill"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        success = db.add_bill(data)
        if success:
            return jsonify({'success': True, 'message': 'Bill added successfully'}), 201
        else:
            return jsonify({'error': 'Failed to add bill'}), 400
    except Exception as e:
        log_error("Add bill error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/bills/<bill_id>', methods=['PUT'])
def update_bill(bill_id):
    """Update a bill"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        success = db.update_bill(bill_id, data)
        if success:
            return jsonify({'success': True, 'message': 'Bill updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update bill'}), 400
    except Exception as e:
        log_error(f"Update bill error: {bill_id}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/bills/<bill_id>', methods=['DELETE'])
def delete_bill(bill_id):
    """Delete a bill"""
    try:
        success = db.delete_bill(bill_id)
        if success:
            return jsonify({'success': True, 'message': 'Bill deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete bill'}), 400
    except Exception as e:
        log_error(f"Delete bill error: {bill_id}", e)
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Medicine Routes
# ============================================================================

@app.route('/api/medicines', methods=['GET'])
def get_medicines():
    """Get all medicines with optional search and pagination"""
    try:
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit
        
        if search:
            medicines = db.search_medicines_master_paginated(search, limit, offset)
            total_count = db.get_search_medicines_count(search)
        else:
            medicines = db.get_all_medicines_master_paginated(limit, offset)
            total_count = db.get_total_medicines_count()
        
        return jsonify({
            'success': True,
            'medicines': medicines,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            }
        }), 200
    except Exception as e:
        log_error("Get medicines error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/medicines/autocomplete', methods=['GET'])
def get_medicine_autocomplete():
    """Get medicine names for autocomplete"""
    try:
        medicines = db.get_all_medicines()
        return jsonify({'success': True, 'medicines': medicines}), 200
    except Exception as e:
        log_error("Get medicine autocomplete error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/medicines/<medicine_name>/dosages', methods=['GET'])
def get_medicine_dosages(medicine_name):
    """Get available dosages for a medicine"""
    try:
        dosages = db.get_medicine_dosages(medicine_name)
        return jsonify({'success': True, 'dosages': dosages}), 200
    except Exception as e:
        log_error(f"Get medicine dosages error: {medicine_name}", e)
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Statistics Routes
# ============================================================================

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    try:
        filter_type = request.args.get('filter_type', 'all')
        filter_date = request.args.get('filter_date')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        if from_date and to_date:
            stats = db.get_date_range_statistics(from_date, to_date)
        elif filter_type != 'all' and filter_date:
            stats = db.get_statistics(filter_type, filter_date)
        else:
            stats = db.get_statistics()
        
        return jsonify({'success': True, 'statistics': stats}), 200
    except Exception as e:
        log_error("Get statistics error", e)
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Reports Routes
# ============================================================================

@app.route('/api/reports/financial', methods=['GET'])
def get_financial_report():
    """Get financial report data"""
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        bills = db.get_all_bills()
        
        # Filter by date if provided
        if from_date and to_date:
            bills = [b for b in bills 
                    if from_date <= b.get('bill_date', '') <= to_date]
        
        paid_bills = [b for b in bills if b.get('payment_status') == 'Paid']
        pending_bills = [b for b in bills if b.get('payment_status') == 'Pending']
        
        total_revenue = sum(float(b.get('total_amount', 0)) for b in paid_bills)
        total_pending = sum(float(b.get('total_amount', 0)) for b in pending_bills)
        total_amount = sum(float(b.get('total_amount', 0)) for b in bills)
        
        # Daily revenue breakdown
        daily_revenue = {}
        for bill in paid_bills:
            date = bill.get('bill_date', 'Unknown')
            amount = float(bill.get('total_amount', 0))
            daily_revenue[date] = daily_revenue.get(date, 0) + amount
        
        # Payment method breakdown
        payment_methods = {}
        for bill in bills:
            method = bill.get('payment_method', 'Unknown')
            payment_methods[method] = payment_methods.get(method, 0) + 1
        
        return jsonify({
            'success': True,
            'report': {
                'total_revenue': total_revenue,
                'total_pending': total_pending,
                'total_amount': total_amount,
                'total_bills': len(bills),
                'paid_bills': len(paid_bills),
                'pending_bills': len(pending_bills),
                'collection_rate': (total_revenue / max(1, total_amount) * 100),
                'average_bill': (total_amount / max(1, len(bills))),
                'daily_revenue': daily_revenue,
                'payment_methods': payment_methods,
                'pending_bills_list': pending_bills[:50]  # Limit to 50
            }
        }), 200
    except Exception as e:
        log_error("Get financial report error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/patient', methods=['GET'])
def get_patient_report():
    """Get patient statistics report"""
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        patients = db.get_all_patients()
        appointments = db.get_all_appointments()
        prescriptions = db.get_all_prescriptions()
        
        # Filter by date if provided
        if from_date and to_date:
            appointments = [a for a in appointments 
                          if from_date <= a.get('appointment_date', '') <= to_date]
            prescriptions = [p for p in prescriptions 
                           if from_date <= p.get('prescription_date', '2000-01-01') <= to_date]
        
        # Calculate demographics
        gender_dist = {}
        age_groups = {'0-18': 0, '19-35': 0, '36-50': 0, '51-65': 0, '65+': 0}
        blood_group_dist = {}
        patient_visits = {}
        
        for appointment in appointments:
            patient_id = appointment.get('patient_id')
            if patient_id:
                patient_visits[patient_id] = patient_visits.get(patient_id, 0) + 1
        
        for patient in patients:
            gender = patient.get('gender', 'Unknown')
            gender_dist[gender] = gender_dist.get(gender, 0) + 1
            
            blood_group = patient.get('blood_group', 'Unknown')
            if blood_group:
                blood_group_dist[blood_group] = blood_group_dist.get(blood_group, 0) + 1
            
            try:
                from datetime import datetime
                dob = datetime.strptime(patient.get('date_of_birth', '2000-01-01'), '%Y-%m-%d')
                age = (datetime.now() - dob).days // 365
                if age <= 18:
                    age_groups['0-18'] += 1
                elif age <= 35:
                    age_groups['19-35'] += 1
                elif age <= 50:
                    age_groups['36-50'] += 1
                elif age <= 65:
                    age_groups['51-65'] += 1
                else:
                    age_groups['65+'] += 1
            except:
                pass
        
        # Top patients
        top_patients = sorted(patient_visits.items(), key=lambda x: x[1], reverse=True)[:10]
        top_patients_list = []
        for patient_id, visits in top_patients:
            patient = next((p for p in patients if p.get('patient_id') == patient_id), None)
            top_patients_list.append({
                'patient_id': patient_id,
                'name': f"{patient.get('first_name', '')} {patient.get('last_name', '')}" if patient else patient_id,
                'visits': visits
            })
        
        return jsonify({
            'success': True,
            'report': {
                'total_patients': len(patients),
                'total_appointments': len(appointments),
                'total_prescriptions': len(prescriptions),
                'avg_appointments_per_patient': (len(appointments) / max(1, len(patients))),
                'gender_distribution': gender_dist,
                'age_groups': age_groups,
                'blood_group_distribution': blood_group_dist,
                'top_patients': top_patients_list
            }
        }), 200
    except Exception as e:
        log_error("Get patient report error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/doctor', methods=['GET'])
def get_doctor_report():
    """Get doctor performance report"""
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        doctors = db.get_all_doctors()
        appointments = db.get_all_appointments()
        
        # Filter by date if provided
        if from_date and to_date:
            appointments = [a for a in appointments 
                          if from_date <= a.get('appointment_date', '') <= to_date]
        
        # Doctor statistics
        doctor_stats = {}
        specialization_dist = {}
        
        for doctor in doctors:
            doctor_id = doctor.get('doctor_id')
            specialization = doctor.get('specialization', 'Unknown')
            specialization_dist[specialization] = specialization_dist.get(specialization, 0) + 1
            
            doctor_appointments = [a for a in appointments if a.get('doctor_id') == doctor_id]
            completed = sum(1 for a in doctor_appointments if a.get('status') == 'Completed')
            
            doctor_stats[doctor_id] = {
                'name': f"{doctor.get('first_name', '')} {doctor.get('last_name', '')}",
                'specialization': specialization,
                'total': len(doctor_appointments),
                'completed': completed,
                'scheduled': sum(1 for a in doctor_appointments if a.get('status') == 'Scheduled'),
                'cancelled': sum(1 for a in doctor_appointments if a.get('status') == 'Cancelled'),
                'completion_rate': (completed / max(1, len(doctor_appointments)) * 100)
            }
        
        return jsonify({
            'success': True,
            'report': {
                'total_doctors': len(doctors),
                'total_appointments': len(appointments),
                'avg_appointments_per_doctor': (len(appointments) / max(1, len(doctors))),
                'specialization_distribution': specialization_dist,
                'doctor_performance': list(doctor_stats.values())
            }
        }), 200
    except Exception as e:
        log_error("Get doctor report error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/appointment', methods=['GET'])
def get_appointment_report():
    """Get appointment statistics report"""
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        appointments = db.get_all_appointments()
        
        # Filter by date if provided
        if from_date and to_date:
            appointments = [a for a in appointments 
                          if from_date <= a.get('appointment_date', '') <= to_date]
        
        # Status breakdown
        status_dist = {}
        daily_appointments = {}
        
        for appointment in appointments:
            status = appointment.get('status', 'Unknown')
            status_dist[status] = status_dist.get(status, 0) + 1
            
            date = appointment.get('appointment_date', 'Unknown')
            daily_appointments[date] = daily_appointments.get(date, 0) + 1
        
        # Top busiest days
        sorted_daily = sorted(daily_appointments.items(), key=lambda x: x[1], reverse=True)[:10]
        
        unique_days = len(set(a.get('appointment_date') for a in appointments))
        
        return jsonify({
            'success': True,
            'report': {
                'total_appointments': len(appointments),
                'avg_appointments_per_day': (len(appointments) / max(1, unique_days)),
                'status_distribution': status_dist,
                'busiest_days': [{'date': date, 'count': count} for date, count in sorted_daily]
            }
        }), 200
    except Exception as e:
        log_error("Get appointment report error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/prescription', methods=['GET'])
def get_prescription_report():
    """Get prescription statistics report"""
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        prescriptions = db.get_all_prescriptions()
        
        # Filter by date if provided
        if from_date and to_date:
            prescriptions = [p for p in prescriptions 
                           if from_date <= p.get('prescription_date', '2000-01-01') <= to_date]
        
        # Medicine usage statistics
        medicine_usage = {}
        daily_prescriptions = {}
        
        for prescription in prescriptions:
            date = prescription.get('prescription_date', 'Unknown')
            daily_prescriptions[date] = daily_prescriptions.get(date, 0) + 1
            
            # Get prescription items
            prescription_id = prescription.get('prescription_id')
            if prescription_id:
                items = db.get_prescription_items(prescription_id)
                for item in items:
                    medicine = item.get('medicine_name', 'Unknown')
                    medicine_usage[medicine] = medicine_usage.get(medicine, 0) + 1
        
        # Top prescribed medicines
        sorted_medicines = sorted(medicine_usage.items(), key=lambda x: x[1], reverse=True)[:20]
        
        unique_days = len(set(p.get('prescription_date') for p in prescriptions))
        
        return jsonify({
            'success': True,
            'report': {
                'total_prescriptions': len(prescriptions),
                'unique_medicines': len(medicine_usage),
                'avg_prescriptions_per_day': (len(prescriptions) / max(1, unique_days)),
                'top_medicines': [{'medicine': med, 'count': count} for med, count in sorted_medicines]
            }
        }), 200
    except Exception as e:
        log_error("Get prescription report error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointments/today', methods=['GET'])
def get_todays_appointments():
    """Get today's appointments"""
    try:
        date = request.args.get('date')  # Optional date parameter
        appointments = db.get_todays_appointments(date)
        return jsonify({'success': True, 'appointments': appointments}), 200
    except Exception as e:
        log_error("Get today's appointments error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/activities/recent', methods=['GET'])
def get_recent_activities():
    """Get recent activities"""
    try:
        limit = int(request.args.get('limit', 10))
        activities = db.get_recent_activities(limit)
        return jsonify({'success': True, 'activities': activities}), 200
    except Exception as e:
        log_error("Get recent activities error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/permissions', methods=['GET'])
def get_user_permissions(user_id):
    """Get permissions for a user"""
    try:
        permissions = db.get_user_permissions(user_id)
        return jsonify({'success': True, 'permissions': permissions}), 200
    except Exception as e:
        log_error(f"Get user permissions error: {user_id}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/has-permission/<module_name>', methods=['GET'])
def check_user_permission(user_id, module_name):
    """Check if user has permission for a module"""
    try:
        has_permission = db.user_has_permission(user_id, module_name)
        return jsonify({'success': True, 'has_permission': has_permission}), 200
    except Exception as e:
        log_error(f"Check user permission error: user_id={user_id}, module={module_name}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/permissions', methods=['PUT'])
def set_user_permissions(user_id):
    """Set direct permissions for a user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        permissions = data.get('permissions', [])
        success = db.set_user_permissions(user_id, permissions)
        if success:
            return jsonify({'success': True, 'message': 'Permissions updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update permissions'}), 400
    except Exception as e:
        log_error(f"Set user permissions error: {user_id}", e)
        return jsonify({'error': str(e)}), 500

# ============================================================================
# User Management Routes
# ============================================================================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        users = db.get_all_users()
        # Remove password hashes from response
        for user in users:
            user.pop('password', None)
        return jsonify({'success': True, 'users': users}), 200
    except Exception as e:
        log_error("Get users error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    try:
        user = db.get_user_by_id(user_id)
        if user:
            user.pop('password', None)  # Remove password hash
            return jsonify({'success': True, 'user': user}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        log_error(f"Get user error: {user_id}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username')
        password = data.get('password')
        full_name = data.get('full_name', '')
        email = data.get('email', '')
        permissions = data.get('permissions', [])  # Direct module permissions
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user_id = db.create_user(username, password, full_name, email, permissions)
        if user_id:
            return jsonify({'success': True, 'user_id': user_id, 'message': 'User created successfully'}), 201
        else:
            return jsonify({'error': 'Failed to create user. Username may already exist.'}), 400
    except Exception as e:
        log_error("Create user error", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username')
        full_name = data.get('full_name')
        email = data.get('email')
        password = data.get('password')
        is_active = data.get('is_active')
        permissions = data.get('permissions')  # Direct module permissions
        
        success = db.update_user(user_id, username=username, full_name=full_name, 
                                email=email, password=password, is_active=is_active)
        
        # Update permissions if provided
        if success and permissions is not None:
            db.set_user_permissions(user_id, permissions)
        
        if success:
            return jsonify({'success': True, 'message': 'User updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update user'}), 400
    except Exception as e:
        log_error(f"Update user error: {user_id}", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user (soft delete)"""
    try:
        success = db.delete_user(user_id)
        if success:
            return jsonify({'success': True, 'message': 'User deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete user'}), 400
    except Exception as e:
        log_error(f"Delete user error: {user_id}", e)
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    log_info("=" * 60)
    log_info("Hospital Management System - Flask API Starting")
    log_info("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)

