"""
Database module for Hospital Management System
Handles all database operations using SQLite
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from logger import log_info, log_error, log_debug, log_database_operation
from logger import log_database_operation, log_info, log_error, log_debug


class Database:
    """Database manager for hospital management system"""
    
    def __init__(self, db_name: str = "hospital.db"):
        """Initialize database connection"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.init_database()
    
    def connect(self):
        """Establish database connection"""
        log_info(f"Connecting to database: {self.db_name}")
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        log_info("Database connection established")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def init_database(self):
        """Initialize database with all required tables"""
        self.connect()
        
        # Patients table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                emergency_contact TEXT,
                emergency_phone TEXT,
                blood_group TEXT,
                allergies TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Doctors table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                qualification TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                consultation_fee REAL DEFAULT 0,
                available_days TEXT,
                available_time TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Appointments table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id TEXT UNIQUE NOT NULL,
                patient_id TEXT NOT NULL,
                doctor_id TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                status TEXT DEFAULT 'Scheduled',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
            )
        """)
        
        # Prescriptions table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id TEXT UNIQUE NOT NULL,
                patient_id TEXT NOT NULL,
                doctor_id TEXT NOT NULL,
                appointment_id TEXT,
                prescription_date TEXT NOT NULL,
                diagnosis TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
                FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
            )
        """)
        
        # Prescription items (medicines)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescription_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id TEXT NOT NULL,
                medicine_name TEXT NOT NULL,
                dosage TEXT NOT NULL,
                frequency TEXT NOT NULL,
                duration TEXT NOT NULL,
                instructions TEXT,
                FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id)
            )
        """)
        
        # Billing table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id TEXT UNIQUE NOT NULL,
                patient_id TEXT NOT NULL,
                appointment_id TEXT,
                bill_date TEXT NOT NULL,
                consultation_fee REAL DEFAULT 0,
                medicine_cost REAL DEFAULT 0,
                other_charges REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                payment_status TEXT DEFAULT 'Pending',
                payment_method TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
            )
        """)
        
        # Staff table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                role TEXT NOT NULL,
                department TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                salary REAL,
                hire_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        log_info("Database initialized successfully")
    
    # Patient operations
    def add_patient(self, patient_data: Dict) -> bool:
        """Add a new patient"""
        log_debug(f"Adding patient: {patient_data.get('patient_id')}")
        try:
            self.cursor.execute("""
                INSERT INTO patients (patient_id, first_name, last_name, date_of_birth,
                gender, phone, email, address, emergency_contact, emergency_phone,
                blood_group, allergies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_data['patient_id'],
                patient_data['first_name'],
                patient_data['last_name'],
                patient_data['date_of_birth'],
                patient_data['gender'],
                patient_data.get('phone', ''),
                patient_data.get('email', ''),
                patient_data.get('address', ''),
                patient_data.get('emergency_contact', ''),
                patient_data.get('emergency_phone', ''),
                patient_data.get('blood_group', ''),
                patient_data.get('allergies', '')
            ))
            self.conn.commit()
            log_info(f"Patient added successfully: {patient_data['patient_id']}")
            return True
        except sqlite3.IntegrityError as e:
            log_error(f"Failed to add patient (integrity error): {patient_data.get('patient_id')}", e)
            return False
        except Exception as e:
            log_error(f"Failed to add patient: {patient_data.get('patient_id')}", e)
            return False
    
    def get_all_patients(self) -> List[Dict]:
        """Get all patients"""
        log_debug("Fetching all patients from database")
        self.cursor.execute("SELECT * FROM patients ORDER BY created_at DESC")
        patients = [dict(row) for row in self.cursor.fetchall()]
        log_info(f"Retrieved {len(patients)} patients from database")
        return patients
    
    def search_patients(self, query: str) -> List[Dict]:
        """Search patients by name, ID, or phone"""
        self.cursor.execute("""
            SELECT * FROM patients 
            WHERE patient_id LIKE ? OR first_name LIKE ? OR last_name LIKE ? 
            OR phone LIKE ? OR email LIKE ?
            ORDER BY created_at DESC
        """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """Get patient by ID"""
        self.cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_patient(self, patient_id: str, patient_data: Dict) -> bool:
        """Update patient information"""
        try:
            log_debug(f"Updating patient: {patient_id}")
            self.cursor.execute("""
                UPDATE patients SET
                first_name = ?, last_name = ?, date_of_birth = ?,
                gender = ?, phone = ?, email = ?, address = ?,
                emergency_contact = ?, emergency_phone = ?,
                blood_group = ?, allergies = ?, updated_at = ?
                WHERE patient_id = ?
            """, (
                patient_data['first_name'],
                patient_data['last_name'],
                patient_data['date_of_birth'],
                patient_data['gender'],
                patient_data.get('phone', ''),
                patient_data.get('email', ''),
                patient_data.get('address', ''),
                patient_data.get('emergency_contact', ''),
                patient_data.get('emergency_phone', ''),
                patient_data.get('blood_group', ''),
                patient_data.get('allergies', ''),
                datetime.now().isoformat(),
                patient_id
            ))
            self.conn.commit()
            log_database_operation("UPDATE", "patients", True, f"Patient ID: {patient_id}")
            return True
        except Exception as e:
            log_database_operation("UPDATE", "patients", False, f"Patient ID: {patient_id} - Error: {str(e)}")
            log_error(f"Error updating patient: {patient_id}", e)
            return False
    
    # Doctor operations
    def add_doctor(self, doctor_data: Dict) -> bool:
        """Add a new doctor"""
        try:
            self.cursor.execute("""
                INSERT INTO doctors (doctor_id, first_name, last_name, specialization,
                qualification, phone, email, address, consultation_fee, available_days,
                available_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doctor_data['doctor_id'],
                doctor_data['first_name'],
                doctor_data['last_name'],
                doctor_data['specialization'],
                doctor_data.get('qualification', ''),
                doctor_data.get('phone', ''),
                doctor_data.get('email', ''),
                doctor_data.get('address', ''),
                doctor_data.get('consultation_fee', 0),
                doctor_data.get('available_days', ''),
                doctor_data.get('available_time', '')
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_doctors(self) -> List[Dict]:
        """Get all doctors"""
        self.cursor.execute("SELECT * FROM doctors ORDER BY specialization, last_name")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_doctor_by_id(self, doctor_id: str) -> Optional[Dict]:
        """Get doctor by ID"""
        self.cursor.execute("SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    # Appointment operations
    def add_appointment(self, appointment_data: Dict) -> bool:
        """Add a new appointment"""
        try:
            self.cursor.execute("""
                INSERT INTO appointments (appointment_id, patient_id, doctor_id,
                appointment_date, appointment_time, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                appointment_data['appointment_id'],
                appointment_data['patient_id'],
                appointment_data['doctor_id'],
                appointment_data['appointment_date'],
                appointment_data['appointment_time'],
                appointment_data.get('status', 'Scheduled'),
                appointment_data.get('notes', '')
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_appointments(self) -> List[Dict]:
        """Get all appointments"""
        self.cursor.execute("""
            SELECT a.*, p.first_name || ' ' || p.last_name as patient_name,
            d.first_name || ' ' || d.last_name as doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_appointments_by_date(self, date: str) -> List[Dict]:
        """Get appointments for a specific date"""
        self.cursor.execute("""
            SELECT a.*, p.first_name || ' ' || p.last_name as patient_name,
            d.first_name || ' ' || d.last_name as doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_date = ?
            ORDER BY a.appointment_time
        """, (date,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    # Prescription operations
    def add_prescription(self, prescription_data: Dict, items: List[Dict]) -> bool:
        """Add a new prescription with items"""
        try:
            self.cursor.execute("""
                INSERT INTO prescriptions (prescription_id, patient_id, doctor_id,
                appointment_id, prescription_date, diagnosis, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                prescription_data['prescription_id'],
                prescription_data['patient_id'],
                prescription_data['doctor_id'],
                prescription_data.get('appointment_id'),
                prescription_data['prescription_date'],
                prescription_data.get('diagnosis', ''),
                prescription_data.get('notes', '')
            ))
            
            for item in items:
                self.cursor.execute("""
                    INSERT INTO prescription_items (prescription_id, medicine_name,
                    dosage, frequency, duration, instructions)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    prescription_data['prescription_id'],
                    item['medicine_name'],
                    item['dosage'],
                    item['frequency'],
                    item['duration'],
                    item.get('instructions', '')
                ))
            
            self.conn.commit()
            return True
        except Exception:
            return False
    
    def get_all_prescriptions(self) -> List[Dict]:
        """Get all prescriptions"""
        self.cursor.execute("""
            SELECT p.*, d.first_name || ' ' || d.last_name as doctor_name
            FROM prescriptions p
            LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
            ORDER BY p.prescription_date DESC
        """)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_prescriptions_by_patient(self, patient_id: str) -> List[Dict]:
        """Get all prescriptions for a patient"""
        self.cursor.execute("""
            SELECT p.*, d.first_name || ' ' || d.last_name as doctor_name
            FROM prescriptions p
            LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
            WHERE p.patient_id = ?
            ORDER BY p.prescription_date DESC
        """, (patient_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_prescription_items(self, prescription_id: str) -> List[Dict]:
        """Get items for a prescription"""
        self.cursor.execute("""
            SELECT * FROM prescription_items WHERE prescription_id = ?
        """, (prescription_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    # Billing operations
    def add_bill(self, bill_data: Dict) -> bool:
        """Add a new bill"""
        try:
            self.cursor.execute("""
                INSERT INTO billing (bill_id, patient_id, appointment_id, bill_date,
                consultation_fee, medicine_cost, other_charges, total_amount,
                payment_status, payment_method, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bill_data['bill_id'],
                bill_data['patient_id'],
                bill_data.get('appointment_id'),
                bill_data['bill_date'],
                bill_data.get('consultation_fee', 0),
                bill_data.get('medicine_cost', 0),
                bill_data.get('other_charges', 0),
                bill_data['total_amount'],
                bill_data.get('payment_status', 'Pending'),
                bill_data.get('payment_method', ''),
                bill_data.get('notes', '')
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_bills(self) -> List[Dict]:
        """Get all bills"""
        self.cursor.execute("""
            SELECT b.*, p.first_name || ' ' || p.last_name as patient_name
            FROM billing b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            ORDER BY b.bill_date DESC
        """)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """Get system statistics"""
        stats = {}
        
        self.cursor.execute("SELECT COUNT(*) FROM patients")
        stats['total_patients'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM doctors")
        stats['total_doctors'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'Scheduled'")
        stats['scheduled_appointments'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'Completed'")
        stats['completed_appointments'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT SUM(total_amount) FROM billing WHERE payment_status = 'Paid'")
        result = self.cursor.fetchone()[0]
        stats['total_revenue'] = result if result else 0
        
        return stats

