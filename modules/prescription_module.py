"""
Prescription Management Module
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import generate_id, get_current_date


class PrescriptionModule:
    """Prescription management interface"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        
        self.create_ui()
        # Defer refresh to make UI appear faster
        self.parent.after(10, self.refresh_list)
    
    def create_ui(self):
        """Create user interface"""
        # Header with modern styling
        header = tk.Label(
            self.parent,
            text="Prescription Management",
            font=('Segoe UI', 24, 'bold'),
            bg='#f5f7fa',
            fg='#1a237e'
        )
        header.pack(pady=20)
        
        # Top frame
        top_frame = tk.Frame(self.parent, bg='#f5f7fa')
        top_frame.pack(fill=tk.X, padx=25, pady=15)
        
        # Search by patient
        search_frame = tk.Frame(top_frame, bg='#f5f7fa')
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(search_frame, text="Search by Patient ID:", font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#374151').pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_prescriptions())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 10), width=20, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground='#d1d5db', highlightcolor='#6366f1')
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Add prescription button with modern styling
        add_btn = tk.Button(
            top_frame,
            text="+ New Prescription",
            command=self.add_prescription,
            font=('Segoe UI', 11, 'bold'),
            bg='#10b981',
            fg='white',
            padx=25,
            pady=10,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#059669',
            activeforeground='white'
        )
        add_btn.pack(side=tk.RIGHT, padx=10)
        
        # List frame
        list_frame = tk.Frame(self.parent, bg='#f5f7fa')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)
        
        # Treeview
        columns = ('ID', 'Patient ID', 'Doctor', 'Date', 'Diagnosis')
        
        # Configure style FIRST before creating treeview - use 'clam' theme for better custom styling
        style = ttk.Style()
        try:
            style.theme_use('clam')  # 'clam' theme works well with custom colors
        except:
            pass  # Use default if theme not available
        
        style.configure("Treeview", 
                       font=('Segoe UI', 10), 
                       rowheight=30, 
                       background='white', 
                       foreground='#374151',
                       fieldbackground='white')
        style.configure("Treeview.Heading", 
                       font=('Segoe UI', 11, 'bold'), 
                       background='#6366f1', 
                       foreground='white',
                       relief='flat')
        style.map("Treeview.Heading", 
                 background=[('active', '#4f46e5'), ('pressed', '#4f46e5')])
        style.map("Treeview",
                 background=[('selected', '#6366f1')],
                 foreground=[('selected', 'white')])
        
        # Create treeview AFTER style is configured
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Style scrollbars to match theme
        style.configure("Vertical.TScrollbar", 
                       background='#d1d5db',
                       troughcolor='#f5f7fa',
                       borderwidth=0,
                       arrowcolor='#6366f1',
                       darkcolor='#d1d5db',
                       lightcolor='#d1d5db')
        style.map("Vertical.TScrollbar",
                 background=[('active', '#9ca3af')],
                 arrowcolor=[('active', '#4f46e5')])
        
        style.configure("Horizontal.TScrollbar",
                       background='#9ca3af',
                       troughcolor='#e5e7eb',
                       borderwidth=1,
                       arrowcolor='#6366f1',
                       darkcolor='#9ca3af',
                       lightcolor='#9ca3af',
                       relief=tk.FLAT)
        style.map("Horizontal.TScrollbar",
                 background=[('active', '#6b7280'), ('pressed', '#4b5563')],
                 arrowcolor=[('active', '#4f46e5')])
        
        # Configure column widths based on content
        column_widths = {
            'ID': 150,
            'Patient ID': 150,
            'Doctor': 200,
            'Date': 150,
            'Diagnosis': 250
        }
        
        min_widths = {
            'ID': 120,
            'Patient ID': 120,
            'Doctor': 150,
            'Date': 120,
            'Diagnosis': 180
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = column_widths.get(col, 150)
            minwidth = min_widths.get(col, 100)
            self.tree.column(col, width=width, minwidth=minwidth, stretch=True, anchor='w')
        
        # Add both vertical and horizontal scrollbars with theme styling
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview, style="Vertical.TScrollbar")
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview, style="Horizontal.TScrollbar")
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Use pack layout - pack horizontal scrollbar first at bottom, then treeview and vertical scrollbar
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Pack treeview and vertical scrollbar side by side
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<Double-1>', self.edit_prescription)
        
        # Action buttons
        action_frame = tk.Frame(self.parent, bg='#f0f0f0')
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(
            action_frame,
            text="View Details",
            command=self.view_prescription,
            font=('Segoe UI', 10, 'bold'),
            bg='#3b82f6',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#2563eb',
            activeforeground='white'
        ).pack(side=tk.LEFT, padx=6)
    
    def refresh_list(self):
        """Refresh prescription list"""
        # Clear existing items
        self.tree.delete(*self.tree.get_children())
        
        # Get all prescriptions from database
        try:
            prescriptions = self.db.get_all_prescriptions()
            
            # Add each prescription to the treeview
            for pres in prescriptions:
                # Get doctor name (fallback to doctor_id if name not available)
                doctor_display = pres.get('doctor_name', pres.get('doctor_id', 'Unknown'))
                
                # Truncate diagnosis if too long for display
                diagnosis = pres.get('diagnosis', '')
                if len(diagnosis) > 50:
                    diagnosis = diagnosis[:47] + '...'
                
                self.tree.insert('', tk.END, values=(
                    pres['prescription_id'],
                    pres['patient_id'],
                    doctor_display,
                    pres['prescription_date'],
                    diagnosis
                ))
        except Exception as e:
            # Log error but don't crash
            print(f"Error refreshing prescription list: {e}")
    
    def search_prescriptions(self):
        """Search prescriptions by patient"""
        patient_id = self.search_var.get()
        if not patient_id:
            self.refresh_list()
            return
        
        self.tree.delete(*self.tree.get_children())
        
        prescriptions = self.db.get_prescriptions_by_patient(patient_id)
        for pres in prescriptions:
            self.tree.insert('', tk.END, values=(
                pres['prescription_id'],
                pres['patient_id'],
                pres.get('doctor_name', ''),
                pres['prescription_date'],
                pres.get('diagnosis', '')
            ))
    
    def get_selected_prescription_id(self):
        """Get selected prescription ID"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a prescription")
            return None
        item = self.tree.item(selection[0])
        return item['values'][0]
    
    def add_prescription(self):
        """Open add prescription form in full window"""
        self.show_prescription_form()
    
    def edit_prescription(self, event=None):
        """Open prescription in edit mode"""
        prescription_id = self.get_selected_prescription_id()
        if not prescription_id:
            return
        self.show_prescription_form(prescription_id=prescription_id)
    
    def view_prescription(self, event=None):
        """View prescription details"""
        prescription_id = self.get_selected_prescription_id()
        if not prescription_id:
            return
        
        # Get prescription items
        items = self.db.get_prescription_items(prescription_id)
        if not items:
            messagebox.showinfo("Prescription", "No items found")
            return
        
        # Show prescription details
        details = "Prescription Details:\n\n"
        for item in items:
            details += f"Medicine: {item['medicine_name']}\n"
            details += f"Dosage: {item['dosage']}\n"
            details += f"Frequency: {item['frequency']}\n"
            details += f"Duration: {item['duration']}\n"
            details += f"Instructions: {item.get('instructions', '')}\n\n"
        
        messagebox.showinfo("Prescription Details", details)
    
    def show_prescription_form(self, prescription_id=None):
        """Show prescription form in full window"""
        # If prescription_id is provided, we're editing
        is_editing = prescription_id is not None
        prescription_data = None
        existing_items = []
        
        if is_editing:
            prescription_data = self.db.get_prescription_by_id(prescription_id)
            if not prescription_data:
                messagebox.showerror("Error", "Prescription not found")
                return
            existing_items = self.db.get_prescription_items(prescription_id)
        # Clear existing content
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Create scrollable container
        canvas = tk.Canvas(self.parent, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main content frame
        main_frame = scrollable_frame
        main_frame.configure(bg='#f0f0f0')
        
        # Header with back button
        header_frame = tk.Frame(main_frame, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        if not is_editing:
            prescription_id = generate_id('PRES')
        title_text = f"{'Edit' if is_editing else 'New'} Prescription - ID: {prescription_id}"
        title_label = tk.Label(
            header_frame,
            text=title_text,
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        def back_to_list():
            """Return to prescription list"""
            for widget in self.parent.winfo_children():
                widget.destroy()
            self.create_ui()
            self.parent.after(10, self.refresh_list)
        
        back_btn = tk.Button(
            header_frame,
            text="← Back to List",
            command=back_to_list,
            font=('Arial', 11, 'bold'),
            bg='#34495e',
            fg='white',
            padx=15,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT
        )
        back_btn.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Form container with padding
        form_container = tk.Frame(main_frame, bg='#f0f0f0')
        form_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Two-column layout
        left_column = tk.Frame(form_container, bg='#f0f0f0')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        right_column = tk.Frame(form_container, bg='#f0f0f0')
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0))
        
        # Form fields frame
        form_frame = tk.LabelFrame(left_column, text="Patient & Doctor Information", font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=15, pady=15)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Patient selection with searchable dropdown
        tk.Label(form_frame, text="Patient *:", font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))
        
        # Get all patients for dropdown
        all_patients = self.db.get_all_patients()
        patient_options = []
        patient_id_map = {}
        
        for p in all_patients:
            display_text = f"{p['patient_id']} - {p['first_name']} {p['last_name']}"
            patient_options.append(display_text)
            patient_id_map[display_text] = p['patient_id']
        
        patient_var = tk.StringVar()
        patient_combo = ttk.Combobox(
            form_frame, 
            textvariable=patient_var,
            values=patient_options,
            font=('Arial', 10),
            state='normal'
        )
        patient_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Make combobox searchable
        def filter_patient(*args):
            value = patient_var.get().lower()
            if value == '':
                patient_combo['values'] = patient_options
            else:
                filtered = [opt for opt in patient_options if value in opt.lower()]
                patient_combo['values'] = filtered
        
        patient_var.trace('w', filter_patient)
        
        # Doctor selection with searchable dropdown
        tk.Label(form_frame, text="Doctor *:", font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))
        
        # Get all doctors for dropdown
        all_doctors = self.db.get_all_doctors()
        doctor_options = []
        doctor_id_map = {}
        
        for d in all_doctors:
            display_text = f"{d['doctor_id']} - Dr. {d['first_name']} {d['last_name']} ({d['specialization']})"
            doctor_options.append(display_text)
            doctor_id_map[display_text] = d['doctor_id']
        
        doctor_var = tk.StringVar()
        doctor_combo = ttk.Combobox(
            form_frame,
            textvariable=doctor_var,
            values=doctor_options,
            font=('Arial', 10),
            state='normal'
        )
        doctor_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Make combobox searchable
        def filter_doctor(*args):
            value = doctor_var.get().lower()
            if value == '':
                doctor_combo['values'] = doctor_options
            else:
                filtered = [opt for opt in doctor_options if value in opt.lower()]
                doctor_combo['values'] = filtered
        
        doctor_var.trace('w', filter_doctor)
        
        # Appointment ID (optional)
        tk.Label(form_frame, text="Appointment ID (Optional):", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))
        appointment_var = tk.StringVar()
        appointment_entry = tk.Entry(form_frame, textvariable=appointment_var, font=('Arial', 10))
        appointment_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Date
        tk.Label(form_frame, text="Date:", font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))
        date_entry = tk.Entry(form_frame, font=('Arial', 10))
        date_entry.insert(0, get_current_date())
        date_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Diagnosis
        tk.Label(form_frame, text="Diagnosis:", font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))
        diagnosis_text = tk.Text(form_frame, font=('Arial', 10), height=4, wrap=tk.WORD)
        diagnosis_text.pack(fill=tk.X, pady=(0, 10))
        
        # Additional Notes section
        notes_frame = tk.LabelFrame(right_column, text="Additional Notes", font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=15, pady=15)
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(notes_frame, text="Doctor's Notes:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))
        notes_text = tk.Text(notes_frame, font=('Arial', 10), height=8, wrap=tk.WORD)
        notes_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Populate form fields if editing
        if is_editing and prescription_data:
            # Set patient
            patient_id_to_find = prescription_data.get('patient_id')
            for display_text, pid in patient_id_map.items():
                if pid == patient_id_to_find:
                    patient_var.set(display_text)
                    break
            
            # Set doctor
            doctor_id_to_find = prescription_data.get('doctor_id')
            for display_text, did in doctor_id_map.items():
                if did == doctor_id_to_find:
                    doctor_var.set(display_text)
                    break
            
            # Set appointment
            if prescription_data.get('appointment_id'):
                appointment_var.set(prescription_data['appointment_id'])
            
            # Set date
            date_entry.delete(0, tk.END)
            date_entry.insert(0, prescription_data.get('prescription_date', get_current_date()))
            
            # Set diagnosis
            diagnosis_text.delete('1.0', tk.END)
            diagnosis_text.insert('1.0', prescription_data.get('diagnosis', ''))
            
            # Set notes
            notes_text.delete('1.0', tk.END)
            notes_text.insert('1.0', prescription_data.get('notes', ''))
        
        # Medicines section - spans full width
        medicines_frame = tk.LabelFrame(main_frame, text="Medicines", font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=15, pady=15)
        medicines_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Common medicines list for searchable dropdown
        default_medicines = [
            # Painkillers and Anti-inflammatory
            "Paracetamol", "Ibuprofen", "Aspirin", "Diclofenac", "Naproxen",
            "Ketorolac", "Piroxicam", "Celecoxib", "Etoricoxib", "Meloxicam",
            "Tramadol", "Codeine", "Morphine", "Fentanyl", "Oxycodone",
            "Pregabalin", "Gabapentin", "Carbamazepine",
            
            # Antibiotics
            "Amoxicillin", "Amoxicillin-Clavulanate", "Azithromycin", "Ciprofloxacin",
            "Levofloxacin", "Cephalexin", "Cefuroxime", "Cefixime", "Ceftriaxone",
            "Doxycycline", "Tetracycline", "Minocycline", "Clindamycin",
            "Erythromycin", "Clarithromycin", "Vancomycin", "Metronidazole",
            "Tinidazole", "Nitrofurantoin", "Trimethoprim-Sulfamethoxazole",
            
            # Diabetes Medications
            "Metformin", "Glipizide", "Gliclazide", "Glibenclamide", "Pioglitazone",
            "Sitagliptin", "Vildagliptin", "Saxagliptin", "Linagliptin",
            "Empagliflozin", "Dapagliflozin", "Canagliflozin", "Insulin",
            "Insulin Glargine", "Insulin Lispro", "Insulin Aspart",
            
            # Cardiovascular Medications
            "Amlodipine", "Atenolol", "Metoprolol", "Propranolol", "Bisoprolol",
            "Carvedilol", "Losartan", "Valsartan", "Irbesartan", "Telmisartan",
            "Enalapril", "Lisinopril", "Ramipril", "Captopril", "Furosemide",
            "Hydrochlorothiazide", "Spironolactone", "Amiloride", "Indapamide",
            "Atorvastatin", "Simvastatin", "Rosuvastatin", "Pravastatin",
            "Clopidogrel", "Aspirin", "Warfarin", "Rivaroxaban", "Apixaban",
            "Dabigatran", "Diltiazem", "Verapamil", "Nifedipine", "Nitroglycerin",
            "Isosorbide", "Digoxin", "Amiodarone",
            
            # Gastrointestinal Medications
            "Omeprazole", "Pantoprazole", "Esomeprazole", "Lansoprazole",
            "Rabeprazole", "Ranitidine", "Famotidine", "Cimetidine",
            "Domperidone", "Metoclopramide", "Ondansetron", "Dimenhydrinate",
            "Loperamide", "Bismuth Subsalicylate", "Sucralfate", "Aluminum Hydroxide",
            "Magnesium Hydroxide", "Simethicone", "Lactulose", "Bisacodyl",
            
            # Respiratory Medications
            "Salbutamol", "Ipratropium", "Budesonide", "Fluticasone",
            "Montelukast", "Theophylline", "Aminophylline", "Acetylcysteine",
            "Ambroxol", "Bromhexine", "Guaifenesin",
            
            # Antihistamines and Allergy
            "Cetirizine", "Loratadine", "Fexofenadine", "Desloratadine",
            "Levocetirizine", "Diphenhydramine", "Chlorpheniramine",
            "Hydroxyzine", "Prednisolone", "Methylprednisolone",
            
            # Neurological and Psychiatric
            "Diazepam", "Alprazolam", "Clonazepam", "Lorazepam", "Sertraline",
            "Fluoxetine", "Paroxetine", "Escitalopram", "Citalopram",
            "Amitriptyline", "Imipramine", "Duloxetine", "Venlafaxine",
            "Quetiapine", "Olanzapine", "Risperidone", "Haloperidol",
            "Carbidopa-Levodopa", "Pramipexole", "Ropinirole",
            
            # Thyroid Medications
            "Levothyroxine", "Liothyronine", "Propylthiouracil", "Methimazole",
            "Carbimazole",
            
            # Vitamins and Supplements
            "Calcium Carbonate", "Calcium Citrate", "Vitamin D", "Vitamin D3",
            "Folic Acid", "Iron Sulfate", "Ferrous Fumarate", "Vitamin B12",
            "Vitamin C", "Multivitamin", "Omega-3",
            
            # Antifungal
            "Fluconazole", "Itraconazole", "Ketoconazole", "Clotrimazole",
            "Nystatin", "Terbinafine",
            
            # Antiviral
            "Acyclovir", "Valacyclovir", "Oseltamivir", "Zanamivir",
            
            # Eye Medications
            "Tobramycin Eye Drops", "Ciprofloxacin Eye Drops", "Artificial Tears",
            "Tropicamide", "Atropine Eye Drops",
            
            # Skin Medications
            "Hydrocortisone Cream", "Betamethasone Cream", "Clobetasol Cream",
            "Mupirocin", "Fusidic Acid", "Acyclovir Cream",
            
            # Other Common Medications
            "Allopurinol", "Colchicine", "Probenecid", "Baclofen", "Tizanidine",
            "Tamsulosin", "Finasteride", "Sildenafil", "Tadalafil",
            "Tamsulosin", "Oxytocyn", "Misoprostol", "Mefenamic Acid",
            "Progesterone", "Estradiol", "Alendronate", "Ibandronate"
        ]
        
        # Get all medicines that have been added through prescriptions
        db_medicines = self.db.get_all_medicines()
        
        # Combine default medicines with database medicines, removing duplicates
        common_medicines = list(set(default_medicines + db_medicines))
        common_medicines.sort()  # Sort alphabetically
        
        # Medicines list with remove button
        med_list_frame = tk.Frame(medicines_frame, bg='#f0f0f0')
        med_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        med_columns = ('Medicine', 'Type', 'Dosage', 'Frequency', 'Duration', 'Instructions')
        med_tree = ttk.Treeview(med_list_frame, columns=med_columns, show='headings', height=8)
        
        for col in med_columns:
            med_tree.heading(col, text=col)
            if col == 'Medicine':
                med_tree.column(col, width=180)
            elif col == 'Type':
                med_tree.column(col, width=80, anchor='center')
            elif col == 'Instructions':
                med_tree.column(col, width=180)
            else:
                med_tree.column(col, width=110)
        
        med_scrollbar = ttk.Scrollbar(med_list_frame, orient=tk.VERTICAL, command=med_tree.yview)
        med_tree.configure(yscrollcommand=med_scrollbar.set)
        
        med_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        med_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        medicines = []
        medicine_data_map = {}  # Map tree item to medicine data
        
        def remove_selected_medicine():
            """Remove the currently selected medicine from the list"""
            selection = med_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a medicine to remove")
                return
            
            item = selection[0]
            if item in medicine_data_map:
                medicines.remove(medicine_data_map[item])
                del medicine_data_map[item]
            med_tree.delete(item)
        
        # Add Remove Selected button below the medicine list
        remove_btn_frame = tk.Frame(medicines_frame, bg='#f0f0f0')
        remove_btn_frame.pack(fill=tk.X, pady=(5, 10))
        
        remove_selected_btn = tk.Button(
            remove_btn_frame,
            text="🗑️ Remove Selected Medicine",
            command=remove_selected_medicine,
            font=('Arial', 10, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        remove_selected_btn.pack(side=tk.LEFT, padx=10)
        
        # Add medicine frame
        add_med_frame = tk.LabelFrame(medicines_frame, text="Add New Medicine", font=('Arial', 10, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        add_med_frame.pack(fill=tk.X, pady=10)
        
        # Medicine name with searchable dropdown
        med_name_frame = tk.Frame(add_med_frame, bg='#f0f0f0')
        med_name_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(med_name_frame, text="Medicine Name *:", font=('Arial', 10), bg='#f0f0f0').pack(side=tk.LEFT, padx=(0, 10))
        med_name_var = tk.StringVar()
        med_name_entry = tk.Entry(
            med_name_frame,
            textvariable=med_name_var,
            font=('Arial', 10),
            width=30
        )
        med_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def open_medicine_selector():
            """Open full window medicine selector"""
            medicine_window = tk.Toplevel(self.parent)
            medicine_window.title("Select Medicine")
            medicine_window.geometry("1200x700")
            medicine_window.configure(bg='#f0f0f0')
            medicine_window.transient(self.parent)
            medicine_window.grab_set()
            
            # Header
            header_frame = tk.Frame(medicine_window, bg='#2c3e50', height=60)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            tk.Label(
                header_frame,
                text="Select Medicine",
                font=('Arial', 18, 'bold'),
                bg='#2c3e50',
                fg='white'
            ).pack(side=tk.LEFT, padx=20, pady=15)
            
            # Search frame
            search_frame = tk.Frame(medicine_window, bg='#f0f0f0', padx=20, pady=15)
            search_frame.pack(fill=tk.X)
            
            tk.Label(search_frame, text="Search:", font=('Arial', 11, 'bold'), bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
            search_var = tk.StringVar()
            search_entry = tk.Entry(search_frame, textvariable=search_var, font=('Arial', 11), width=40)
            search_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
            search_entry.focus_set()
            
            # Button frame - pack first to reserve space at bottom
            button_frame = tk.Frame(medicine_window, bg='#f0f0f0', padx=20, pady=15)
            button_frame.pack(fill=tk.X, side=tk.BOTTOM)
            
            # Pagination frame - pack before button frame to reserve space (bright red for debugging, will change)
            pagination_frame = tk.Frame(medicine_window, bg='#2c3e50', relief=tk.RAISED, bd=3, padx=20, pady=15, height=70)
            pagination_frame.pack_propagate(False)
            pagination_frame.pack(fill=tk.X, side=tk.BOTTOM)
            
            # Main content frame with scrollbar - pack after reserving space for pagination/buttons
            content_frame = tk.Frame(medicine_window, bg='#f0f0f0')
            content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 0))
            
            # Treeview with scrollbars
            tree_frame = tk.Frame(content_frame, bg='#f0f0f0')
            tree_frame.pack(fill=tk.BOTH, expand=True)
            
            columns = ('Medicine Name', 'Company', 'Dosage (mg)', 'Form', 'Category', 'Description')
            medicine_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
            
            # Configure the tree column (#0) to be empty and hidden
            medicine_tree.column('#0', width=0, stretch=False)
            
            # Configure columns
            medicine_tree.heading('Medicine Name', text='Medicine Name')
            medicine_tree.heading('Company', text='Company Name')
            medicine_tree.heading('Dosage (mg)', text='Dosage')
            medicine_tree.heading('Form', text='Form')
            medicine_tree.heading('Category', text='Category')
            medicine_tree.heading('Description', text='Description')
            
            medicine_tree.column('Medicine Name', width=200, anchor='w', stretch=True)
            medicine_tree.column('Company', width=150, anchor='w', stretch=True)
            medicine_tree.column('Dosage (mg)', width=120, anchor='w', stretch=True)
            medicine_tree.column('Form', width=100, anchor='w', stretch=True)
            medicine_tree.column('Category', width=120, anchor='w', stretch=True)
            medicine_tree.column('Description', width=300, anchor='w', stretch=True)
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=medicine_tree.yview)
            h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=medicine_tree.xview)
            medicine_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            medicine_tree.grid(row=0, column=0, sticky='nsew')
            v_scrollbar.grid(row=0, column=1, sticky='ns')
            h_scrollbar.grid(row=1, column=0, sticky='ew')
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)
            
            # Pagination settings
            items_per_page = 50
            current_page = 1
            current_search_query = ""
            total_items = 0
            
            # Left side - Previous button
            prev_btn = tk.Button(
                pagination_frame,
                text="< Prev",
                font=('Arial', 11, 'bold'),
                bg='#3498db',
                fg='white',
                width=8,
                padx=15,
                pady=10,
                cursor='hand2',
                relief=tk.RAISED,
                bd=2,
                state=tk.DISABLED,
                activebackground='#2980b9',
                activeforeground='white',
                disabledforeground='#bdc3c7'
            )
            prev_btn.pack(side=tk.LEFT, padx=(20, 10), pady=10)
            
            # Center - Page number display
            page_info_label = tk.Label(
                pagination_frame,
                text="Page 1 of 1",
                font=('Arial', 12, 'bold'),
                bg='#2c3e50',
                fg='white',
                padx=30
            )
            page_info_label.pack(side=tk.LEFT, padx=20, pady=10, expand=True)
            
            # Right side - Next button
            next_btn = tk.Button(
                pagination_frame,
                text="Next >",
                font=('Arial', 11, 'bold'),
                bg='#3498db',
                fg='white',
                width=8,
                padx=15,
                pady=10,
                cursor='hand2',
                relief=tk.RAISED,
                bd=2,
                state=tk.DISABLED,
                activebackground='#2980b9',
                activeforeground='white',
                disabledforeground='#bdc3c7'
            )
            next_btn.pack(side=tk.LEFT, padx=(10, 20), pady=10)
            
            def populate_tree(medicines_list):
                """Populate tree with medicines - displays all available data"""
                medicine_tree.delete(*medicine_tree.get_children())
                for med in medicines_list:
                    # Get all values from the medicine dictionary
                    # The database method returns all fields, so we extract them directly
                    medicine_name = str(med.get('medicine_name', '') or '')
                    company_name = str(med.get('company_name', '') or '')
                    dosage_mg = str(med.get('dosage_mg', '') or '')
                    dosage_form = str(med.get('dosage_form', '') or '')
                    category = str(med.get('category', '') or '')
                    description = str(med.get('description', '') or '')
                    
                    # Insert values in the exact order matching the columns tuple
                    # Column order: ('Medicine Name', 'Company', 'Dosage (mg)', 'Form', 'Category', 'Description')
                    # When using show='headings', text='' ensures values map to columns correctly
                    item_id = medicine_tree.insert('', tk.END, text='', values=(
                        medicine_name,      # Maps to 'Medicine Name' column
                        company_name,      # Maps to 'Company' column
                        dosage_mg,         # Maps to 'Dosage (mg)' column
                        dosage_form,       # Maps to 'Form' column
                        category,          # Maps to 'Category' column
                        description        # Maps to 'Description' column
                    ))
            
            def load_page(page_num, search_query=""):
                """Load a specific page of medicines"""
                try:
                    nonlocal current_page, current_search_query, total_items
                    current_page = page_num
                    current_search_query = search_query
                    
                    offset = (page_num - 1) * items_per_page
                    
                    if search_query:
                        medicines = self.db.search_medicines_master_paginated(search_query, items_per_page, offset)
                        total_items = self.db.get_search_medicines_count(search_query)
                    else:
                        medicines = self.db.get_all_medicines_master_paginated(items_per_page, offset)
                        total_items = self.db.get_total_medicines_count()
                    
                    populate_tree(medicines)
                    
                    # Update pagination controls
                    total_pages = (total_items + items_per_page - 1) // items_per_page if total_items > 0 else 1
                    
                    if total_pages > 0:
                        page_info_label.config(text=f"Page {current_page} of {total_pages}")
                    else:
                        page_info_label.config(text="No medicines found")
                    
                    # Enable/disable navigation buttons
                    prev_btn.config(state=tk.NORMAL if current_page > 1 else tk.DISABLED)
                    next_btn.config(state=tk.NORMAL if current_page < total_pages else tk.DISABLED)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load medicines: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            def go_to_previous_page():
                """Go to previous page"""
                if current_page > 1:
                    load_page(current_page - 1, current_search_query)
            
            def go_to_next_page():
                """Go to next page"""
                total_pages = (total_items + items_per_page - 1) // items_per_page if total_items > 0 else 1
                if current_page < total_pages:
                    load_page(current_page + 1, current_search_query)
            
            prev_btn.config(command=go_to_previous_page)
            next_btn.config(command=go_to_next_page)
            
            # Load first page
            load_page(1, "")
            
            # Search functionality
            def on_search(*args):
                query = search_var.get().strip()
                # Reset to first page when searching
                load_page(1, query)
            
            search_var.trace('w', on_search)
            search_entry.bind('<Return>', lambda e: on_search())
            
            # Double-click to select
            selected_medicine = {'name': None, 'dosage': None}
            
            def on_double_click(event):
                selection = medicine_tree.selection()
                if selection:
                    item = medicine_tree.item(selection[0])
                    values = item['values']
                    if values:
                        selected_medicine['name'] = values[0]
                        selected_medicine['dosage'] = values[2] if len(values) > 2 else None
                        med_name_var.set(values[0])
                        # Update dosage options and set selected dosage if available
                        update_dosage_options(values[0])
                        if selected_medicine['dosage']:
                            # If dosage contains comma, don't set it (let user select from dropdown)
                            dosage_value = str(selected_medicine['dosage']).strip()
                            if ',' not in dosage_value:
                                dosage_var.set(dosage_value)
                            # If comma-separated, leave empty so user can select from dropdown
                        medicine_window.destroy()
            
            medicine_tree.bind('<Double-1>', on_double_click)
            
            def select_medicine():
                selection = medicine_tree.selection()
                if selection:
                    item = medicine_tree.item(selection[0])
                    values = item['values']
                    if values:
                        selected_medicine['name'] = values[0]
                        selected_medicine['dosage'] = values[2] if len(values) > 2 else None
                        med_name_var.set(values[0])
                        # Update dosage options and set selected dosage if available
                        update_dosage_options(values[0])
                        if selected_medicine['dosage']:
                            # If dosage contains comma, don't set it (let user select from dropdown)
                            dosage_value = str(selected_medicine['dosage']).strip()
                            if ',' not in dosage_value:
                                dosage_var.set(dosage_value)
                            # If comma-separated, leave empty so user can select from dropdown
                        medicine_window.destroy()
                else:
                    messagebox.showwarning("Warning", "Please select a medicine")
            
            def cancel_selection():
                medicine_window.destroy()
            
            select_btn = tk.Button(
                button_frame,
                text="Select Medicine",
                command=select_medicine,
                font=('Arial', 11, 'bold'),
                bg='#27ae60',
                fg='white',
                padx=20,
                pady=8,
                cursor='hand2'
            )
            select_btn.pack(side=tk.LEFT, padx=5)
            
            cancel_btn = tk.Button(
                button_frame,
                text="Cancel",
                command=cancel_selection,
                font=('Arial', 11),
                bg='#95a5a6',
                fg='white',
                padx=20,
                pady=8,
                cursor='hand2'
            )
            cancel_btn.pack(side=tk.LEFT, padx=5)
            
            # Bind Enter key to select
            medicine_tree.bind('<Return>', lambda e: select_medicine())
            search_entry.bind('<Return>', lambda e: medicine_tree.focus_set())
            
        # Button to open medicine selector
        select_med_btn = tk.Button(
            med_name_frame,
            text="🔍 Browse Medicines",
            command=open_medicine_selector,
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            padx=10,
            pady=5,
            cursor='hand2'
        )
        select_med_btn.pack(side=tk.LEFT, padx=5)
        
        # Medicine details in a grid
        details_frame = tk.Frame(add_med_frame, bg='#f0f0f0')
        details_frame.pack(fill=tk.X, pady=5)
        
        # Default dosage options (fallback)
        default_dosage_options = [
            "25mg", "50mg", "75mg", "100mg", "125mg", "150mg", "200mg", "250mg",
            "300mg", "400mg", "500mg", "600mg", "625mg", "750mg", "800mg", "1000mg",
            "10mcg", "25mcg", "50mcg", "75mcg", "100mcg", "200mcg",
            "1ml", "2ml", "3ml", "5ml", "10ml",
            "100 units", "200 units", "300 units", "400 units",
            "1%", "2%", "5%", "10%",
            "5mg/ml", "10mg/ml", "20mg/ml", "50mg/ml",
            "100 IU", "500 IU", "1000 IU", "2000 IU"
        ]
        
        # Current dosage options (will be updated based on medicine selection)
        dosage_options = default_dosage_options.copy()
        
        tk.Label(details_frame, text="Dosage *:", font=('Arial', 10), bg='#f0f0f0').grid(row=0, column=0, sticky='w', padx=(0, 5), pady=5)
        dosage_var = tk.StringVar()
        dosage_combo = ttk.Combobox(details_frame, textvariable=dosage_var, values=dosage_options, font=('Arial', 10), width=18, state='normal')
        dosage_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        def update_dosage_options(medicine_name: str):
            """Update dosage options based on selected medicine"""
            if medicine_name and medicine_name.strip():
                # Get dosages for this medicine from database
                med_dosages = self.db.get_medicine_dosages(medicine_name.strip())
                if med_dosages:
                    # Split any comma-separated dosages and flatten the list
                    all_dosages = []
                    for dosage in med_dosages:
                        if dosage:
                            # Split by comma and strip whitespace
                            split_dosages = [d.strip() for d in str(dosage).split(',') if d.strip()]
                            all_dosages.extend(split_dosages)
                    
                    # Remove duplicates while preserving order
                    unique_dosages = []
                    seen = set()
                    for dosage in all_dosages:
                        if dosage not in seen:
                            unique_dosages.append(dosage)
                            seen.add(dosage)
                    
                    if unique_dosages:
                        # Update dosage combo with medicine-specific dosages
                        dosage_combo['values'] = unique_dosages
                        # Auto-select first dosage if available and no dosage is currently selected
                        if not dosage_var.get():
                            dosage_var.set(unique_dosages[0])
                    else:
                        # No valid dosages found, use default options
                        dosage_combo['values'] = default_dosage_options
                else:
                    # No specific dosages found, use default options
                    dosage_combo['values'] = default_dosage_options
            else:
                # No medicine selected, use default options
                dosage_combo['values'] = default_dosage_options
        
        # Make dosage searchable
        def filter_dosage(*args):
            value = dosage_var.get().lower()
            current_options = dosage_combo['values']
            if value == '':
                # Restore options based on medicine
                med_name = med_name_var.get().strip()
                if med_name:
                    update_dosage_options(med_name)
                else:
                    dosage_combo['values'] = default_dosage_options
            else:
                filtered = [opt for opt in current_options if value in opt.lower()]
                dosage_combo['values'] = filtered
        
        dosage_var.trace('w', filter_dosage)
        
        # Update dosage when medicine name changes
        def on_medicine_changed(*args):
            medicine_name = med_name_var.get()
            if medicine_name:
                update_dosage_options(medicine_name)
            else:
                dosage_combo['values'] = default_dosage_options
                dosage_var.set('')
        
        med_name_var.trace('w', on_medicine_changed)
        
        # Frequency options
        frequency_options = [
            "Once daily", "Twice daily", "Three times daily", "Four times daily",
            "Once in morning", "Once in evening", "Once at night",
            "Every 4 hours", "Every 6 hours", "Every 8 hours", "Every 12 hours",
            "As needed", "Before meals", "After meals", "With meals",
            "Before bedtime", "As directed", "When required",
            "Once weekly", "Twice weekly", "Three times weekly",
            "Every other day", "Alternate days",
            "1x/day", "2x/day", "3x/day", "4x/day"
        ]
        
        tk.Label(details_frame, text="Frequency *:", font=('Arial', 10), bg='#f0f0f0').grid(row=0, column=2, sticky='w', padx=(10, 5), pady=5)
        frequency_var = tk.StringVar()
        frequency_combo = ttk.Combobox(details_frame, textvariable=frequency_var, values=frequency_options, font=('Arial', 10), width=18, state='normal')
        frequency_combo.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        
        # Make frequency searchable
        def filter_frequency(*args):
            value = frequency_var.get().lower()
            if value == '':
                frequency_combo['values'] = frequency_options
            else:
                filtered = [opt for opt in frequency_options if value in opt.lower()]
                frequency_combo['values'] = filtered
        
        frequency_var.trace('w', filter_frequency)
        
        # Duration options
        duration_options = [
            "1 day", "2 days", "3 days", "4 days", "5 days", "6 days", "7 days",
            "10 days", "14 days", "15 days", "21 days",
            "1 week", "2 weeks", "3 weeks", "4 weeks",
            "1 month", "2 months", "3 months", "6 months",
            "Until finished", "As needed", "As directed",
            "For 5 days", "For 7 days", "For 10 days", "For 14 days"
        ]
        
        tk.Label(details_frame, text="Duration *:", font=('Arial', 10), bg='#f0f0f0').grid(row=1, column=0, sticky='w', padx=(0, 5), pady=5)
        duration_var = tk.StringVar()
        duration_combo = ttk.Combobox(details_frame, textvariable=duration_var, values=duration_options, font=('Arial', 10), width=18, state='normal')
        duration_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # Make duration searchable
        def filter_duration(*args):
            value = duration_var.get().lower()
            if value == '':
                duration_combo['values'] = duration_options
            else:
                filtered = [opt for opt in duration_options if value in opt.lower()]
                duration_combo['values'] = filtered
        
        duration_var.trace('w', filter_duration)
        
        tk.Label(details_frame, text="Instructions:", font=('Arial', 10), bg='#f0f0f0').grid(row=1, column=2, sticky='w', padx=(10, 5), pady=5)
        instructions_entry = tk.Entry(details_frame, font=('Arial', 10), width=18)
        instructions_entry.grid(row=1, column=3, padx=5, pady=5, sticky='ew')
        
        details_frame.grid_columnconfigure(1, weight=1)
        details_frame.grid_columnconfigure(3, weight=1)
        
        def add_medicine():
            med_name = med_name_var.get().strip()
            dosage = dosage_var.get().strip()
            frequency = frequency_var.get().strip()
            duration = duration_var.get().strip()
            instructions = instructions_entry.get().strip()
            
            if not med_name:
                messagebox.showwarning("Warning", "Please enter medicine name")
                med_name_entry.focus_set()
                return
            
            if not dosage:
                messagebox.showwarning("Warning", "Please enter dosage")
                dosage_combo.focus_set()
                return
            
            if not frequency:
                messagebox.showwarning("Warning", "Please enter frequency")
                frequency_combo.focus_set()
                return
            
            if not duration:
                messagebox.showwarning("Warning", "Please enter duration")
                duration_combo.focus_set()
                return
            
            # Get medicine form/type from database
            medicine_info = self.db.get_medicine_by_name_and_dosage(med_name, dosage)
            medicine_type = 'Other'
            if medicine_info and medicine_info.get('dosage_form'):
                form = medicine_info['dosage_form']
                # Normalize common forms
                form_lower = form.lower()
                if 'tablet' in form_lower:
                    medicine_type = 'Tablet'
                elif 'syrup' in form_lower or 'suspension' in form_lower:
                    medicine_type = 'Syrup'
                elif 'capsule' in form_lower:
                    medicine_type = 'Capsule'
                elif 'injection' in form_lower or 'inject' in form_lower:
                    medicine_type = 'Injection'
                elif 'cream' in form_lower or 'ointment' in form_lower:
                    medicine_type = 'Cream'
                elif 'drops' in form_lower or 'drop' in form_lower:
                    medicine_type = 'Drops'
                elif 'inhaler' in form_lower:
                    medicine_type = 'Inhaler'
                else:
                    medicine_type = form  # Use the form as-is if not recognized
            
            # Add to tree (Medicine, Type, Dosage, Frequency, Duration, Instructions)
            item = med_tree.insert('', tk.END, values=(med_name, medicine_type, dosage, frequency, duration, instructions))
            medicine_data = {
                'medicine_name': med_name,
                'dosage': dosage,
                'frequency': frequency,
                'duration': duration,
                'instructions': instructions,
                'type': medicine_type
            }
            medicines.append(medicine_data)
            medicine_data_map[item] = medicine_data
            
            # Clear fields
            med_name_var.set('')
            dosage_var.set('')
            frequency_var.set('')
            duration_var.set('')
            instructions_entry.delete(0, tk.END)
            
            # Set focus back to medicine name
            med_name_entry.focus_set()
        
        # Add Medicine button
        add_med_btn = tk.Button(
            add_med_frame,
            text="+ Add Medicine",
            command=add_medicine,
            font=('Arial', 11, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        add_med_btn.pack(pady=10)
        
        # Bind Enter key to add medicine
        def on_med_enter(event):
            add_medicine()
            return "break"
        
        med_name_entry.bind('<Return>', on_med_enter)
        dosage_combo.bind('<Return>', on_med_enter)
        frequency_combo.bind('<Return>', on_med_enter)
        duration_combo.bind('<Return>', on_med_enter)
        instructions_entry.bind('<Return>', on_med_enter)
        
        # Populate existing medicines if editing
        if is_editing and existing_items:
            for item in existing_items:
                med_name = item.get('medicine_name', '')
                dosage = item.get('dosage', '')
                frequency = item.get('frequency', '')
                duration = item.get('duration', '')
                instructions = item.get('instructions', '')
                
                # Get medicine form/type from database
                medicine_info = self.db.get_medicine_by_name_and_dosage(med_name, dosage)
                medicine_type = 'Other'
                if medicine_info and medicine_info.get('dosage_form'):
                    form = medicine_info['dosage_form']
                    form_lower = form.lower()
                    if 'tablet' in form_lower:
                        medicine_type = 'Tablet'
                    elif 'syrup' in form_lower or 'suspension' in form_lower:
                        medicine_type = 'Syrup'
                    elif 'capsule' in form_lower:
                        medicine_type = 'Capsule'
                    elif 'injection' in form_lower or 'inject' in form_lower:
                        medicine_type = 'Injection'
                    elif 'cream' in form_lower or 'ointment' in form_lower:
                        medicine_type = 'Cream'
                    elif 'drops' in form_lower or 'drop' in form_lower:
                        medicine_type = 'Drops'
                    elif 'inhaler' in form_lower:
                        medicine_type = 'Inhaler'
                    else:
                        medicine_type = form
                
                # Add to tree
                tree_item = med_tree.insert('', tk.END, values=(med_name, medicine_type, dosage, frequency, duration, instructions))
                medicine_data = {
                    'medicine_name': med_name,
                    'dosage': dosage,
                    'frequency': frequency,
                    'duration': duration,
                    'instructions': instructions,
                    'type': medicine_type
                }
                medicines.append(medicine_data)
                medicine_data_map[tree_item] = medicine_data
        
        # Save and Cancel buttons at bottom
        button_frame = tk.Frame(main_frame, bg='#f0f0f0', relief=tk.RAISED, bd=2)
        button_frame.pack(fill=tk.X, padx=30, pady=20)
        
        inner_button_frame = tk.Frame(button_frame, bg='#f0f0f0')
        inner_button_frame.pack(padx=20, pady=15)
        
        def save_prescription():
            # Get selected patient ID
            patient_display = patient_var.get()
            patient_id = None
            if patient_display in patient_id_map:
                patient_id = patient_id_map[patient_display]
            else:
                parts = patient_display.split(' - ')
                if parts and parts[0].startswith('PAT-'):
                    patient_id = parts[0]
            
            # Get selected doctor ID
            doctor_display = doctor_var.get()
            doctor_id = None
            if doctor_display in doctor_id_map:
                doctor_id = doctor_id_map[doctor_display]
            else:
                parts = doctor_display.split(' - ')
                if parts and parts[0].startswith('DOC-'):
                    doctor_id = parts[0]
            
            if not patient_id:
                messagebox.showerror("Error", "Please select a valid patient")
                patient_combo.focus_set()
                return
            
            if not doctor_id:
                messagebox.showerror("Error", "Please select a valid doctor")
                doctor_combo.focus_set()
                return
            
            if not medicines:
                messagebox.showerror("Error", "Please add at least one medicine")
                return
            
            appointment_id = appointment_var.get().strip() or None
            
            data = {
                'patient_id': patient_id,
                'doctor_id': doctor_id,
                'appointment_id': appointment_id,
                'prescription_date': date_entry.get() or get_current_date(),
                'diagnosis': diagnosis_text.get('1.0', tk.END).strip(),
                'notes': notes_text.get('1.0', tk.END).strip()
            }
            
            if is_editing:
                # Update existing prescription
                if self.db.update_prescription(prescription_id, data, medicines):
                    messagebox.showinfo("Success", "Prescription updated successfully")
                    back_to_list()
                    self.parent.after(100, self.refresh_list)
                else:
                    messagebox.showerror("Error", "Failed to update prescription")
            else:
                # Create new prescription
                data['prescription_id'] = prescription_id
                if self.db.add_prescription(data, medicines):
                    messagebox.showinfo("Success", "Prescription created successfully")
                    back_to_list()
                    self.parent.after(100, self.refresh_list)
                else:
                    messagebox.showerror("Error", "Failed to create prescription")
        
        save_btn = tk.Button(
            inner_button_frame,
            text="💾 Save Prescription",
            command=save_prescription,
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=30,
            pady=10,
            cursor='hand2',
            relief=tk.RAISED,
            bd=3
        )
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(
            inner_button_frame,
            text="Cancel",
            command=back_to_list,
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            padx=30,
            pady=10,
            cursor='hand2'
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # Set focus on patient combo when form opens
        self.parent.after(100, lambda: patient_combo.focus_set())
        
        # Update canvas scroll region when content changes
        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind('<Configure>', update_scroll_region)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            # Windows uses delta, Linux uses num
            if event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                canvas.yview_scroll(1, "units")
        
        # Bind mouse wheel events
        canvas.bind("<MouseWheel>", on_mousewheel)
        canvas.bind("<Button-4>", on_mousewheel)  # Linux
        canvas.bind("<Button-5>", on_mousewheel)  # Linux

