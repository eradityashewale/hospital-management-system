"""
Database module for Hospital Management System
Handles all database operations using SQLite
"""
import sqlite3
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Utils imports
from utils.logger import log_info, log_error, log_debug, log_database_operation, log_warning
from utils.helpers import generate_id


def get_app_data_dir():
    """Get the application data directory for logs and database"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable (PyInstaller)
        # Check if we're in Program Files
        exe_dir = os.path.dirname(sys.executable)
        if 'Program Files' in exe_dir or 'Program Files (x86)' in exe_dir:
            # Use AppData for installed applications
            appdata = os.getenv('APPDATA', os.path.expanduser('~'))
            app_dir = os.path.join(appdata, 'Hospital Management System')
            if not os.path.exists(app_dir):
                try:
                    os.makedirs(app_dir)
                except OSError:
                    # If AppData fails, try user's home directory
                    app_dir = os.path.join(os.path.expanduser('~'), 'Hospital Management System')
                    if not os.path.exists(app_dir):
                        os.makedirs(app_dir)
            return app_dir
        else:
            # Use executable directory if not in Program Files
            return exe_dir
    else:
        # Running from source (development mode)
        return os.path.dirname(os.path.abspath(__file__))


class Database:
    """Database manager for hospital management system"""
    
    def __init__(self, db_name: str = "hospital.db"):
        """Initialize database connection"""
        # Get the appropriate directory for the database
        app_data_dir = get_app_data_dir()
        # Use full path for database file
        self.db_name = os.path.join(app_data_dir, db_name)
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        log_info(f"Database location: {self.db_name}")
        self.init_database()
    
    def connect(self) -> None:
        """Establish database connection"""
        log_info(f"Connecting to database: {self.db_name}")
        # Allow SQLite connections to be used across threads (for Flask)
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        log_info("Database connection established")
    
    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def init_database(self) -> None:
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

        # Admissions (In-Patient) table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS admissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admission_id TEXT UNIQUE NOT NULL,
                patient_id TEXT NOT NULL,
                doctor_id TEXT,
                admission_date TEXT NOT NULL,
                expected_days INTEGER DEFAULT 0,
                expected_discharge_date TEXT,
                discharge_date TEXT,
                discharge_summary TEXT,
                status TEXT DEFAULT 'Admitted',
                ward TEXT,
                bed TEXT,
                reason TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
            )
        """)

        # Daily progress notes for admissions
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS admission_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id TEXT UNIQUE NOT NULL,
                admission_id TEXT NOT NULL,
                note_date TEXT NOT NULL,
                note_time TEXT,
                note_text TEXT NOT NULL,
                created_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admission_id) REFERENCES admissions(admission_id)
            )
        """)

        # Helpful indexes
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admissions_patient_status
            ON admissions(patient_id, status)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admission_notes_admission_date
            ON admission_notes(admission_id, note_date)
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
        
        # Medicines master table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicines_master (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_name TEXT NOT NULL,
                company_name TEXT,
                dosage_mg TEXT,
                dosage_form TEXT,
                category TEXT,
                description TEXT,
                is_pediatric INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Users table for login system
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                email TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User permissions table - stores direct module access for users
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                module_name TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, module_name)
            )
        """)
        
        # X-ray reports table - patient X-ray report metadata and file path
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS xray_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT UNIQUE NOT NULL,
                patient_id TEXT NOT NULL,
                report_date TEXT NOT NULL,
                body_part TEXT,
                findings TEXT,
                file_path TEXT NOT NULL,
                file_name_original TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_xray_reports_patient_date
            ON xray_reports(patient_id, report_date)
        """)
        
        # Migration: Add is_pediatric column if it doesn't exist
        try:
            self.cursor.execute("PRAGMA table_info(medicines_master)")
            columns = [row[1] for row in self.cursor.fetchall()]
            if 'is_pediatric' not in columns:
                log_info("Adding is_pediatric column to medicines_master table")
                self.cursor.execute("""
                    ALTER TABLE medicines_master 
                    ADD COLUMN is_pediatric INTEGER DEFAULT 0
                """)
                self.conn.commit()
                log_info("Successfully added is_pediatric column")
        except Exception as e:
            log_error("Error adding is_pediatric column to medicines_master", e)
        
        # Migration: Add vital signs and follow-up date to prescriptions table
        try:
            self.cursor.execute("PRAGMA table_info(prescriptions)")
            columns = [row[1] for row in self.cursor.fetchall()]
            
            vital_fields = {
                'weight': 'TEXT',
                'spo2': 'TEXT',
                'hr': 'TEXT',
                'rr': 'TEXT',
                'bp': 'TEXT',
                'height': 'TEXT',
                'ideal_body_weight': 'TEXT',
                'follow_up_date': 'TEXT',
                'icd_codes': 'TEXT'
            }
            
            for field_name, field_type in vital_fields.items():
                if field_name not in columns:
                    log_info(f"Adding {field_name} column to prescriptions table")
                    self.cursor.execute(f"""
                        ALTER TABLE prescriptions 
                        ADD COLUMN {field_name} {field_type}
                    """)
                    self.conn.commit()
                    log_info(f"Successfully added {field_name} column")
        except Exception as e:
            log_error("Error adding vital signs columns to prescriptions", e)
        
        # Migration: Add purpose field to prescription_items table
        try:
            self.cursor.execute("PRAGMA table_info(prescription_items)")
            columns = [row[1] for row in self.cursor.fetchall()]
            if 'purpose' not in columns:
                log_info("Adding purpose column to prescription_items table")
                self.cursor.execute("""
                    ALTER TABLE prescription_items 
                    ADD COLUMN purpose TEXT
                """)
                self.conn.commit()
                log_info("Successfully added purpose column")
        except Exception as e:
            log_error("Error adding purpose column to prescription_items", e)
        
        # Migration: Add email column to users table if it doesn't exist
        try:
            self.cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in self.cursor.fetchall()]
            if 'email' not in columns:
                log_info("Adding email column to users table")
                self.cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN email TEXT
                """)
                self.conn.commit()
                log_info("Successfully added email column")
        except Exception as e:
            log_error("Error adding email column to users table", e)
        
        # Migration: Remove role_id and role columns if they exist (cleanup from old role system)
        try:
            self.cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in self.cursor.fetchall()]
            if 'role_id' in columns or 'role' in columns:
                log_info("Removing role-related columns from users table")
                # Create new table without role columns
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        full_name TEXT,
                        email TEXT,
                        is_active INTEGER DEFAULT 1,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.cursor.execute("""
                    INSERT INTO users_new (id, username, password, full_name, email, is_active, created_at)
                    SELECT id, username, password, full_name, email, is_active, created_at FROM users
                """)
                self.cursor.execute("DROP TABLE users")
                self.cursor.execute("ALTER TABLE users_new RENAME TO users")
                self.conn.commit()
                log_info("Successfully removed role columns")
        except Exception as e:
            log_error("Error removing role columns from users table", e)
        
        # Migration: Create xray_reports table if it doesn't exist (for existing deployments)
        try:
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='xray_reports'"
            )
            if self.cursor.fetchone() is None:
                log_info("Creating xray_reports table (migration)")
                self.cursor.execute("""
                    CREATE TABLE xray_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        report_id TEXT UNIQUE NOT NULL,
                        patient_id TEXT NOT NULL,
                        report_date TEXT NOT NULL,
                        body_part TEXT,
                        findings TEXT,
                        file_path TEXT NOT NULL,
                        file_name_original TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
                    )
                """)
                self.cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_xray_reports_patient_date
                    ON xray_reports(patient_id, report_date)
                """)
                self.conn.commit()
                log_info("Successfully created xray_reports table")
        except Exception as e:
            log_error("Error creating xray_reports table", e)
        
        self.conn.commit()
        log_info("Database initialized successfully")
        
        # Create default user if no users exist
        self.create_default_user()
        
        # Populate medicines if table is empty
        self.populate_medicines()
    
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
        log_debug(f"Adding doctor: {doctor_data.get('doctor_id')}")
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
            log_info(f"Doctor added successfully: {doctor_data['doctor_id']}")
            return True
        except sqlite3.IntegrityError as e:
            log_error(f"Failed to add doctor (integrity error): {doctor_data.get('doctor_id')}", e)
            return False
        except Exception as e:
            log_error(f"Failed to add doctor: {doctor_data.get('doctor_id')}", e)
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
    
    def update_doctor(self, doctor_id: str, doctor_data: Dict) -> bool:
        """Update doctor information"""
        try:
            log_debug(f"Updating doctor: {doctor_id}")
            self.cursor.execute("""
                UPDATE doctors SET
                first_name = ?, last_name = ?, specialization = ?,
                qualification = ?, phone = ?, email = ?, address = ?,
                consultation_fee = ?, available_days = ?, available_time = ?
                WHERE doctor_id = ?
            """, (
                doctor_data['first_name'],
                doctor_data['last_name'],
                doctor_data['specialization'],
                doctor_data.get('qualification', ''),
                doctor_data.get('phone', ''),
                doctor_data.get('email', ''),
                doctor_data.get('address', ''),
                doctor_data.get('consultation_fee', 0),
                doctor_data.get('available_days', ''),
                doctor_data.get('available_time', ''),
                doctor_id
            ))
            self.conn.commit()
            log_database_operation("UPDATE", "doctors", True, f"Doctor ID: {doctor_id}")
            return True
        except Exception as e:
            log_database_operation("UPDATE", "doctors", False, f"Doctor ID: {doctor_id} - Error: {str(e)}")
            log_error(f"Error updating doctor: {doctor_id}", e)
            return False
    
    def delete_doctor(self, doctor_id: str) -> bool:
        """Delete a doctor"""
        try:
            log_debug(f"Deleting doctor: {doctor_id}")
            
            # Check for related appointments
            self.cursor.execute("SELECT COUNT(*) FROM appointments WHERE doctor_id = ?", (doctor_id,))
            appointment_count = self.cursor.fetchone()[0]
            
            # Check for related prescriptions
            self.cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE doctor_id = ?", (doctor_id,))
            prescription_count = self.cursor.fetchone()[0]
            
            if appointment_count > 0 or prescription_count > 0:
                log_warning(f"Cannot delete doctor {doctor_id}: Has {appointment_count} appointments and {prescription_count} prescriptions")
                return False
            
            # Delete the doctor
            self.cursor.execute("DELETE FROM doctors WHERE doctor_id = ?", (doctor_id,))
            self.conn.commit()
            log_database_operation("DELETE", "doctors", True, f"Doctor ID: {doctor_id}")
            return True
        except Exception as e:
            log_database_operation("DELETE", "doctors", False, f"Doctor ID: {doctor_id} - Error: {str(e)}")
            log_error(f"Error deleting doctor: {doctor_id}", e)
            return False
    
    # Appointment operations
    def add_appointment(self, appointment_data: Dict) -> bool:
        """Add a new appointment"""
        log_debug(f"Adding appointment: {appointment_data.get('appointment_id')}")
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
            log_info(f"Appointment added successfully: {appointment_data['appointment_id']}")
            return True
        except sqlite3.IntegrityError as e:
            log_error(f"Failed to add appointment (integrity error): {appointment_data.get('appointment_id')}", e)
            return False
        except Exception as e:
            log_error(f"Failed to add appointment: {appointment_data.get('appointment_id')}", e)
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
    
    def get_appointments_by_status(self, status: str) -> List[Dict]:
        """Get appointments by status"""
        self.cursor.execute("""
            SELECT a.*, p.first_name || ' ' || p.last_name as patient_name,
            d.first_name || ' ' || d.last_name as doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.status = ?
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """, (status,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_appointments_by_date_and_status(self, date: str, status: str) -> List[Dict]:
        """Get appointments by date and status"""
        self.cursor.execute("""
            SELECT a.*, p.first_name || ' ' || p.last_name as patient_name,
            d.first_name || ' ' || d.last_name as doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_date = ? AND a.status = ?
            ORDER BY a.appointment_time
        """, (date, status))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_appointments_by_patient_name(self, patient_name: str) -> List[Dict]:
        """Get appointments by patient name (searches first name and last name)"""
        self.cursor.execute("""
            SELECT a.*, p.first_name || ' ' || p.last_name as patient_name,
            d.first_name || ' ' || d.last_name as doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE p.first_name LIKE ? OR p.last_name LIKE ? 
            OR (p.first_name || ' ' || p.last_name) LIKE ?
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """, (f'%{patient_name}%', f'%{patient_name}%', f'%{patient_name}%'))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_appointments_by_patient_name_and_date(self, patient_name: str, date: str) -> List[Dict]:
        """Get appointments by patient name and date"""
        self.cursor.execute("""
            SELECT a.*, p.first_name || ' ' || p.last_name as patient_name,
            d.first_name || ' ' || d.last_name as doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE (p.first_name LIKE ? OR p.last_name LIKE ? 
            OR (p.first_name || ' ' || p.last_name) LIKE ?) AND a.appointment_date = ?
            ORDER BY a.appointment_time
        """, (f'%{patient_name}%', f'%{patient_name}%', f'%{patient_name}%', date))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_appointments_by_patient_name_and_status(self, patient_name: str, status: str) -> List[Dict]:
        """Get appointments by patient name and status"""
        self.cursor.execute("""
            SELECT a.*, p.first_name || ' ' || p.last_name as patient_name,
            d.first_name || ' ' || d.last_name as doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE (p.first_name LIKE ? OR p.last_name LIKE ? 
            OR (p.first_name || ' ' || p.last_name) LIKE ?) AND a.status = ?
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """, (f'%{patient_name}%', f'%{patient_name}%', f'%{patient_name}%', status))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_appointments_by_patient_name_date_and_status(self, patient_name: str, date: str, status: str) -> List[Dict]:
        """Get appointments by patient name, date and status"""
        self.cursor.execute("""
            SELECT a.*, p.first_name || ' ' || p.last_name as patient_name,
            d.first_name || ' ' || d.last_name as doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE (p.first_name LIKE ? OR p.last_name LIKE ? 
            OR (p.first_name || ' ' || p.last_name) LIKE ?) 
            AND a.appointment_date = ? AND a.status = ?
            ORDER BY a.appointment_time
        """, (f'%{patient_name}%', f'%{patient_name}%', f'%{patient_name}%', date, status))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_appointment_by_id(self, appointment_id: str) -> Optional[Dict]:
        """Get appointment by ID"""
        self.cursor.execute("""
            SELECT a.*, p.first_name || ' ' || p.last_name as patient_name,
            d.first_name || ' ' || d.last_name as doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_id = ?
        """, (appointment_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_appointment(self, appointment_id: str, appointment_data: Dict) -> bool:
        """Update an existing appointment"""
        log_debug(f"Updating appointment: {appointment_id}")
        try:
            self.cursor.execute("""
                UPDATE appointments SET
                patient_id = ?, doctor_id = ?, appointment_date = ?,
                appointment_time = ?, status = ?, notes = ?
                WHERE appointment_id = ?
            """, (
                appointment_data['patient_id'],
                appointment_data['doctor_id'],
                appointment_data['appointment_date'],
                appointment_data['appointment_time'],
                appointment_data.get('status', 'Scheduled'),
                appointment_data.get('notes', ''),
                appointment_id
            ))
            self.conn.commit()
            log_database_operation("UPDATE", "appointments", True, f"Appointment ID: {appointment_id}")
            log_info(f"Appointment updated successfully: {appointment_id}")
            return True
        except Exception as e:
            log_database_operation("UPDATE", "appointments", False, f"Appointment ID: {appointment_id} - Error: {str(e)}")
            log_error(f"Error updating appointment: {appointment_id}", e)
            return False

    # Admission (IPD) operations
    def add_admission(self, admission_data: Dict) -> bool:
        """Add a new in-patient admission"""
        try:
            admission_date = admission_data.get('admission_date')
            expected_days = int(admission_data.get('expected_days') or 0)
            expected_discharge_date = admission_data.get('expected_discharge_date', '')

            if admission_date and expected_days > 0 and not expected_discharge_date:
                try:
                    expected_discharge_date = (datetime.strptime(admission_date, '%Y-%m-%d') + timedelta(days=expected_days)).strftime('%Y-%m-%d')
                except Exception:
                    expected_discharge_date = ''

            self.cursor.execute("""
                INSERT INTO admissions (
                    admission_id, patient_id, doctor_id, admission_date,
                    expected_days, expected_discharge_date,
                    status, ward, bed, reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                admission_data['admission_id'],
                admission_data['patient_id'],
                admission_data.get('doctor_id'),
                admission_date,
                expected_days,
                expected_discharge_date,
                admission_data.get('status', 'Admitted'),
                admission_data.get('ward', ''),
                admission_data.get('bed', ''),
                admission_data.get('reason', '')
            ))
            self.conn.commit()
            log_info(f"Admission added successfully: {admission_data['admission_id']}")
            return True
        except sqlite3.IntegrityError as e:
            log_error(f"Failed to add admission (integrity error): {admission_data.get('admission_id')}", e)
            return False
        except Exception as e:
            log_error(f"Failed to add admission: {admission_data.get('admission_id')}", e)
            return False

    def get_admissions_by_patient(self, patient_id: str) -> List[Dict]:
        """Get admissions for a patient (latest first)"""
        self.cursor.execute("""
            SELECT a.*,
                   d.first_name || ' ' || d.last_name AS doctor_name
            FROM admissions a
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = ?
            ORDER BY a.admission_date DESC, a.created_at DESC
        """, (patient_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_active_admission_by_patient(self, patient_id: str) -> Optional[Dict]:
        """Get the current active admission for a patient (if any)"""
        self.cursor.execute("""
            SELECT a.*,
                   d.first_name || ' ' || d.last_name AS doctor_name
            FROM admissions a
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = ? AND a.status = 'Admitted'
            ORDER BY a.admission_date DESC, a.created_at DESC
            LIMIT 1
        """, (patient_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_active_admissions(self) -> List[Dict]:
        """Get all currently active admissions with patient and doctor details"""
        self.cursor.execute("""
            SELECT a.*,
                   p.first_name || ' ' || p.last_name AS patient_name,
                   p.patient_id,
                   d.first_name || ' ' || d.last_name AS doctor_name
            FROM admissions a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.status = 'Admitted'
            ORDER BY a.admission_date DESC, a.created_at DESC
        """)
        return [dict(row) for row in self.cursor.fetchall()]

    def discharge_admission(self, admission_id: str, discharge_date: str = None, discharge_summary: str = '') -> bool:
        """Discharge an admission"""
        try:
            discharge_date = discharge_date or datetime.now().strftime('%Y-%m-%d')
            self.cursor.execute("""
                UPDATE admissions SET
                    discharge_date = ?,
                    discharge_summary = ?,
                    status = 'Discharged',
                    updated_at = ?
                WHERE admission_id = ?
            """, (discharge_date, discharge_summary or '', datetime.now().isoformat(), admission_id))
            self.conn.commit()
            log_info(f"Admission discharged: {admission_id}")
            return True
        except Exception as e:
            log_error(f"Failed to discharge admission: {admission_id}", e)
            return False

    def add_admission_note(self, note_data: Dict) -> bool:
        """Add a daily progress note for an admission"""
        try:
            self.cursor.execute("""
                INSERT INTO admission_notes (
                    note_id, admission_id, note_date, note_time,
                    note_text, created_by
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                note_data['note_id'],
                note_data['admission_id'],
                note_data['note_date'],
                note_data.get('note_time', ''),
                note_data['note_text'],
                note_data.get('created_by', '')
            ))
            self.conn.commit()
            log_info(f"Admission note added successfully: {note_data['note_id']}")
            return True
        except sqlite3.IntegrityError as e:
            log_error(f"Failed to add admission note (integrity error): {note_data.get('note_id')}", e)
            return False
        except Exception as e:
            log_error(f"Failed to add admission note: {note_data.get('note_id')}", e)
            return False

    def get_admission_notes(self, admission_id: str) -> List[Dict]:
        """Get progress notes for an admission (oldest first) with computed day number"""
        self.cursor.execute("""
            SELECT n.*,
                   a.admission_date,
                   CAST((julianday(n.note_date) - julianday(a.admission_date)) AS INTEGER) + 1 AS day_number
            FROM admission_notes n
            JOIN admissions a ON n.admission_id = a.admission_id
            WHERE n.admission_id = ?
            ORDER BY n.note_date ASC, n.created_at ASC
        """, (admission_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    # Prescription operations
    def add_prescription(self, prescription_data: Dict, items: List[Dict]) -> bool:
        """Add a new prescription with items"""
        log_debug(f"Adding prescription: {prescription_data.get('prescription_id')}")
        try:
            self.cursor.execute("""
                INSERT INTO prescriptions (prescription_id, patient_id, doctor_id,
                appointment_id, prescription_date, diagnosis, notes,
                weight, spo2, hr, rr, bp, height, ideal_body_weight,
                follow_up_date, icd_codes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prescription_data['prescription_id'],
                prescription_data['patient_id'],
                prescription_data['doctor_id'],
                prescription_data.get('appointment_id'),
                prescription_data['prescription_date'],
                prescription_data.get('diagnosis', ''),
                prescription_data.get('notes', ''),
                prescription_data.get('weight', ''),
                prescription_data.get('spo2', ''),
                prescription_data.get('hr', ''),
                prescription_data.get('rr', ''),
                prescription_data.get('bp', ''),
                prescription_data.get('height', ''),
                prescription_data.get('ideal_body_weight', ''),
                prescription_data.get('follow_up_date', ''),
                prescription_data.get('icd_codes', '')
            ))
            
            for item in items:
                self.cursor.execute("""
                    INSERT INTO prescription_items (prescription_id, medicine_name,
                    dosage, frequency, duration, instructions, purpose)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    prescription_data['prescription_id'],
                    item['medicine_name'],
                    item['dosage'],
                    item['frequency'],
                    item['duration'],
                    item.get('instructions', ''),
                    item.get('purpose', '')
                ))
            
            self.conn.commit()
            log_info(f"Prescription added successfully: {prescription_data['prescription_id']}")
            return True
        except Exception as e:
            log_error(f"Failed to add prescription: {prescription_data.get('prescription_id')}", e)
            return False
    
    def get_all_prescriptions(self) -> List[Dict]:
        """Get all prescriptions"""
        self.cursor.execute("""
            SELECT p.*, d.first_name || ' ' || d.last_name as doctor_name,
            pat.first_name || ' ' || pat.last_name as patient_name
            FROM prescriptions p
            LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
            LEFT JOIN patients pat ON p.patient_id = pat.patient_id
            ORDER BY p.prescription_date DESC
        """)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_prescriptions_by_date(self, date: str) -> List[Dict]:
        """Get prescriptions by date"""
        self.cursor.execute("""
            SELECT p.*, d.first_name || ' ' || d.last_name as doctor_name,
            pat.first_name || ' ' || pat.last_name as patient_name
            FROM prescriptions p
            LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
            LEFT JOIN patients pat ON p.patient_id = pat.patient_id
            WHERE p.prescription_date = ?
            ORDER BY p.prescription_date DESC
        """, (date,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_prescriptions_by_patient(self, patient_id: str) -> List[Dict]:
        """Get all prescriptions for a patient"""
        self.cursor.execute("""
            SELECT p.*, d.first_name || ' ' || d.last_name as doctor_name,
            pat.first_name || ' ' || pat.last_name as patient_name
            FROM prescriptions p
            LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
            LEFT JOIN patients pat ON p.patient_id = pat.patient_id
            WHERE p.patient_id = ?
            ORDER BY p.prescription_date DESC
        """, (patient_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_prescriptions_by_patient_name(self, patient_name: str) -> List[Dict]:
        """Get prescriptions by patient name (searches first name and last name)"""
        self.cursor.execute("""
            SELECT p.*, d.first_name || ' ' || d.last_name as doctor_name,
            pat.first_name || ' ' || pat.last_name as patient_name
            FROM prescriptions p
            LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
            LEFT JOIN patients pat ON p.patient_id = pat.patient_id
            WHERE pat.first_name LIKE ? OR pat.last_name LIKE ? 
            OR (pat.first_name || ' ' || pat.last_name) LIKE ?
            ORDER BY p.prescription_date DESC
        """, (f'%{patient_name}%', f'%{patient_name}%', f'%{patient_name}%'))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_prescription_items(self, prescription_id: str) -> List[Dict]:
        """Get items for a prescription"""
        self.cursor.execute("""
            SELECT * FROM prescription_items WHERE prescription_id = ?
        """, (prescription_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_prescription_by_id(self, prescription_id: str) -> Dict:
        """Get a prescription by ID"""
        self.cursor.execute("""
            SELECT p.*, d.first_name || ' ' || d.last_name as doctor_name
            FROM prescriptions p
            LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
            WHERE p.prescription_id = ?
        """, (prescription_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_prescription(self, prescription_id: str, prescription_data: Dict, items: List[Dict]) -> bool:
        """Update an existing prescription with items"""
        log_debug(f"Updating prescription: {prescription_id}")
        try:
            # Update prescription
            self.cursor.execute("""
                UPDATE prescriptions 
                SET patient_id = ?, doctor_id = ?, appointment_id = ?,
                    prescription_date = ?, diagnosis = ?, notes = ?,
                    weight = ?, spo2 = ?, hr = ?, rr = ?, bp = ?,
                    height = ?, ideal_body_weight = ?, follow_up_date = ?, icd_codes = ?
                WHERE prescription_id = ?
            """, (
                prescription_data['patient_id'],
                prescription_data['doctor_id'],
                prescription_data.get('appointment_id'),
                prescription_data['prescription_date'],
                prescription_data.get('diagnosis', ''),
                prescription_data.get('notes', ''),
                prescription_data.get('weight', ''),
                prescription_data.get('spo2', ''),
                prescription_data.get('hr', ''),
                prescription_data.get('rr', ''),
                prescription_data.get('bp', ''),
                prescription_data.get('height', ''),
                prescription_data.get('ideal_body_weight', ''),
                prescription_data.get('follow_up_date', ''),
                prescription_data.get('icd_codes', ''),
                prescription_id
            ))
            
            # Delete existing items
            self.cursor.execute("""
                DELETE FROM prescription_items WHERE prescription_id = ?
            """, (prescription_id,))
            
            # Insert new items
            for item in items:
                self.cursor.execute("""
                    INSERT INTO prescription_items (prescription_id, medicine_name,
                    dosage, frequency, duration, instructions, purpose)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    prescription_id,
                    item['medicine_name'],
                    item['dosage'],
                    item['frequency'],
                    item['duration'],
                    item.get('instructions', ''),
                    item.get('purpose', '')
                ))
            
            self.conn.commit()
            log_info(f"Prescription updated successfully: {prescription_id}")
            return True
        except Exception as e:
            log_error(f"Failed to update prescription: {prescription_id}", e)
            return False
    
    def get_all_medicines(self) -> List[str]:
        """Get all unique medicine names from medicines_master table"""
        try:
            self.cursor.execute("""
                SELECT DISTINCT medicine_name FROM medicines_master 
                ORDER BY medicine_name ASC
            """)
            medicines = [row[0] for row in self.cursor.fetchall()]
            log_debug(f"Retrieved {len(medicines)} unique medicines from medicines_master table")
            return medicines
        except Exception as e:
            log_error("Failed to retrieve medicines from medicines_master table", e)
            return []
    
    # Billing operations
    def add_bill(self, bill_data: Dict) -> bool:
        """Add a new bill"""
        log_debug(f"Adding bill: {bill_data.get('bill_id')}")
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
            log_info(f"Bill added successfully: {bill_data['bill_id']}")
            return True
        except sqlite3.IntegrityError as e:
            log_error(f"Failed to add bill (integrity error): {bill_data.get('bill_id')}", e)
            return False
        except Exception as e:
            log_error(f"Failed to add bill: {bill_data.get('bill_id')}", e)
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
    
    def get_bills_by_patient_id(self, patient_id: str) -> List[Dict]:
        """Get bills by patient ID"""
        self.cursor.execute("""
            SELECT b.*, p.first_name || ' ' || p.last_name as patient_name
            FROM billing b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            WHERE b.patient_id = ?
            ORDER BY b.bill_date DESC
        """, (patient_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    # X-ray reports operations
    def add_xray_report(
        self,
        patient_id: str,
        report_date: str,
        body_part: str,
        findings: str,
        file_path: str,
        file_name_original: str,
        report_id: Optional[str] = None,
    ) -> Optional[str]:
        """Add an X-ray report. Returns report_id on success, None on failure.
        If report_id is not provided, one is generated."""
        if not report_id:
            report_id = generate_id("XR")
        try:
            self.cursor.execute("""
                INSERT INTO xray_reports (
                    report_id, patient_id, report_date, body_part,
                    findings, file_path, file_name_original
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (report_id, patient_id, report_date, body_part or "", findings or "",
                  file_path, file_name_original or ""))
            self.conn.commit()
            log_info(f"X-ray report added: {report_id}")
            return report_id
        except sqlite3.IntegrityError as e:
            log_error(f"Failed to add X-ray report (integrity error): {report_id}", e)
            return None
        except Exception as e:
            log_error(f"Failed to add X-ray report: {report_id}", e)
            return None

    def get_xray_reports_by_patient(self, patient_id: str) -> List[Dict]:
        """Get all X-ray reports for a patient, ordered by report_date DESC."""
        try:
            self.cursor.execute("""
                SELECT report_id, patient_id, report_date, body_part, findings, file_path, file_name_original
                FROM xray_reports
                WHERE patient_id = ?
                ORDER BY report_date DESC
            """, (str(patient_id),))
            rows = self.cursor.fetchall()
            # Use column names as keys (sqlite3.Row: dict(row) may not work in all environments)
            result = []
            for row in rows:
                try:
                    result.append(dict(zip(row.keys(), row)))
                except Exception:
                    result.append(dict(row))
            return result
        except Exception as e:
            log_error("get_xray_reports_by_patient failed", e)
            return []

    def get_xray_report_by_id(self, report_id: str) -> Optional[Dict]:
        """Get a single X-ray report by report_id."""
        self.cursor.execute(
            "SELECT * FROM xray_reports WHERE report_id = ?", (report_id,)
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def delete_xray_report(self, report_id: str) -> bool:
        """Delete an X-ray report by report_id. Caller should delete file on disk."""
        try:
            self.cursor.execute("DELETE FROM xray_reports WHERE report_id = ?", (report_id,))
            self.conn.commit()
            log_info(f"X-ray report deleted: {report_id}")
            return True
        except Exception as e:
            log_error(f"Failed to delete X-ray report: {report_id}", e)
            return False

    def get_bills_by_patient_name(self, patient_name: str) -> List[Dict]:
        """Get bills by patient name (searches first name and last name)"""
        self.cursor.execute("""
            SELECT b.*, p.first_name || ' ' || p.last_name as patient_name
            FROM billing b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            WHERE p.first_name LIKE ? OR p.last_name LIKE ? 
            OR (p.first_name || ' ' || p.last_name) LIKE ?
            ORDER BY b.bill_date DESC
        """, (f'%{patient_name}%', f'%{patient_name}%', f'%{patient_name}%'))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_bills_by_date(self, date: str) -> List[Dict]:
        """Get bills by date"""
        self.cursor.execute("""
            SELECT b.*, p.first_name || ' ' || p.last_name as patient_name
            FROM billing b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            WHERE b.bill_date = ?
            ORDER BY b.bill_date DESC
        """, (date,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_bills_by_status(self, status: str) -> List[Dict]:
        """Get bills by payment status"""
        self.cursor.execute("""
            SELECT b.*, p.first_name || ' ' || p.last_name as patient_name
            FROM billing b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            WHERE b.payment_status = ?
            ORDER BY b.bill_date DESC
        """, (status,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_bills_by_patient_name_and_date(self, patient_name: str, date: str) -> List[Dict]:
        """Get bills by patient name and date"""
        self.cursor.execute("""
            SELECT b.*, p.first_name || ' ' || p.last_name as patient_name
            FROM billing b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            WHERE (p.first_name LIKE ? OR p.last_name LIKE ? 
            OR (p.first_name || ' ' || p.last_name) LIKE ?) AND b.bill_date = ?
            ORDER BY b.bill_date DESC
        """, (f'%{patient_name}%', f'%{patient_name}%', f'%{patient_name}%', date))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_bills_by_patient_name_and_status(self, patient_name: str, status: str) -> List[Dict]:
        """Get bills by patient name and status"""
        self.cursor.execute("""
            SELECT b.*, p.first_name || ' ' || p.last_name as patient_name
            FROM billing b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            WHERE (p.first_name LIKE ? OR p.last_name LIKE ? 
            OR (p.first_name || ' ' || p.last_name) LIKE ?) AND b.payment_status = ?
            ORDER BY b.bill_date DESC
        """, (f'%{patient_name}%', f'%{patient_name}%', f'%{patient_name}%', status))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_bills_by_date_and_status(self, date: str, status: str) -> List[Dict]:
        """Get bills by date and status"""
        self.cursor.execute("""
            SELECT b.*, p.first_name || ' ' || p.last_name as patient_name
            FROM billing b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            WHERE b.bill_date = ? AND b.payment_status = ?
            ORDER BY b.bill_date DESC
        """, (date, status))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_bills_by_patient_name_date_and_status(self, patient_name: str, date: str, status: str) -> List[Dict]:
        """Get bills by patient name, date and status"""
        self.cursor.execute("""
            SELECT b.*, p.first_name || ' ' || p.last_name as patient_name
            FROM billing b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            WHERE (p.first_name LIKE ? OR p.last_name LIKE ? 
            OR (p.first_name || ' ' || p.last_name) LIKE ?) 
            AND b.bill_date = ? AND b.payment_status = ?
            ORDER BY b.bill_date DESC
        """, (f'%{patient_name}%', f'%{patient_name}%', f'%{patient_name}%', date, status))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_bill_by_id(self, bill_id: str) -> Optional[Dict]:
        """Get bill by ID"""
        self.cursor.execute("""
            SELECT b.*, p.first_name || ' ' || p.last_name as patient_name
            FROM billing b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            WHERE b.bill_id = ?
        """, (bill_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_bill(self, bill_id: str, bill_data: Dict) -> bool:
        """Update an existing bill"""
        log_debug(f"Updating bill: {bill_id}")
        try:
            self.cursor.execute("""
                UPDATE billing SET
                patient_id = ?, appointment_id = ?, bill_date = ?,
                consultation_fee = ?, medicine_cost = ?, other_charges = ?,
                total_amount = ?, payment_status = ?, payment_method = ?, notes = ?
                WHERE bill_id = ?
            """, (
                bill_data['patient_id'],
                bill_data.get('appointment_id'),
                bill_data['bill_date'],
                bill_data.get('consultation_fee', 0),
                bill_data.get('medicine_cost', 0),
                bill_data.get('other_charges', 0),
                bill_data['total_amount'],
                bill_data.get('payment_status', 'Pending'),
                bill_data.get('payment_method', ''),
                bill_data.get('notes', ''),
                bill_id
            ))
            self.conn.commit()
            log_info(f"Bill updated successfully: {bill_id}")
            return True
        except Exception as e:
            log_error(f"Failed to update bill: {bill_id}", e)
            return False
    
    def delete_bill(self, bill_id: str) -> bool:
        """Delete a bill"""
        log_debug(f"Deleting bill: {bill_id}")
        try:
            self.cursor.execute("DELETE FROM billing WHERE bill_id = ?", (bill_id,))
            self.conn.commit()
            log_info(f"Bill deleted successfully: {bill_id}")
            return True
        except Exception as e:
            log_error(f"Failed to delete bill: {bill_id}", e)
            return False
    
    def get_statistics(self, filter_type: str = 'all', filter_date: str = None) -> Dict:
        """Get system statistics with optional filters
        
        Args:
            filter_type: 'all', 'daily', 'monthly', 'yearly', 'datewise'
            filter_date: Date string in 'YYYY-MM-DD' format (required for 'daily' and 'datewise')
        """
        stats = {}
        
        # Build date filter conditions for appointments, bills, and admissions
        appointment_filter = ""
        bill_filter = ""
        admission_filter = ""
        
        if filter_type == 'daily' and filter_date:
            appointment_filter = f"AND appointment_date = '{filter_date}'"
            bill_filter = f"AND bill_date = '{filter_date}'"
            admission_filter = f"AND admission_date = '{filter_date}'"
        elif filter_type == 'monthly' and filter_date:
            # filter_date should be in 'YYYY-MM' format
            appointment_filter = f"AND strftime('%Y-%m', appointment_date) = '{filter_date}'"
            bill_filter = f"AND strftime('%Y-%m', bill_date) = '{filter_date}'"
            admission_filter = f"AND strftime('%Y-%m', admission_date) = '{filter_date}'"
        elif filter_type == 'yearly' and filter_date:
            # filter_date should be in 'YYYY' format
            appointment_filter = f"AND strftime('%Y', appointment_date) = '{filter_date}'"
            bill_filter = f"AND strftime('%Y', bill_date) = '{filter_date}'"
            admission_filter = f"AND strftime('%Y', admission_date) = '{filter_date}'"
        elif filter_type == 'datewise' and filter_date:
            appointment_filter = f"AND appointment_date = '{filter_date}'"
            bill_filter = f"AND bill_date = '{filter_date}'"
            admission_filter = f"AND admission_date = '{filter_date}'"
        
        # Total patients and doctors are not date-filtered (they're cumulative)
        self.cursor.execute("SELECT COUNT(*) FROM patients")
        stats['total_patients'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM doctors")
        stats['total_doctors'] = self.cursor.fetchone()[0]
        
        # Appointments with date filter
        if appointment_filter:
            self.cursor.execute(f"SELECT COUNT(*) FROM appointments WHERE status = 'Scheduled' {appointment_filter}")
            stats['scheduled_appointments'] = self.cursor.fetchone()[0]
            
            self.cursor.execute(f"SELECT COUNT(*) FROM appointments WHERE status = 'Completed' {appointment_filter}")
            stats['completed_appointments'] = self.cursor.fetchone()[0]
        else:
            self.cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'Scheduled'")
            stats['scheduled_appointments'] = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'Completed'")
            stats['completed_appointments'] = self.cursor.fetchone()[0]
        
        # Admissions statistics
        # Active admissions (currently admitted) - not date-filtered as they're current state
        self.cursor.execute("SELECT COUNT(*) FROM admissions WHERE status = 'Admitted'")
        stats['active_admissions'] = self.cursor.fetchone()[0]
        
        # Total admissions (all time or filtered by date)
        if admission_filter:
            self.cursor.execute(f"SELECT COUNT(*) FROM admissions WHERE 1=1 {admission_filter}")
            stats['total_admissions'] = self.cursor.fetchone()[0]
            
            self.cursor.execute(f"SELECT COUNT(*) FROM admissions WHERE status = 'Discharged' {admission_filter}")
            stats['discharged_admissions'] = self.cursor.fetchone()[0]
        else:
            self.cursor.execute("SELECT COUNT(*) FROM admissions")
            stats['total_admissions'] = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM admissions WHERE status = 'Discharged'")
            stats['discharged_admissions'] = self.cursor.fetchone()[0]
        
        # Revenue with date filter
        if bill_filter:
            self.cursor.execute(f"SELECT SUM(total_amount) FROM billing WHERE payment_status = 'Paid' {bill_filter}")
        else:
            self.cursor.execute("SELECT SUM(total_amount) FROM billing WHERE payment_status = 'Paid'")
        result = self.cursor.fetchone()[0]
        stats['total_revenue'] = result if result else 0
        
        return stats
    
    def get_daily_statistics(self, date_str: str) -> Dict:
        """Get statistics for a specific date"""
        return self.get_statistics('daily', date_str)
    
    def get_monthly_statistics(self, month_str: str) -> Dict:
        """Get statistics for a specific month (format: 'YYYY-MM')"""
        return self.get_statistics('monthly', month_str)
    
    def get_yearly_statistics(self, year_str: str) -> Dict:
        """Get statistics for a specific year (format: 'YYYY')"""
        return self.get_statistics('yearly', year_str)
    
    def get_datewise_statistics(self, date_str: str) -> Dict:
        """Get statistics for a specific date (same as daily)"""
        return self.get_statistics('datewise', date_str)
    
    def get_date_range_statistics(self, from_date: str, to_date: str) -> Dict:
        """Get statistics for a date range"""
        stats = {}
        
        # Build date filter conditions for appointments, bills, and admissions
        appointment_filter = f"AND appointment_date >= '{from_date}' AND appointment_date <= '{to_date}'"
        bill_filter = f"AND bill_date >= '{from_date}' AND bill_date <= '{to_date}'"
        admission_filter = f"AND admission_date >= '{from_date}' AND admission_date <= '{to_date}'"
        
        # Total patients and doctors are not date-filtered (they're cumulative)
        self.cursor.execute("SELECT COUNT(*) FROM patients")
        stats['total_patients'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM doctors")
        stats['total_doctors'] = self.cursor.fetchone()[0]
        
        # Appointments with date range filter
        self.cursor.execute(f"SELECT COUNT(*) FROM appointments WHERE status = 'Scheduled' {appointment_filter}")
        stats['scheduled_appointments'] = self.cursor.fetchone()[0]
        
        self.cursor.execute(f"SELECT COUNT(*) FROM appointments WHERE status = 'Completed' {appointment_filter}")
        stats['completed_appointments'] = self.cursor.fetchone()[0]
        
        # Admissions statistics
        # Active admissions (currently admitted) - not date-filtered as they're current state
        self.cursor.execute("SELECT COUNT(*) FROM admissions WHERE status = 'Admitted'")
        stats['active_admissions'] = self.cursor.fetchone()[0]
        
        # Total admissions in date range
        self.cursor.execute(f"SELECT COUNT(*) FROM admissions WHERE 1=1 {admission_filter}")
        stats['total_admissions'] = self.cursor.fetchone()[0]
        
        # Discharged admissions in date range
        self.cursor.execute(f"SELECT COUNT(*) FROM admissions WHERE status = 'Discharged' {admission_filter}")
        stats['discharged_admissions'] = self.cursor.fetchone()[0]
        
        # Revenue with date range filter
        self.cursor.execute(f"SELECT SUM(total_amount) FROM billing WHERE payment_status = 'Paid' {bill_filter}")
        result = self.cursor.fetchone()[0]
        stats['total_revenue'] = result if result else 0
        
        return stats
    
    def get_todays_appointments(self, date: str = None) -> List[Dict]:
        """Get today's appointments"""
        from utils.helpers import get_current_date
        if not date:
            date = get_current_date()
        
        self.cursor.execute("""
            SELECT a.*, p.first_name || ' ' || p.last_name as patient_name,
            d.first_name || ' ' || d.last_name as doctor_name,
            d.specialization
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_date = ?
            ORDER BY a.appointment_time ASC
        """, (date,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_recent_activities(self, limit: int = 10) -> List[Dict]:
        """Get recent activities from appointments, patients, and bills"""
        activities = []
        
        # Recent patients
        self.cursor.execute("""
            SELECT 'patient' as type, patient_id as id, first_name || ' ' || last_name as name,
            'registered' as action, created_at as timestamp
            FROM patients
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        for row in self.cursor.fetchall():
            activities.append(dict(row))
        
        # Recent appointments
        self.cursor.execute("""
            SELECT 'appointment' as type, appointment_id as id, 
            p.first_name || ' ' || p.last_name as name,
            'completed' as action, a.appointment_date || ' ' || a.appointment_time as timestamp
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            WHERE a.status = 'Completed'
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
            LIMIT ?
        """, (limit,))
        for row in self.cursor.fetchall():
            activities.append(dict(row))
        
        # Recent bills
        self.cursor.execute("""
            SELECT 'bill' as type, bill_id as id,
            p.first_name || ' ' || p.last_name as name,
            'generated' as action, b.bill_date as timestamp
            FROM billing b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            ORDER BY b.bill_date DESC, b.created_at DESC
            LIMIT ?
        """, (limit,))
        for row in self.cursor.fetchall():
            activities.append(dict(row))
        
        # Sort by timestamp and return limited results
        activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return activities[:limit]
    
    # Medicine master operations
    def populate_medicines(self) -> None:
        """Populate medicines master table with comprehensive branded medicine list"""
        # Check if medicines already exist
        self.cursor.execute("SELECT COUNT(*) FROM medicines_master")
        count = self.cursor.fetchone()[0]
        if count > 0:
            log_debug(f"Medicines master table already has {count} records, skipping population")
            return
        
        log_info("Populating medicines master table with branded medicines...")
        
        medicines = [
            # ===== PAIN & FEVER =====
            ("Paracetamol", "Dolo", "Pain & Fever", "650mg", "Tablet", 0),
            ("Paracetamol", "Calpol", "Pain & Fever", "500mg", "Tablet", 0),
            ("Paracetamol", "Calpol", "Pain & Fever", "250mg/5ml", "Syrup", 1),
            ("Paracetamol", "Crocin Advance", "Pain & Fever", "500mg", "Tablet", 0),
            ("Ibuprofen", "Brufen", "Pain & Fever", "400mg", "Tablet", 0),
            ("Ibuprofen", "Ibugesic", "Pain & Fever", "100mg/5ml", "Suspension", 1),
            ("Paracetamol+Ibuprofen", "Combiflam", "Pain & Fever", "400mg/325mg", "Tablet", 0),
            ("Aspirin", "Ecosprin", "Pain & Fever", "75mg", "Tablet", 0),
            ("Diclofenac", "Voveran", "Pain & Fever", "50mg", "Tablet", 0),
            ("Aceclofenac", "Hifenac", "Pain & Fever", "100mg", "Tablet", 0),
            ("Naproxen", "Naprosyn", "Pain & Fever", "500mg", "Tablet", 0),

            # ===== ANTACID & GASTRIC =====
            ("Pantoprazole", "Pantocid", "Acidity", "40mg", "Tablet", 0),
            ("Pantoprazole", "Pantocid", "Acidity", "4mg/ml", "Injection", 0),
            ("Omeprazole", "Omez", "Acidity", "20mg", "Capsule", 0),
            ("Ranitidine", "Rantac", "Acidity", "150mg", "Tablet", 0),
            ("Sucralfate", "Sucral", "Acidity", "1g/5ml", "Syrup", 0),
            ("Digene", "Digene", "Acidity", "Chewable", "Tablet", 0),
            ("Domperidone", "Domstal", "Nausea", "10mg", "Tablet", 0),
            ("ORS", "Electral", "Rehydration", "21g Sachet", "Powder", 1),
            ("ORS", "Pedialyte", "Rehydration", "Sachet", "Powder", 1),

            # ===== COUGH & COLD =====
            ("Cetirizine", "Cetzine", "Allergy", "10mg", "Tablet", 0),
            ("Cetirizine", "Cetzine", "Allergy", "5mg/5ml", "Syrup", 1),
            ("Levocetirizine", "Levocet", "Allergy", "5mg", "Tablet", 0),
            ("Dextromethorphan", "Benadryl", "Cough", "15mg/5ml", "Syrup", 1),
            ("Ambroxol", "Mucosolvan", "Cough", "30mg/5ml", "Syrup", 1),
            ("Montelukast+Levocetirizine", "Montair-LC", "Respiratory", "10mg/5mg", "Tablet", 0),
            ("Phenylephrine", "Sudafed", "Cold", "10mg", "Tablet", 0),

            # ===== VITAMINS & MINERALS =====
            ("Vitamin C", "Limcee", "Vitamin", "500mg", "Tablet", 0),
            ("Vitamin D3", "D-Rise", "Vitamin", "60k IU", "Capsule", 0),
            ("Iron+Folic Acid", "Fefol", "Supplement", "100mg/1mg", "Tablet", 0),
            ("Zinc", "Zinconia", "Supplement", "20mg", "Tablet", 1),
            ("Multivitamin", "Becosules", "Vitamin", "Capsule", "Capsule", 0),

            # ===== BASIC INJECTIONS =====
            ("Paracetamol", "Paracip", "Pain & Fever", "150mg/ml", "Injection", 0),
            ("Ranitidine", "Zinetac", "Acidity", "25mg/ml", "Injection", 0),

            # ===== ANTIBIOTICS =====
            ("Amoxicillin+Clavulanic Acid", "Augmentin", "Antibiotic", "625mg", "Tablet", 0),
            ("Amoxicillin+Clavulanic Acid", "Augmentin", "Antibiotic", "228mg/5ml", "Syrup", 1),
            ("Amoxicillin", "Mox", "Antibiotic", "500mg", "Capsule", 0),
            ("Amoxicillin", "Mox Kid", "Antibiotic", "250mg/5ml", "Syrup", 1),
            ("Cefixime", "Taxim-O", "Antibiotic", "200mg", "Tablet", 0),
            ("Cefixime", "Suprax", "Antibiotic", "100mg/5ml", "Syrup", 1),
            ("Cefdinir", "Omnicef", "Antibiotic", "300mg", "Capsule", 0),
            ("Azithromycin", "Azithral", "Antibiotic", "500mg", "Tablet", 0),
            ("Azithromycin", "Zithromax", "Antibiotic", "200mg/5ml", "Suspension", 1),
            ("Ciprofloxacin", "Cifran", "Antibiotic", "500mg", "Tablet", 0),
            ("Levofloxacin", "Levoflox", "Antibiotic", "500mg", "Tablet", 0),
            ("Ofloxacin", "Oflox", "Antibiotic", "200mg", "Tablet", 0),
            ("Metronidazole", "Flagyl", "Antibiotic", "400mg", "Tablet", 0),
            ("Metronidazole", "Metrogyl", "Antibiotic", "200mg/5ml", "Suspension", 1),
            ("Doxycycline", "Doxy", "Antibiotic", "100mg", "Tablet", 0),
            ("Clarithromycin", "Claribid", "Antibiotic", "500mg", "Tablet", 0),
            ("Linezolid", "Linox", "Antibiotic", "600mg", "Tablet", 0),
            ("Ceftriaxone", "Monocef", "Antibiotic", "1g", "Injection", 0),
            ("Piperacillin+Tazobactam", "Piptaz", "Antibiotic", "4.5g", "Injection", 0),
            ("Meropenem", "Meromac", "Antibiotic", "1g", "Injection", 0),
            ("Vancomycin", "Vancobin", "Antibiotic", "500mg", "Injection", 0),
            ("Gentamicin", "Genticyn", "Antibiotic", "80mg/2ml", "Injection", 1),

            # ===== UTI, GYNAE =====
            ("Nitrofurantoin", "Macrodantin", "UTI", "100mg", "Capsule", 0),
            ("Fosfomycin", "Fosfomed", "UTI", "3g", "Sachet", 0),
            ("Tinidazole", "Tini", "Gynecological", "500mg", "Tablet", 0),

            # ===== ANTI TUBERCULAR THERAPY (ATT) =====
            ("Isoniazid", "Isonex", "ATT", "300mg", "Tablet", 0),
            ("Rifampicin", "R-Cin", "ATT", "450mg", "Capsule", 0),
            ("Ethambutol", "Combutol", "ATT", "800mg", "Tablet", 0),
            ("Pyrazinamide", "Zid", "ATT", "750mg", "Tablet", 0),

            # ===== ANTIFUNGALS =====
            ("Fluconazole", "Flucos", "Antifungal", "150mg", "Tablet", 0),
            ("Clotrimazole", "Candid", "Antifungal", "1%", "Cream", 0),
            ("Terbinafine", "Terbinaforce", "Antifungal", "250mg", "Tablet", 0),

            # ===== ANTIVIRALS =====
            ("Acyclovir", "Zovirax", "Antiviral", "400mg", "Tablet", 0),
            ("Oseltamivir", "Tamiflu", "Antiviral", "75mg", "Capsule", 0),

            # ===== CARDIAC / BLOOD PRESSURE =====
            ("Amlodipine", "Amlong", "Hypertension", "5mg", "Tablet", 0),
            ("Telmisartan", "Telma", "Hypertension", "40mg", "Tablet", 0),
            ("Losartan", "Losar", "Hypertension", "50mg", "Tablet", 0),
            ("Metoprolol", "Betaloc", "Hypertension", "50mg", "Tablet", 0),
            ("Atenolol", "Tenormin", "Hypertension", "50mg", "Tablet", 0),
            ("Enalapril", "Enam", "Hypertension", "5mg", "Tablet", 0),
            ("Clonidine", "Arkamin", "Hypertension", "100mcg", "Tablet", 0),

            # ===== CHOLESTEROL =====
            ("Atorvastatin", "Atorva", "Cholesterol", "10mg", "Tablet", 0),
            ("Rosuvastatin", "Crestor", "Cholesterol", "10mg", "Tablet", 0),
            ("Simvastatin", "Simvotin", "Cholesterol", "20mg", "Tablet", 0),

            # ===== DIABETES =====
            ("Metformin", "Glycomet", "Diabetes", "500mg", "Tablet", 0),
            ("Glimepiride", "Amaryl", "Diabetes", "2mg", "Tablet", 0),
            ("Gliclazide", "Diamicron", "Diabetes", "80mg", "Tablet", 0),
            ("Sitagliptin", "Januvia", "Diabetes", "100mg", "Tablet", 0),
            ("Insulin Regular", "Actrapid", "Diabetes", "100IU/ml", "Injection", 0),
            ("Insulin Glargine", "Lantus", "Diabetes", "100IU/ml", "Injection", 0),

            # ===== THYROID =====
            ("Levothyroxine", "Thyronorm", "Thyroid", "50mcg", "Tablet", 0),
            ("Levothyroxine", "Thyronorm", "Thyroid", "100mcg", "Tablet", 0),

            # ===== ORTHO / PAIN / NEURO =====
            ("Gabapentin", "Gabapin", "Neuropathic Pain", "300mg", "Capsule", 0),
            ("Pregabalin", "Lyrica", "Neuropathic Pain", "75mg", "Capsule", 0),
            ("Duloxetine", "Duzela", "Pain & Depression", "30mg", "Capsule", 0),
            ("Tramadol", "Ultracet", "Severe Pain", "50mg", "Tablet", 0),
            ("Etoricoxib", "Arcoxia", "Pain & Ortho", "60mg", "Tablet", 0),
            ("Tizanidine", "Sirdalud", "Muscle Relaxant", "2mg", "Tablet", 0),

            # ===== ASTHMA & COPD =====
            ("Salbutamol", "Asthalin", "Asthma", "100mcg", "Inhaler", 0),
            ("Formoterol+Budesonide", "Foracort", "Asthma", "200mcg", "Inhaler", 0),
            ("Ipratropium", "Atrovent", "COPD", "20mcg", "Inhaler", 0),

            # ===== PSYCHIATRY =====
            ("Sertraline", "Serlift", "Psychiatry", "50mg", "Tablet", 0),
            ("Clonazepam", "Lonazep", "Anxiety", "0.5mg", "Tablet", 0),
            ("Olanzapine", "Oliza", "Schizophrenia", "5mg", "Tablet", 0),

            # ===== PEDIATRIC HIGH-USE =====
            ("Paracetamol", "Tempol", "Pediatric", "150mg/5ml", "Drops", 1),
            ("Amoxicillin", "Mox Kid", "Pediatric", "250mg/5ml", "Syrup", 1),
            ("Zinc", "Z&D", "Pediatric", "10mg", "Tablet", 1),
            ("ORS", "Rehydralyte", "Pediatric", "Sachet", "Powder", 1),
            ("Ondansetron", "Emeset", "Vomiting", "2mg/5ml", "Syrup", 1),
            ("Albendazole", "Zentel", "Deworming", "200mg", "Chewable", 1),

            # ===== EMERGENCY MEDICINES =====
            ("Adrenaline", "Epinephrine", "Emergency", "1mg/ml", "Injection", 0),
            ("Atropine", "Atropen", "Emergency", "0.6mg/ml", "Injection", 0),
            ("Nitroglycerin", "Sorbitrate", "Emergency", "5mg", "Tablet", 0),
            ("Diazepam", "Valium", "Seizure", "5mg/ml", "Injection", 0),
            ("Hydrocortisone", "Solucortef", "Emergency", "100mg", "Injection", 0),
            ("Magnesium Sulfate", "MgSO4", "Pre-eclampsia", "50%", "Injection", 0),

            # ===== IV FLUIDS / ELECTROLYTES =====
            ("Normal Saline", "NS", "IV Fluid", "100ml", "Infusion", 0),
            ("Normal Saline", "NS", "IV Fluid", "500ml", "Infusion", 0),
            ("Ringer's Lactate", "RL", "IV Fluid", "500ml", "Infusion", 0),
            ("Dextrose Normal Saline", "DNS", "IV Fluid", "500ml", "Infusion", 0),
            ("Dextrose 5%", "D5", "IV Fluid", "500ml", "Infusion", 0),
            ("Potassium Chloride", "KCl", "Electrolyte", "15%", "Injection", 0),
        ]
        
        try:
            for name, company, category, dosage, form, is_pediatric in medicines:
                # Create description from available data
                description = f"{category} medication"
                if is_pediatric:
                    description += " - Pediatric use"
                
                self.cursor.execute("""
                    INSERT OR IGNORE INTO medicines_master 
                    (medicine_name, company_name, category, dosage_mg, dosage_form, description, is_pediatric)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, company, category, dosage, form, description, is_pediatric))
            
            self.conn.commit()
            log_info(f"Successfully populated {len(medicines)} branded medicines into master table")
        except Exception as e:
            log_error("Failed to populate medicines master table", e)
    
    def get_all_medicines_master(self) -> List[Dict]:
        """Get all medicines from master table"""
        try:
            self.cursor.execute("""
                SELECT medicine_name, company_name, dosage_mg, dosage_form, category, description 
                FROM medicines_master 
                ORDER BY medicine_name ASC
            """)
            rows = self.cursor.fetchall()
            medicines = []
            for row in rows:
                # Access Row columns by name - sqlite3.Row supports dictionary-style access
                # Convert None to empty string and ensure all values are strings
                try:
                    medicine = {
                        'medicine_name': str(row['medicine_name']) if row['medicine_name'] is not None else '',
                        'company_name': str(row['company_name']) if row['company_name'] is not None else '',
                        'dosage_mg': str(row['dosage_mg']) if row['dosage_mg'] is not None else '',
                        'dosage_form': str(row['dosage_form']) if row['dosage_form'] is not None else '',
                        'category': str(row['category']) if row['category'] is not None else '',
                        'description': str(row['description']) if row['description'] is not None else ''
                    }
                except (KeyError, IndexError) as e:
                    # Fallback to index-based access if name access fails
                    medicine = {
                        'medicine_name': str(row[0]) if len(row) > 0 and row[0] is not None else '',
                        'company_name': str(row[1]) if len(row) > 1 and row[1] is not None else '',
                        'dosage_mg': str(row[2]) if len(row) > 2 and row[2] is not None else '',
                        'dosage_form': str(row[3]) if len(row) > 3 and row[3] is not None else '',
                        'category': str(row[4]) if len(row) > 4 and row[4] is not None else '',
                        'description': str(row[5]) if len(row) > 5 and row[5] is not None else ''
                    }
                medicines.append(medicine)
            log_debug(f"Retrieved {len(medicines)} medicines from master table")
            return medicines
        except Exception as e:
            log_error("Failed to retrieve medicines from master table", e)
            return []
    
    def search_medicines_master(self, query: str) -> List[Dict]:
        """Search medicines by medicine name only"""
        try:
            self.cursor.execute("""
                SELECT medicine_name, company_name, dosage_mg, dosage_form, category, description 
                FROM medicines_master 
                WHERE medicine_name LIKE ?
                ORDER BY medicine_name ASC
            """, (f'%{query}%',))
            rows = self.cursor.fetchall()
            medicines = []
            for row in rows:
                # Access Row columns by name - sqlite3.Row supports dictionary-style access
                # Convert None to empty string and ensure all values are strings
                try:
                    medicine = {
                        'medicine_name': str(row['medicine_name']) if row['medicine_name'] is not None else '',
                        'company_name': str(row['company_name']) if row['company_name'] is not None else '',
                        'dosage_mg': str(row['dosage_mg']) if row['dosage_mg'] is not None else '',
                        'dosage_form': str(row['dosage_form']) if row['dosage_form'] is not None else '',
                        'category': str(row['category']) if row['category'] is not None else '',
                        'description': str(row['description']) if row['description'] is not None else ''
                    }
                except (KeyError, IndexError) as e:
                    # Fallback to index-based access if name access fails
                    medicine = {
                        'medicine_name': str(row[0]) if len(row) > 0 and row[0] is not None else '',
                        'company_name': str(row[1]) if len(row) > 1 and row[1] is not None else '',
                        'dosage_mg': str(row[2]) if len(row) > 2 and row[2] is not None else '',
                        'dosage_form': str(row[3]) if len(row) > 3 and row[3] is not None else '',
                        'category': str(row[4]) if len(row) > 4 and row[4] is not None else '',
                        'description': str(row[5]) if len(row) > 5 and row[5] is not None else ''
                    }
                medicines.append(medicine)
            return medicines
        except Exception as e:
            log_error("Failed to search medicines", e)
            return []
    
    def get_all_medicines_master_paginated(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get paginated medicines from master table"""
        try:
            self.cursor.execute("""
                SELECT medicine_name, company_name, dosage_mg, dosage_form, category, description 
                FROM medicines_master 
                ORDER BY medicine_name ASC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            rows = self.cursor.fetchall()
            medicines = []
            for row in rows:
                try:
                    medicine = {
                        'medicine_name': str(row['medicine_name']) if row['medicine_name'] is not None else '',
                        'company_name': str(row['company_name']) if row['company_name'] is not None else '',
                        'dosage_mg': str(row['dosage_mg']) if row['dosage_mg'] is not None else '',
                        'dosage_form': str(row['dosage_form']) if row['dosage_form'] is not None else '',
                        'category': str(row['category']) if row['category'] is not None else '',
                        'description': str(row['description']) if row['description'] is not None else ''
                    }
                except (KeyError, IndexError):
                    medicine = {
                        'medicine_name': str(row[0]) if len(row) > 0 and row[0] is not None else '',
                        'company_name': str(row[1]) if len(row) > 1 and row[1] is not None else '',
                        'dosage_mg': str(row[2]) if len(row) > 2 and row[2] is not None else '',
                        'dosage_form': str(row[3]) if len(row) > 3 and row[3] is not None else '',
                        'category': str(row[4]) if len(row) > 4 and row[4] is not None else '',
                        'description': str(row[5]) if len(row) > 5 and row[5] is not None else ''
                    }
                medicines.append(medicine)
            return medicines
        except Exception as e:
            log_error("Failed to retrieve paginated medicines from master table", e)
            return []
    
    def search_medicines_master_paginated(self, query: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Search medicines by medicine name only with pagination"""
        try:
            self.cursor.execute("""
                SELECT medicine_name, company_name, dosage_mg, dosage_form, category, description 
                FROM medicines_master 
                WHERE medicine_name LIKE ?
                ORDER BY medicine_name ASC
                LIMIT ? OFFSET ?
            """, (f'%{query}%', limit, offset))
            rows = self.cursor.fetchall()
            medicines = []
            for row in rows:
                try:
                    medicine = {
                        'medicine_name': str(row['medicine_name']) if row['medicine_name'] is not None else '',
                        'company_name': str(row['company_name']) if row['company_name'] is not None else '',
                        'dosage_mg': str(row['dosage_mg']) if row['dosage_mg'] is not None else '',
                        'dosage_form': str(row['dosage_form']) if row['dosage_form'] is not None else '',
                        'category': str(row['category']) if row['category'] is not None else '',
                        'description': str(row['description']) if row['description'] is not None else ''
                    }
                except (KeyError, IndexError):
                    medicine = {
                        'medicine_name': str(row[0]) if len(row) > 0 and row[0] is not None else '',
                        'company_name': str(row[1]) if len(row) > 1 and row[1] is not None else '',
                        'dosage_mg': str(row[2]) if len(row) > 2 and row[2] is not None else '',
                        'dosage_form': str(row[3]) if len(row) > 3 and row[3] is not None else '',
                        'category': str(row[4]) if len(row) > 4 and row[4] is not None else '',
                        'description': str(row[5]) if len(row) > 5 and row[5] is not None else ''
                    }
                medicines.append(medicine)
            return medicines
        except Exception as e:
            log_error("Failed to search medicines with pagination", e)
            return []
    
    def get_total_medicines_count(self) -> int:
        """Get total count of medicines in master table"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM medicines_master")
            count = self.cursor.fetchone()[0]
            return count if count else 0
        except Exception as e:
            log_error("Failed to get total medicines count", e)
            return 0
    
    def get_search_medicines_count(self, query: str) -> int:
        """Get total count of medicines matching search query"""
        try:
            self.cursor.execute("""
                SELECT COUNT(*) FROM medicines_master 
                WHERE medicine_name LIKE ?
            """, (f'%{query}%',))
            count = self.cursor.fetchone()[0]
            return count if count else 0
        except Exception as e:
            log_error("Failed to get search medicines count", e)
            return 0
    
    def get_medicine_dosages(self, medicine_name: str) -> List[str]:
        """Get all available dosages for a specific medicine"""
        try:
            self.cursor.execute("""
                SELECT DISTINCT dosage_mg FROM medicines_master 
                WHERE medicine_name = ?
                ORDER BY dosage_mg ASC
            """, (medicine_name,))
            dosages = [row[0] for row in self.cursor.fetchall() if row[0]]
            log_debug(f"Retrieved {len(dosages)} dosages for {medicine_name}")
            return dosages
        except Exception as e:
            log_error(f"Failed to retrieve dosages for {medicine_name}", e)
            return []
    
    def get_medicine_by_name_and_dosage(self, medicine_name: str, dosage: str = None) -> Optional[Dict]:
        """Get medicine details by name and optional dosage"""
        try:
            if dosage:
                self.cursor.execute("""
                    SELECT * FROM medicines_master 
                    WHERE medicine_name = ? AND dosage_mg = ?
                    LIMIT 1
                """, (medicine_name, dosage))
            else:
                self.cursor.execute("""
                    SELECT * FROM medicines_master 
                    WHERE medicine_name = ?
                    LIMIT 1
                """, (medicine_name,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            log_error(f"Failed to retrieve medicine {medicine_name}", e)
            return None
    
    def add_medicine_to_master(self, medicine_data: Dict) -> bool:
        """Add a single medicine to the master table"""
        try:
            log_debug(f"Adding medicine to master: {medicine_data.get('medicine_name')}")
            self.cursor.execute("""
                INSERT OR IGNORE INTO medicines_master 
                (medicine_name, company_name, category, dosage_mg, dosage_form, description, is_pediatric)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                medicine_data.get('medicine_name', ''),
                medicine_data.get('company_name', ''),
                medicine_data.get('category', ''),
                medicine_data.get('dosage_mg', ''),
                medicine_data.get('dosage_form', ''),
                medicine_data.get('description', ''),
                medicine_data.get('is_pediatric', 0)
            ))
            self.conn.commit()
            return True
        except Exception as e:
            log_error(f"Failed to add medicine to master: {medicine_data.get('medicine_name')}", e)
            return False
    
    def batch_add_medicines_to_master(self, medicines_list: List[Dict]) -> int:
        """Add multiple medicines to the master table in a single transaction"""
        if not medicines_list:
            return 0
        
        imported = 0
        try:
            for medicine_data in medicines_list:
                self.cursor.execute("""
                    INSERT OR IGNORE INTO medicines_master 
                    (medicine_name, company_name, category, dosage_mg, dosage_form, description, is_pediatric)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    medicine_data.get('medicine_name', ''),
                    medicine_data.get('company_name', ''),
                    medicine_data.get('category', ''),
                    medicine_data.get('dosage_mg', ''),
                    medicine_data.get('dosage_form', ''),
                    medicine_data.get('description', ''),
                    medicine_data.get('is_pediatric', 0)
                ))
                if self.cursor.rowcount > 0:
                    imported += 1
            
            self.conn.commit()
            return imported
        except Exception as e:
            self.conn.rollback()
            log_error(f"Failed to batch add medicines to master", e)
            return 0
    
    def import_medicines_from_csv(self, csv_file_path: str, batch_size: int = 1000) -> Dict:
        """Import medicines from CSV file into medicines_master table"""
        import csv
        import os
        
        if not os.path.exists(csv_file_path):
            log_error(f"CSV file not found: {csv_file_path}")
            return {'success': False, 'message': f'File not found: {csv_file_path}', 'imported': 0, 'failed': 0}
        
        imported = 0
        failed = 0
        skipped = 0
        
        try:
            log_info(f"Starting CSV import from: {csv_file_path}")
            
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                # Detect delimiter with fallback to common delimiters
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                try:
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                    log_info(f"Detected CSV delimiter: '{delimiter}'")
                except Exception:
                    # If sniffer fails, try common delimiters
                    log_info("CSV sniffer failed, trying common delimiters...")
                    common_delimiters = [',', ';', '\t', '|']
                    for delim in common_delimiters:
                        # Count occurrences in first line
                        first_line = sample.split('\n')[0] if '\n' in sample else sample
                        if first_line.count(delim) > 0:
                            delimiter = delim
                            log_info(f"Using delimiter: '{delimiter}'")
                            break
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                # Map CSV columns to database columns (case-insensitive)
                column_mapping = {}
                fieldnames_lower = [col.lower().strip() for col in reader.fieldnames]
                
                for csv_col in reader.fieldnames:
                    csv_col_lower = csv_col.lower().strip()
                    
                    # Medicine name mapping (priority order)
                    if 'medicine_name' not in column_mapping:
                        if csv_col_lower in ['product_name', 'medicine_name', 'drug_name', 'name']:
                            column_mapping['medicine_name'] = csv_col
                        elif 'medicine' in csv_col_lower and 'name' in csv_col_lower:
                            column_mapping['medicine_name'] = csv_col
                        elif 'product' in csv_col_lower and 'name' in csv_col_lower:
                            column_mapping['medicine_name'] = csv_col
                        elif csv_col_lower in ['medicine', 'drug', 'medication']:
                            column_mapping['medicine_name'] = csv_col
                        elif 'name' in csv_col_lower and csv_col_lower not in ['company_name', 'company name']:
                            # Only if we don't have a better match
                            if 'medicine_name' not in column_mapping:
                                column_mapping['medicine_name'] = csv_col
                    
                    # Company name mapping
                    if 'company_name' not in column_mapping:
                        if csv_col_lower in ['product_manufactured', 'manufacturer', 'company_name', 'company', 'maker', 'brand']:
                            column_mapping['company_name'] = csv_col
                        elif 'company' in csv_col_lower and 'name' in csv_col_lower:
                            column_mapping['company_name'] = csv_col
                        elif 'manufactured' in csv_col_lower or 'manufacturer' in csv_col_lower:
                            column_mapping['company_name'] = csv_col
                    
                    # Category mapping
                    if 'category' not in column_mapping:
                        if csv_col_lower in ['sub_category', 'category', 'type', 'class', 'classification', 'drug_category']:
                            column_mapping['category'] = csv_col
                        elif 'category' in csv_col_lower:
                            column_mapping['category'] = csv_col
                    
                    # Dosage mapping (check dosage_mg first, then dosage_form)
                    if csv_col_lower in ['salt_composition', 'dosage', 'dose', 'strength']:
                        if 'dosage_mg' not in column_mapping:
                            column_mapping['dosage_mg'] = csv_col
                    elif 'dosage' in csv_col_lower or 'dose' in csv_col_lower or 'strength' in csv_col_lower:
                        if 'dosage_mg' not in column_mapping and ('mg' in csv_col_lower or 'form' not in csv_col_lower):
                            column_mapping['dosage_mg'] = csv_col
                        elif 'dosage_form' not in column_mapping and 'form' in csv_col_lower:
                            column_mapping['dosage_form'] = csv_col
                    elif 'form' in csv_col_lower and 'dosage_form' not in column_mapping:
                        column_mapping['dosage_form'] = csv_col
                    
                    # Description mapping
                    if 'description' not in column_mapping:
                        if csv_col_lower in ['medicine_desc', 'description', 'desc', 'details', 'notes', 'remarks']:
                            column_mapping['description'] = csv_col
                        elif 'desc' in csv_col_lower:
                            column_mapping['description'] = csv_col
                    
                    # Pediatric mapping
                    if 'is_pediatric' not in column_mapping:
                        if csv_col_lower in ['pediatric', 'paediatric', 'child', 'children', 'is_pediatric', 'pediatric_use']:
                            column_mapping['is_pediatric'] = csv_col
                
                # If medicine_name still not found, use first column as fallback
                if 'medicine_name' not in column_mapping and reader.fieldnames:
                    column_mapping['medicine_name'] = reader.fieldnames[0]
                    log_info(f"Using first column '{reader.fieldnames[0]}' as medicine_name")
                
                log_info(f"Column mapping: {column_mapping}")
                
                batch = []
                for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
                    try:
                        medicine_data = {}
                        
                        # Extract data using column mapping
                        medicine_data['medicine_name'] = row.get(column_mapping.get('medicine_name', reader.fieldnames[0] if reader.fieldnames else ''), '').strip()
                        
                        if not medicine_data['medicine_name']:
                            skipped += 1
                            continue
                        
                        medicine_data['company_name'] = row.get(column_mapping.get('company_name', ''), '').strip() if column_mapping.get('company_name') else ''
                        medicine_data['category'] = row.get(column_mapping.get('category', ''), '').strip() if column_mapping.get('category') else ''
                        medicine_data['dosage_mg'] = row.get(column_mapping.get('dosage_mg', ''), '').strip() if column_mapping.get('dosage_mg') else ''
                        medicine_data['dosage_form'] = row.get(column_mapping.get('dosage_form', ''), '').strip() if column_mapping.get('dosage_form') else ''
                        medicine_data['description'] = row.get(column_mapping.get('description', ''), '').strip() if column_mapping.get('description') else ''
                        
                        # Handle is_pediatric - convert to integer
                        pediatric_val = row.get(column_mapping.get('is_pediatric', ''), '0').strip() if column_mapping.get('is_pediatric') else '0'
                        if pediatric_val.lower() in ['yes', 'true', '1', 'y']:
                            medicine_data['is_pediatric'] = 1
                        else:
                            medicine_data['is_pediatric'] = 0
                        
                        batch.append(medicine_data)
                        
                        if len(batch) >= batch_size:
                            # Insert batch
                            batch_imported = self.batch_add_medicines_to_master(batch)
                            imported += batch_imported
                            failed += (len(batch) - batch_imported)
                            batch = []
                            log_info(f"Processed {row_num} rows. Imported: {imported}, Failed: {failed}, Skipped: {skipped}")
                    
                    except Exception as e:
                        failed += 1
                        log_error(f"Error processing row {row_num}", e)
                        continue
                
                # Insert remaining batch
                if batch:
                    batch_imported = self.batch_add_medicines_to_master(batch)
                    imported += batch_imported
                    failed += (len(batch) - batch_imported)
                    batch = []
            
            log_info(f"CSV import completed. Imported: {imported}, Failed: {failed}, Skipped: {skipped}")
            return {
                'success': True,
                'imported': imported,
                'failed': failed,
                'skipped': skipped,
                'total': imported + failed + skipped
            }
        
        except Exception as e:
            log_error(f"Failed to import medicines from CSV: {csv_file_path}", e)
            return {'success': False, 'message': str(e), 'imported': imported, 'failed': failed}
    
    # User authentication operations
    def create_default_user(self) -> None:
        """Create default user if no users exist"""
        try:
            # Check if any users exist
            self.cursor.execute("SELECT COUNT(*) FROM users")
            count = self.cursor.fetchone()[0]
            
            if count == 0:
                # Create default user: username='admin', password='admin'
                import hashlib
                # Simple password hashing (in production, use bcrypt or similar)
                password_hash = hashlib.sha256('admin'.encode()).hexdigest()
                
                self.cursor.execute("""
                    INSERT INTO users (username, password, full_name, email, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, ('admin', password_hash, 'System Administrator', 'admin@hospital.com', 1))
                
                user_id = self.cursor.lastrowid
                
                # Grant all module permissions to admin user
                all_modules = ['dashboard', 'patient', 'doctor', 'appointments', 'prescription', 'ipd', 'billing', 'report']
                for module in all_modules:
                    self.cursor.execute("""
                        INSERT INTO user_permissions (user_id, module_name)
                        VALUES (?, ?)
                    """, (user_id, module))
                
                self.conn.commit()
                log_info("Default admin user created: username='admin', password='admin' with all permissions")
            else:
                log_debug(f"Users table already has {count} user(s), skipping default user creation")
        except Exception as e:
            log_error("Failed to create default user", e)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with username and password"""
        try:
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            self.cursor.execute("""
                SELECT * FROM users 
                WHERE username = ? AND password = ? AND is_active = 1
            """, (username, password_hash))
            
            row = self.cursor.fetchone()
            if row:
                user = dict(row)
                log_info(f"User authenticated successfully: {username}")
                return user
            else:
                log_warning(f"Authentication failed for username: {username}")
                return None
        except Exception as e:
            log_error(f"Error authenticating user: {username}", e)
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            log_error(f"Error getting user: {username}", e)
            return None
    
    # User permission management operations
    def user_has_permission(self, user_id: int, module_name: str) -> bool:
        """Check if a user has permission to access a specific module"""
        try:
            # Check if user is admin - admin always has all permissions
            self.cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user_row = self.cursor.fetchone()
            if user_row and user_row[0].lower() == 'admin':
                return True
            
            # Check direct user permissions
            self.cursor.execute("""
                SELECT COUNT(*) FROM user_permissions 
                WHERE user_id = ? AND module_name = ?
            """, (user_id, module_name))
            count = self.cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            log_error(f"Failed to check user permission: user_id={user_id}, module={module_name}", e)
            return False
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """Get list of modules that a user has access to"""
        try:
            # Check if user is admin - admin always has all permissions
            self.cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user_row = self.cursor.fetchone()
            if user_row and user_row[0].lower() == 'admin':
                # Admin always has all permissions
                all_modules = ['dashboard', 'patient', 'doctor', 'appointments', 'prescription', 'ipd', 'billing', 'report']
                # Ensure admin has all permissions in database
                current_perms = self.cursor.execute("""
                    SELECT module_name FROM user_permissions 
                    WHERE user_id = ?
                """, (user_id,)).fetchall()
                current_module_names = [row[0] for row in current_perms]
                
                # Add any missing permissions
                for module in all_modules:
                    if module not in current_module_names:
                        self.cursor.execute("""
                            INSERT INTO user_permissions (user_id, module_name)
                            VALUES (?, ?)
                        """, (user_id, module))
                self.conn.commit()
                return all_modules
            
            # Regular user - get their permissions
            self.cursor.execute("""
                SELECT module_name FROM user_permissions 
                WHERE user_id = ?
            """, (user_id,))
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            log_error(f"Failed to get user permissions: {user_id}", e)
            return []
    
    def set_user_permissions(self, user_id: int, permissions: List[str]) -> bool:
        """Set direct module permissions for a user (replaces existing permissions)"""
        try:
            # Prevent changing admin permissions
            self.cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user_row = self.cursor.fetchone()
            if user_row and user_row[0].lower() == 'admin':
                log_warning(f"Attempted to change admin permissions - blocked")
                return False
            
            log_debug(f"Setting direct permissions for user: {user_id}")
            # Delete existing permissions
            self.cursor.execute("DELETE FROM user_permissions WHERE user_id = ?", (user_id,))
            # Add new permissions
            for module in permissions:
                self.cursor.execute("""
                    INSERT INTO user_permissions (user_id, module_name)
                    VALUES (?, ?)
                """, (user_id, module))
            self.conn.commit()
            log_info(f"Direct permissions set successfully for user: {user_id}")
            return True
        except Exception as e:
            log_error(f"Failed to set user permissions: {user_id}", e)
            return False
    
    def get_user_direct_permissions(self, user_id: int) -> List[str]:
        """Get direct module permissions for a user"""
        try:
            self.cursor.execute("""
                SELECT module_name FROM user_permissions 
                WHERE user_id = ?
            """, (user_id,))
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            log_error(f"Failed to get user direct permissions: {user_id}", e)
            return []
    
    def create_user(self, username: str, password: str, full_name: str = '', email: str = '', permissions: List[str] = None) -> Optional[int]:
        """Create a new user with username, password, email, and optional direct permissions"""
        try:
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            log_debug(f"Creating user: {username}")
            
            # First, check if an active user with this username already exists
            self.cursor.execute("SELECT id, is_active FROM users WHERE username = ?", (username,))
            existing_user = self.cursor.fetchone()
            
            if existing_user:
                existing_user_dict = dict(existing_user)
                # If an active user exists, return None (username already taken)
                if existing_user_dict.get('is_active', 0) == 1:
                    log_error(f"Failed to create user (active user already exists): {username}")
                    return None
                # If an inactive user exists, delete it first to allow reuse of username
                else:
                    log_info(f"Inactive user with username '{username}' found. Deleting to allow reuse.")
                    self.cursor.execute("DELETE FROM users WHERE id = ?", (existing_user_dict['id'],))
                    self.conn.commit()
            
            # Now insert the new user
            self.cursor.execute("""
                INSERT INTO users (username, password, full_name, email, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password_hash, full_name, email, 1))
            
            user_id = self.cursor.lastrowid
            
            # Add direct permissions if provided
            if permissions:
                for module in permissions:
                    self.cursor.execute("""
                        INSERT INTO user_permissions (user_id, module_name)
                        VALUES (?, ?)
                    """, (user_id, module))
            
            self.conn.commit()
            log_info(f"User created successfully: {username} (ID: {user_id})")
            return user_id
        except sqlite3.IntegrityError as e:
            log_error(f"Failed to create user (duplicate username): {username}", e)
            return None
        except Exception as e:
            log_error(f"Failed to create user: {username}", e)
            return None
    
    def get_all_users(self) -> List[Dict]:
        """Get all active users with their permissions"""
        try:
            # Only get active users (is_active = 1)
            self.cursor.execute("SELECT * FROM users WHERE is_active = 1 ORDER BY created_at DESC")
            users = []
            for row in self.cursor.fetchall():
                user = dict(row)
                # Get permissions for this user
                self.cursor.execute("""
                    SELECT module_name FROM user_permissions 
                    WHERE user_id = ?
                """, (user['id'],))
                permissions = [row[0] for row in self.cursor.fetchall()]
                user['permissions'] = permissions
                users.append(user)
            return users
        except Exception as e:
            log_error("Failed to get all users", e)
            return []
    
    def update_user(self, user_id: int, username: str = None, full_name: str = None, email: str = None, 
                    password: str = None, is_active: int = None) -> bool:
        """Update user information"""
        try:
            # Prevent updating admin user
            self.cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user_row = self.cursor.fetchone()
            if user_row and user_row[0].lower() == 'admin':
                log_warning(f"Attempted to update admin user - blocked")
                return False
            
            log_debug(f"Updating user: {user_id}")
            updates = []
            params = []
            
            if username is not None:
                updates.append("username = ?")
                params.append(username)
            if full_name is not None:
                updates.append("full_name = ?")
                params.append(full_name)
            if email is not None:
                updates.append("email = ?")
                params.append(email)
            if password is not None:
                import hashlib
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                updates.append("password = ?")
                params.append(password_hash)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(is_active)
            
            if not updates:
                return False
            
            params.append(user_id)
            self.cursor.execute(f"""
                UPDATE users SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            self.conn.commit()
            log_info(f"User updated successfully: {user_id}")
            return True
        except Exception as e:
            log_error(f"Failed to update user: {user_id}", e)
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user (soft delete by setting is_active = 0)"""
        try:
            # Prevent deleting admin user
            self.cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user_row = self.cursor.fetchone()
            if not user_row:
                log_warning(f"User not found: {user_id}")
                return False
            if user_row[0].lower() == 'admin':
                log_warning(f"Attempted to delete admin user - blocked")
                return False
            
            log_debug(f"Deleting user: {user_id}")
            self.cursor.execute("""
                UPDATE users SET is_active = 0
                WHERE id = ?
            """, (user_id,))
            
            # Check if any rows were actually updated
            if self.cursor.rowcount == 0:
                log_warning(f"No rows updated for user: {user_id}")
                return False
            
            self.conn.commit()
            log_info(f"User deleted successfully: {user_id}")
            return True
        except Exception as e:
            log_error(f"Failed to delete user: {user_id}", e)
            self.conn.rollback()
            return False
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID with permissions"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = self.cursor.fetchone()
            if row:
                user = dict(row)
                # Get permissions for this user
                self.cursor.execute("""
                    SELECT module_name FROM user_permissions 
                    WHERE user_id = ?
                """, (user_id,))
                permissions = [row[0] for row in self.cursor.fetchall()]
                user['permissions'] = permissions
                return user
            return None
        except Exception as e:
            log_error(f"Error getting user: {user_id}", e)
            return None

    # ========================================================================
    # Backup & Restore
    # ========================================================================

    def create_local_backup(self, dest_path: str) -> str:
        """Create a copy of the database file at dest_path. Returns dest_path."""
        import shutil
        self.conn.commit()
        self.close()
        try:
            shutil.copy2(self.db_name, dest_path)
            log_info(f"Backup created: {dest_path}")
            return dest_path
        finally:
            self.connect()

    def restore_from_file(self, src_path: str) -> bool:
        """Restore database from a backup file. Replaces current database."""
        import shutil
        if not os.path.isfile(src_path):
            log_error("Restore failed: backup file not found", src_path)
            return False
        self.close()
        try:
            shutil.copy2(src_path, self.db_name)
            log_info(f"Database restored from: {src_path}")
            self.connect()
            return True
        except Exception as e:
            log_error("Restore failed", e)
            self.connect()
            return False
