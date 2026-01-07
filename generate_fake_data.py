"""
Script to generate fake data for Hospital Management System
Generates 50+ records for patients, doctors, appointments, prescriptions, and bills
"""
import random
from datetime import datetime, timedelta
from database import Database
from utils import generate_id
import sys


class FakeDataGenerator:
    """Generate fake data for the hospital management system"""
    
    def __init__(self):
        self.db = Database()
        self.patient_ids = []
        self.doctor_ids = []
        self.appointment_ids = []
        self.prescription_ids = []
        
        # Predefined lists for realistic data
        self.first_names = [
            "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Jessica",
            "William", "Ashley", "James", "Amanda", "Christopher", "Melissa", "Daniel", "Nicole",
            "Matthew", "Michelle", "Anthony", "Kimberly", "Mark", "Amy", "Donald", "Angela",
            "Steven", "Stephanie", "Paul", "Rebecca", "Andrew", "Laura", "Joshua", "Sharon",
            "Kenneth", "Cynthia", "Kevin", "Kathleen", "Brian", "Helen", "George", "Samantha",
            "Edward", "Deborah", "Ronald", "Rachel", "Timothy", "Carolyn", "Jason", "Janet",
            "Jeffrey", "Catherine", "Ryan", "Maria", "Jacob", "Frances", "Gary", "Christine",
            "Nicholas", "Ann", "Eric", "Marie", "Jonathan", "Diane", "Stephen", "Julie",
            "Larry", "Joyce", "Justin", "Victoria", "Scott", "Kelly", "Brandon", "Christina",
            "Benjamin", "Joan", "Samuel", "Evelyn", "Frank", "Judith", "Gregory", "Megan",
            "Raymond", "Cheryl", "Alexander", "Andrea", "Patrick", "Hannah", "Jack", "Jacqueline",
            "Dennis", "Martha", "Jerry", "Gloria", "Tyler", "Teresa", "Aaron", "Sara",
            "Jose", "Janice", "Henry", "Marie", "Adam", "Julia", "Douglas", "Grace",
            "Nathan", "Judy", "Zachary", "Theresa", "Kyle", "Madison", "Noah", "Beverly",
            "Ethan", "Denise", "Jeremy", "Marilyn", "Walter", "Amber", "Christian", "Danielle",
            "Keith", "Brittany", "Roger", "Diana", "Terry", "Abigail", "Gerald", "Jane",
            "Harold", "Lori", "Sean", "Brenda", "Carl", "Pamela", "Arthur", "Emma",
            "Lawrence", "Carol", "Dylan", "Christine", "Jesse", "Samantha", "Jordan", "Debra",
            "Bryan", "Rachel", "Billy", "Cynthia", "Joe", "Kathryn", "Bruce", "Sharon",
            "Gabriel", "Amy", "Logan", "Anna", "Alan", "Lisa", "Juan", "Nancy",
            "Wayne", "Karen", "Roy", "Betty", "Ralph", "Helen", "Randy", "Sandra",
            "Eugene", "Donna", "Vincent", "Carol", "Russell", "Ruth", "Louis", "Sharon",
            "Philip", "Michelle", "Bobby", "Laura", "Johnny", "Emily", "Willie", "Kimberly"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor",
            "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris", "Sanchez",
            "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
            "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams",
            "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
            "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards",
            "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers",
            "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey", "Reed", "Kelly",
            "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson", "Brooks",
            "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
            "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross",
            "Foster", "Jimenez", "Powell", "Jenkins", "Perry", "Russell", "Sullivan", "Bell",
            "Coleman", "Butler", "Henderson", "Barnes", "Gonzales", "Fisher", "Vasquez", "Simmons",
            "Romero", "Jordan", "Patterson", "Alexander", "Hamilton", "Graham", "Reynolds", "Griffin",
            "Wallace", "Moreno", "West", "Cole", "Hayes", "Bryant", "Herrera", "Gibson",
            "Ellis", "Tran", "Medina", "Aguilar", "Stevens", "Murray", "Ford", "Castro",
            "Marshall", "Owens", "Harrison", "Fernandez", "Mcdonald", "Woods", "Washington", "Kennedy",
            "Wells", "Vargas", "Henry", "Chen", "Freeman", "Webb", "Tucker", "Guzman",
            "Burns", "Crawford", "Olson", "Simpson", "Porter", "Hunter", "Gordon", "Mendez",
            "Silva", "Shaw", "Snyder", "Mason", "Dixon", "Munoz", "Hunt", "Hicks",
            "Holmes", "Palmer", "Wagner", "Mills", "Nichols", "Grant", "Knight", "Ferguson",
            "Rose", "Stone", "Hawkins", "Dunn", "Perkins", "Hudson", "Spencer", "Gardner",
            "Stephens", "Payne", "Pierce", "Berry", "Matthews", "Arnold", "Wagner", "Willis",
            "Ray", "Watkins", "Olson", "Carroll", "Duncan", "Duncan", "Duncan", "Duncan"
        ]
        
        self.specializations = [
            "Cardiology", "Dermatology", "Endocrinology", "Gastroenterology", "General Medicine",
            "Neurology", "Oncology", "Orthopedics", "Pediatrics", "Psychiatry",
            "Pulmonology", "Rheumatology", "Urology", "Gynecology", "Ophthalmology",
            "ENT", "Anesthesiology", "Emergency Medicine", "Family Medicine", "Internal Medicine",
            "Nephrology", "Hematology", "Infectious Disease", "Geriatrics", "Sports Medicine",
            "Plastic Surgery", "Vascular Surgery", "Neurosurgery", "Cardiac Surgery", "General Surgery"
        ]
        
        self.qualifications = [
            "MBBS, MD", "MBBS, MS", "MBBS, DM", "MBBS, DNB", "MBBS, MRCP",
            "MBBS, FRCS", "MBBS, PhD", "MBBS, MCh", "MBBS, DMRE", "MBBS, DCH"
        ]
        
        self.blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        
        self.genders = ["Male", "Female", "Other"]
        
        self.allergies = [
            "None", "Penicillin", "Aspirin", "Latex", "Peanuts", "Dust", "Pollen",
            "Shellfish", "Eggs", "Soy", "Wheat", "Dairy", "Sulfa drugs", "Ibuprofen"
        ]
        
        self.diagnoses = [
            "Hypertension", "Diabetes Type 2", "Common Cold", "Upper Respiratory Infection",
            "Gastritis", "Migraine", "Arthritis", "Asthma", "Bronchitis", "Pneumonia",
            "Urinary Tract Infection", "Sinusitis", "Allergic Rhinitis", "Anxiety Disorder",
            "Depression", "Insomnia", "Acid Reflux", "Constipation", "Diarrhea", "Fever",
            "Back Pain", "Joint Pain", "Headache", "Cough", "Sore Throat", "Ear Infection",
            "Skin Rash", "Eczema", "High Cholesterol", "Hypothyroidism", "Hyperthyroidism",
            "Anemia", "Vitamin D Deficiency", "Osteoporosis", "Obesity", "GERD",
            "Irritable Bowel Syndrome", "Chronic Fatigue", "Fibromyalgia", "Tendonitis"
        ]
        
        self.medicines = [
            "Paracetamol", "Ibuprofen", "Amoxicillin", "Azithromycin", "Cetirizine",
            "Omeprazole", "Metformin", "Amlodipine", "Atorvastatin", "Levothyroxine",
            "Salbutamol", "Montelukast", "Pantoprazole", "Domperidone", "Diclofenac",
            "Gabapentin", "Sertraline", "Losartan", "Metoprolol", "Glimepiride"
        ]
        
        self.dosages = ["500mg", "250mg", "100mg", "50mg", "10mg", "5mg", "1 tablet", "2 tablets"]
        
        self.frequencies = ["Once daily", "Twice daily", "Three times daily", "Four times daily",
                           "After meals", "Before meals", "As needed", "Every 6 hours", "Every 8 hours"]
        
        self.durations = ["3 days", "5 days", "7 days", "10 days", "14 days", "1 month", "2 months", "As directed"]
        
        self.payment_methods = ["Cash", "Credit Card", "Debit Card", "Insurance", "Online Payment"]
        
        self.payment_statuses = ["Paid", "Pending", "Partial"]
        
        self.appointment_statuses = ["Scheduled", "Completed", "Cancelled", "No Show"]
        
        self.time_slots = [
            "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30",
            "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"
        ]
        
        self.available_days = [
            "Monday, Wednesday, Friday",
            "Tuesday, Thursday, Saturday",
            "Monday to Friday",
            "Monday, Tuesday, Wednesday",
            "Thursday, Friday, Saturday",
            "Monday, Wednesday, Friday, Saturday"
        ]
        
        self.available_times = [
            "09:00 - 13:00",
            "14:00 - 18:00",
            "09:00 - 17:00",
            "10:00 - 14:00",
            "15:00 - 19:00"
        ]
    
    def generate_phone(self):
        """Generate a random phone number"""
        return f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    def generate_email(self, first_name, last_name):
        """Generate an email address"""
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "example.com"]
        return f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"
    
    def generate_address(self):
        """Generate a random address"""
        streets = ["Main St", "Oak Ave", "Park Rd", "Elm St", "Maple Dr", "Cedar Ln", "Pine St", "First Ave"]
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego"]
        return f"{random.randint(100, 9999)} {random.choice(streets)}, {random.choice(cities)}, {random.choice(['NY', 'CA', 'TX', 'IL', 'AZ', 'PA'])} {random.randint(10000, 99999)}"
    
    def generate_date_of_birth(self, min_age=18, max_age=80):
        """Generate a random date of birth"""
        today = datetime.now()
        age = random.randint(min_age, max_age)
        birth_year = today.year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Use 28 to avoid month-end issues
        return f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
    
    def generate_past_date(self, days_back_min=1, days_back_max=365):
        """Generate a random date in the past"""
        days_back = random.randint(days_back_min, days_back_max)
        date = datetime.now() - timedelta(days=days_back)
        return date.strftime('%Y-%m-%d')
    
    def generate_future_date(self, days_ahead_min=1, days_ahead_max=90):
        """Generate a random date in the future"""
        days_ahead = random.randint(days_ahead_min, days_ahead_max)
        date = datetime.now() + timedelta(days=days_ahead)
        return date.strftime('%Y-%m-%d')
    
    def generate_patients(self, count=60):
        """Generate fake patients"""
        print(f"\nGenerating {count} patients...")
        generated = 0
        
        for i in range(count):
            try:
                first_name = random.choice(self.first_names)
                last_name = random.choice(self.last_names)
                patient_id = generate_id("PAT")
                
                patient_data = {
                    'patient_id': patient_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'date_of_birth': self.generate_date_of_birth(),
                    'gender': random.choice(self.genders),
                    'phone': self.generate_phone(),
                    'email': self.generate_email(first_name, last_name),
                    'address': self.generate_address(),
                    'emergency_contact': f"{random.choice(self.first_names)} {random.choice(self.last_names)}",
                    'emergency_phone': self.generate_phone(),
                    'blood_group': random.choice(self.blood_groups),
                    'allergies': random.choice(self.allergies)
                }
                
                if self.db.add_patient(patient_data):
                    self.patient_ids.append(patient_id)
                    generated += 1
                    if (generated % 10 == 0):
                        print(f"  Generated {generated} patients...")
            except Exception as e:
                print(f"  Error generating patient {i+1}: {e}")
                continue
        
        print(f"[OK] Successfully generated {generated} patients")
        return generated
    
    def generate_doctors(self, count=60):
        """Generate fake doctors"""
        print(f"\nGenerating {count} doctors...")
        generated = 0
        
        for i in range(count):
            try:
                first_name = random.choice(self.first_names)
                last_name = random.choice(self.last_names)
                doctor_id = generate_id("DOC")
                
                doctor_data = {
                    'doctor_id': doctor_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'specialization': random.choice(self.specializations),
                    'qualification': random.choice(self.qualifications),
                    'phone': self.generate_phone(),
                    'email': self.generate_email(first_name, last_name),
                    'address': self.generate_address(),
                    'consultation_fee': round(random.uniform(50, 500), 2),
                    'available_days': random.choice(self.available_days),
                    'available_time': random.choice(self.available_times)
                }
                
                if self.db.add_doctor(doctor_data):
                    self.doctor_ids.append(doctor_id)
                    generated += 1
                    if (generated % 10 == 0):
                        print(f"  Generated {generated} doctors...")
            except Exception as e:
                print(f"  Error generating doctor {i+1}: {e}")
                continue
        
        print(f"[OK] Successfully generated {generated} doctors")
        return generated
    
    def generate_appointments(self, count=60):
        """Generate fake appointments"""
        print(f"\nGenerating {count} appointments...")
        
        if not self.patient_ids or not self.doctor_ids:
            print("  Error: Need patients and doctors first!")
            return 0
        
        generated = 0
        
        for i in range(count):
            try:
                appointment_id = generate_id("APT")
                patient_id = random.choice(self.patient_ids)
                doctor_id = random.choice(self.doctor_ids)
                
                # Mix of past and future appointments
                if random.random() < 0.6:  # 60% past appointments
                    appointment_date = self.generate_past_date(days_back_min=1, days_back_max=180)
                    status = random.choice(["Completed", "Cancelled", "No Show"])
                else:  # 40% future appointments
                    appointment_date = self.generate_future_date(days_ahead_min=1, days_ahead_max=60)
                    status = "Scheduled"
                
                appointment_data = {
                    'appointment_id': appointment_id,
                    'patient_id': patient_id,
                    'doctor_id': doctor_id,
                    'appointment_date': appointment_date,
                    'appointment_time': random.choice(self.time_slots),
                    'status': status,
                    'notes': random.choice([
                        "Regular checkup", "Follow-up visit", "Initial consultation",
                        "Emergency visit", "Routine examination", ""
                    ])
                }
                
                if self.db.add_appointment(appointment_data):
                    self.appointment_ids.append(appointment_id)
                    generated += 1
                    if (generated % 10 == 0):
                        print(f"  Generated {generated} appointments...")
            except Exception as e:
                print(f"  Error generating appointment {i+1}: {e}")
                continue
        
        print(f"[OK] Successfully generated {generated} appointments")
        return generated
    
    def generate_prescriptions(self, count=60):
        """Generate fake prescriptions with items"""
        print(f"\nGenerating {count} prescriptions...")
        
        if not self.patient_ids or not self.doctor_ids:
            print("  Error: Need patients and doctors first!")
            return 0
        
        generated = 0
        
        for i in range(count):
            try:
                prescription_id = generate_id("PRES")
                patient_id = random.choice(self.patient_ids)
                doctor_id = random.choice(self.doctor_ids)
                
                # Some prescriptions linked to appointments, some not
                appointment_id = None
                if self.appointment_ids and random.random() < 0.7:  # 70% linked to appointments
                    appointment_id = random.choice(self.appointment_ids)
                
                prescription_date = self.generate_past_date(days_back_min=1, days_back_max=90)
                
                prescription_data = {
                    'prescription_id': prescription_id,
                    'patient_id': patient_id,
                    'doctor_id': doctor_id,
                    'appointment_id': appointment_id,
                    'prescription_date': prescription_date,
                    'diagnosis': random.choice(self.diagnoses),
                    'notes': random.choice([
                        "Take with food", "Avoid alcohol", "Complete the course",
                        "Monitor blood pressure", "Follow up in 2 weeks", ""
                    ])
                }
                
                # Generate 1-4 prescription items
                num_items = random.randint(1, 4)
                items = []
                for j in range(num_items):
                    item = {
                        'medicine_name': random.choice(self.medicines),
                        'dosage': random.choice(self.dosages),
                        'frequency': random.choice(self.frequencies),
                        'duration': random.choice(self.durations),
                        'instructions': random.choice([
                            "Take after meals", "Take before meals", "Take with plenty of water",
                            "Do not drive after taking", "Take at bedtime", ""
                        ])
                    }
                    items.append(item)
                
                if self.db.add_prescription(prescription_data, items):
                    self.prescription_ids.append(prescription_id)
                    generated += 1
                    if (generated % 10 == 0):
                        print(f"  Generated {generated} prescriptions...")
            except Exception as e:
                print(f"  Error generating prescription {i+1}: {e}")
                continue
        
        print(f"[OK] Successfully generated {generated} prescriptions")
        return generated
    
    def generate_bills(self, count=60):
        """Generate fake bills"""
        print(f"\nGenerating {count} bills...")
        
        if not self.patient_ids:
            print("  Error: Need patients first!")
            return 0
        
        generated = 0
        
        for i in range(count):
            try:
                bill_id = generate_id("BILL")
                patient_id = random.choice(self.patient_ids)
                
                # Some bills linked to appointments, some not
                appointment_id = None
                if self.appointment_ids and random.random() < 0.6:  # 60% linked to appointments
                    appointment_id = random.choice(self.appointment_ids)
                
                bill_date = self.generate_past_date(days_back_min=1, days_back_max=120)
                
                consultation_fee = round(random.uniform(50, 500), 2)
                medicine_cost = round(random.uniform(20, 300), 2)
                other_charges = round(random.uniform(0, 200), 2) if random.random() < 0.4 else 0
                total_amount = round(consultation_fee + medicine_cost + other_charges, 2)
                
                bill_data = {
                    'bill_id': bill_id,
                    'patient_id': patient_id,
                    'appointment_id': appointment_id,
                    'bill_date': bill_date,
                    'consultation_fee': consultation_fee,
                    'medicine_cost': medicine_cost,
                    'other_charges': other_charges,
                    'total_amount': total_amount,
                    'payment_status': random.choice(self.payment_statuses),
                    'payment_method': random.choice(self.payment_methods) if random.random() < 0.7 else "",
                    'notes': random.choice([
                        "Payment received", "Insurance claim pending", "Partial payment",
                        "Payment due", ""
                    ])
                }
                
                if self.db.add_bill(bill_data):
                    generated += 1
                    if (generated % 10 == 0):
                        print(f"  Generated {generated} bills...")
            except Exception as e:
                print(f"  Error generating bill {i+1}: {e}")
                continue
        
        print(f"[OK] Successfully generated {generated} bills")
        return generated
    
    def generate_all(self, patients_count=60, doctors_count=60, appointments_count=60, 
                     prescriptions_count=60, bills_count=60):
        """Generate all fake data"""
        print("=" * 60)
        print("Hospital Management System - Fake Data Generator")
        print("=" * 60)
        
        total_generated = 0
        
        # Generate in order to maintain referential integrity
        total_generated += self.generate_patients(patients_count)
        total_generated += self.generate_doctors(doctors_count)
        total_generated += self.generate_appointments(appointments_count)
        total_generated += self.generate_prescriptions(prescriptions_count)
        total_generated += self.generate_bills(bills_count)
        
        print("\n" + "=" * 60)
        print("Summary:")
        print(f"  Patients: {len(self.patient_ids)}")
        print(f"  Doctors: {len(self.doctor_ids)}")
        print(f"  Appointments: {len(self.appointment_ids)}")
        print(f"  Prescriptions: {len(self.prescription_ids)}")
        print(f"  Bills: {bills_count}")
        print("=" * 60)
        print(f"\n[OK] Fake data generation completed successfully!")
        print(f"  Total records generated: {total_generated}")
        
        self.db.close()


def main():
    """Main entry point"""
    try:
        generator = FakeDataGenerator()
        
        # Generate 60 records for each table (50+ as requested)
        generator.generate_all(
            patients_count=60,
            doctors_count=60,
            appointments_count=60,
            prescriptions_count=60,
            bills_count=60
        )
        
    except KeyboardInterrupt:
        print("\n\nGeneration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

