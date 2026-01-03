"""
Database module for Hospital Management System
Handles all database operations using SQLite
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from logger import log_info, log_error, log_debug, log_database_operation


class Database:
    """Database manager for hospital management system"""
    
    def __init__(self, db_name: str = "hospital.db"):
        """Initialize database connection"""
        self.db_name = db_name
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.init_database()
    
    def connect(self) -> None:
        """Establish database connection"""
        log_info(f"Connecting to database: {self.db_name}")
        self.conn = sqlite3.connect(self.db_name)
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
        
        self.conn.commit()
        log_info("Database initialized successfully")
        
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
    
    # Prescription operations
    def add_prescription(self, prescription_data: Dict, items: List[Dict]) -> bool:
        """Add a new prescription with items"""
        log_debug(f"Adding prescription: {prescription_data.get('prescription_id')}")
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
            log_info(f"Prescription added successfully: {prescription_data['prescription_id']}")
            return True
        except Exception as e:
            log_error(f"Failed to add prescription: {prescription_data.get('prescription_id')}", e)
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
                    prescription_date = ?, diagnosis = ?, notes = ?
                WHERE prescription_id = ?
            """, (
                prescription_data['patient_id'],
                prescription_data['doctor_id'],
                prescription_data.get('appointment_id'),
                prescription_data['prescription_date'],
                prescription_data.get('diagnosis', ''),
                prescription_data.get('notes', ''),
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
                    dosage, frequency, duration, instructions)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    prescription_id,
                    item['medicine_name'],
                    item['dosage'],
                    item['frequency'],
                    item['duration'],
                    item.get('instructions', '')
                ))
            
            self.conn.commit()
            log_info(f"Prescription updated successfully: {prescription_id}")
            return True
        except Exception as e:
            log_error(f"Failed to update prescription: {prescription_id}", e)
            return False
    
    def get_all_medicines(self) -> List[str]:
        """Get all unique medicine names from prescription items"""
        try:
            self.cursor.execute("""
                SELECT DISTINCT medicine_name FROM prescription_items 
                ORDER BY medicine_name ASC
            """)
            medicines = [row[0] for row in self.cursor.fetchall()]
            log_debug(f"Retrieved {len(medicines)} unique medicines from database")
            return medicines
        except Exception as e:
            log_error("Failed to retrieve medicines from database", e)
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
                SELECT * FROM medicines_master 
                ORDER BY medicine_name ASC
            """)
            medicines = [dict(row) for row in self.cursor.fetchall()]
            log_debug(f"Retrieved {len(medicines)} medicines from master table")
            return medicines
        except Exception as e:
            log_error("Failed to retrieve medicines from master table", e)
            return []
    
    def search_medicines_master(self, query: str) -> List[Dict]:
        """Search medicines by name, company, or category"""
        try:
            self.cursor.execute("""
                SELECT * FROM medicines_master 
                WHERE medicine_name LIKE ? OR company_name LIKE ? 
                OR category LIKE ? OR dosage_mg LIKE ?
                ORDER BY medicine_name ASC
            """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            log_error("Failed to search medicines", e)
            return []
    
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

