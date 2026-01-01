"""
Prescription Management Module
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database
from utils import generate_id, get_current_date
import tempfile
import os
import subprocess
import platform


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
        # Header
        header = tk.Label(
            self.parent,
            text="Prescription Management",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        header.pack(pady=10)
        
        # Top frame
        top_frame = tk.Frame(self.parent, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Search by patient
        search_frame = tk.Frame(top_frame, bg='#f0f0f0')
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(search_frame, text="Search by Patient ID:", font=('Arial', 10), bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_prescriptions())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Arial', 10), width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Add prescription button
        add_btn = tk.Button(
            top_frame,
            text="+ New Prescription",
            command=self.add_prescription,
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        add_btn.pack(side=tk.RIGHT, padx=10)
        
        # List frame
        list_frame = tk.Frame(self.parent, bg='#f0f0f0')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ('ID', 'Patient ID', 'Doctor', 'Date', 'Diagnosis')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure style for better visibility
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 10), rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<Double-1>', self.view_prescription)
        
        # Action buttons
        action_frame = tk.Frame(self.parent, bg='#f0f0f0')
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(
            action_frame,
            text="View Details",
            command=self.view_prescription,
            font=('Arial', 10),
            bg='#3498db',
            fg='black',
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="✏️ Edit",
            command=self.edit_prescription,
            font=('Arial', 10),
            bg='#9b59b6',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="🖨️ Print",
            command=self.print_prescription,
            font=('Arial', 10),
            bg='#e67e22',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
    
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
        """Open add prescription dialog"""
        self.prescription_dialog()
    
    def edit_prescription(self):
        """Open edit prescription dialog"""
        prescription_id = self.get_selected_prescription_id()
        if not prescription_id:
            messagebox.showwarning("Warning", "Please select a prescription to edit")
            return
        self.prescription_dialog(prescription_id=prescription_id)
    
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
    
    def print_prescription(self):
        """Print prescription"""
        prescription_id = self.get_selected_prescription_id()
        if not prescription_id:
            return
        
        # Get prescription details
        prescription = self.db.get_prescription_by_id(prescription_id)
        if not prescription:
            messagebox.showerror("Error", "Prescription not found")
            return
        
        # Get prescription items
        items = self.db.get_prescription_items(prescription_id)
        if not items:
            messagebox.showinfo("Prescription", "No items found")
            return
        
        # Get patient details
        patient = self.db.get_patient_by_id(prescription['patient_id'])
        patient_name = f"{patient['first_name']} {patient['last_name']}" if patient else prescription['patient_id']
        
        # Format prescription for printing
        print_text = f"""
╔══════════════════════════════════════════════════════════════╗
║                  PRESCRIPTION                                ║
╚══════════════════════════════════════════════════════════════╝

Prescription ID: {prescription['prescription_id']}
Date: {prescription['prescription_date']}

Patient Information:
  Name: {patient_name}
  Patient ID: {prescription['patient_id']}
"""
        if patient:
            if patient.get('date_of_birth'):
                print_text += f"  Date of Birth: {patient['date_of_birth']}\n"
            if patient.get('gender'):
                print_text += f"  Gender: {patient['gender']}\n"
        
        print_text += f"""
Doctor: {prescription.get('doctor_name', prescription.get('doctor_id', 'N/A'))}
"""
        
        if prescription.get('chief_complaints'):
            print_text += f"""
Chief Complaints / Symptoms:
{prescription['chief_complaints']}
"""
        
        if prescription.get('examination'):
            print_text += f"""
Examination / Vitals:
{prescription['examination']}
"""
        
        print_text += f"""
Diagnosis:
{prescription.get('diagnosis', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MEDICINES PRESCRIBED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for idx, item in enumerate(items, 1):
            print_text += f"""
{idx}. {item['medicine_name']}
   Dosage: {item['dosage']}
   Frequency: {item['frequency']}
   Duration: {item['duration']}"""
            if item.get('instructions'):
                print_text += f"\n   Instructions: {item['instructions']}"
            print_text += "\n"
        
        if prescription.get('notes'):
            print_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Notes / Additional Instructions:
{prescription['notes']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        if prescription.get('follow_up_date'):
            print_text += f"""
Follow-up Date: {prescription['follow_up_date']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        print_text += "\n"
        
        # Show print dialog
        self._show_print_dialog(print_text, f"Prescription - {prescription_id}")
    
    def prescription_dialog(self, prescription_id=None):
        """Prescription form dialog"""
        is_edit_mode = prescription_id is not None
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Prescription" if is_edit_mode else "New Prescription")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.parent)
        
        # Maximize the window to fill the screen
        try:
            # Windows
            dialog.state('zoomed')
        except:
            try:
                # Linux
                dialog.attributes('-zoomed', True)
            except:
                # Fallback: set to screen size
                dialog.update_idletasks()
                width = dialog.winfo_screenwidth()
                height = dialog.winfo_screenheight()
                dialog.geometry(f"{width}x{height}+0+0")
        
        # Load existing prescription data if editing
        prescription_data = None
        existing_items = []
        if is_edit_mode:
            prescription_data = self.db.get_prescription_by_id(prescription_id)
            if not prescription_data:
                messagebox.showerror("Error", "Prescription not found")
                dialog.destroy()
                return
            existing_items = self.db.get_prescription_items(prescription_id)
        
        # Make dialog modal but ensure input works
        dialog.lift()
        dialog.focus_force()
        try:
            dialog.grab_set_global(False)
        except:
            dialog.grab_set()
        
        # Button frame - pack first at bottom (always visible)
        button_frame = tk.Frame(dialog, bg='#f0f0f0', relief=tk.RAISED, bd=2)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)
        
        # Create canvas and scrollbar for scrollable content
        canvas_frame = tk.Frame(dialog, bg='#f0f0f0')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        canvas = tk.Canvas(canvas_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        def configure_scroll_region(event=None):
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        canvas.bind('<Configure>', configure_canvas_width)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel to canvas (Windows and Mac)
        def _on_mousewheel(event):
            try:
                # Windows
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                # Linux/Mac
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Also support Linux mousewheel
        canvas.bind("<Button-4>", _on_mousewheel)
        canvas.bind("<Button-5>", _on_mousewheel)
        
        # Main content frame - inside scrollable frame
        main_frame = tk.Frame(scrollable_frame, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        if not is_edit_mode:
            prescription_id = generate_id('PRES')
        tk.Label(main_frame, text=f"Prescription ID: {prescription_id}", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=5)
        
        # Form fields - use grid for side-by-side layouts
        form_frame = tk.Frame(main_frame, bg='#f0f0f0')
        form_frame.pack(fill=tk.X, expand=False, pady=10)
        
        # Get all patients for dropdown
        all_patients = self.db.get_all_patients()
        patient_options = []
        patient_id_map = {}  # Map display string to patient_id
        
        for p in all_patients:
            display_text = f"{p['patient_id']} - {p['first_name']} {p['last_name']}"
            patient_options.append(display_text)
            patient_id_map[display_text] = p['patient_id']
        
        # Get all doctors for dropdown
        all_doctors = self.db.get_all_doctors()
        doctor_options = []
        doctor_id_map = {}  # Map display string to doctor_id
        
        for d in all_doctors:
            display_text = f"{d['doctor_id']} - Dr. {d['first_name']} {d['last_name']} ({d['specialization']})"
            doctor_options.append(display_text)
            doctor_id_map[display_text] = d['doctor_id']
        
        # Row 1: Patient and Doctor side by side
        tk.Label(form_frame, text="Patient *:", font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50').grid(row=0, column=0, sticky='w', padx=5, pady=8)
        patient_var = tk.StringVar()
        patient_combo = ttk.Combobox(form_frame, textvariable=patient_var, values=patient_options, font=('Arial', 10), width=35, state='normal')
        patient_combo.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        form_frame.columnconfigure(0, weight=1)
        
        tk.Label(form_frame, text="Doctor *:", font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50').grid(row=0, column=1, sticky='w', padx=5, pady=8)
        doctor_var = tk.StringVar()
        doctor_combo = ttk.Combobox(form_frame, textvariable=doctor_var, values=doctor_options, font=('Arial', 10), width=35, state='normal')
        doctor_combo.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        form_frame.columnconfigure(1, weight=1)
        
        # Make comboboxes searchable and auto-focus
        def on_patient_enter(event):
            patient_combo.focus_set()
        patient_combo.bind('<Enter>', on_patient_enter)
        
        def filter_patient(*args):
            value = patient_var.get().lower()
            if value == '':
                patient_combo['values'] = patient_options
            else:
                filtered = [opt for opt in patient_options if value in opt.lower()]
                patient_combo['values'] = filtered
                if filtered:
                    patient_combo.event_generate('<Button-1>')
        patient_var.trace('w', filter_patient)
        
        def on_doctor_enter(event):
            doctor_combo.focus_set()
        doctor_combo.bind('<Enter>', on_doctor_enter)
        
        def filter_doctor(*args):
            value = doctor_var.get().lower()
            if value == '':
                doctor_combo['values'] = doctor_options
            else:
                filtered = [opt for opt in doctor_options if value in opt.lower()]
                doctor_combo['values'] = filtered
                if filtered:
                    doctor_combo.event_generate('<Button-1>')
        doctor_var.trace('w', filter_doctor)
        
        # Row 2: Patient Info Display Panel (spans both columns)
        patient_info_frame = tk.LabelFrame(form_frame, text="Patient Information", font=('Arial', 9, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        patient_info_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=8)
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)
        
        patient_info_label = tk.Label(patient_info_frame, text="Select a patient to view information", 
                                       font=('Arial', 9), bg='#f0f0f0', fg='#7f8c8d', justify='left')
        patient_info_label.pack(anchor='w', padx=10, pady=5)
        
        def update_patient_info(*args):
            selected_patient = patient_var.get()
            patient_id = None
            if selected_patient in patient_id_map:
                patient_id = patient_id_map[selected_patient]
            else:
                parts = selected_patient.split(' - ')
                if parts and parts[0].startswith('PAT-'):
                    patient_id = parts[0]
            
            if patient_id:
                patient = self.db.get_patient_by_id(patient_id)
                if patient:
                    age_info = ""
                    if patient.get('date_of_birth'):
                        try:
                            from datetime import datetime
                            dob = datetime.strptime(patient['date_of_birth'], '%Y-%m-%d')
                            today = datetime.now()
                            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                            age_info = f"Age: {age} years"
                        except:
                            age_info = f"DOB: {patient['date_of_birth']}"
                    
                    info_lines = []
                    if age_info:
                        info_lines.append(age_info)
                    if patient.get('gender'):
                        info_lines.append(f"Gender: {patient['gender']}")
                    if patient.get('blood_group'):
                        info_lines.append(f"Blood Group: {patient['blood_group']}")
                    if patient.get('allergies'):
                        info_lines.append(f"⚠️ Allergies: {patient['allergies']}")
                    else:
                        info_lines.append("Allergies: None")
                    
                    patient_info_label.config(text=" | ".join(info_lines), fg='#2c3e50')
                else:
                    patient_info_label.config(text="Patient information not found", fg='#e74c3c')
            else:
                patient_info_label.config(text="Select a patient to view information", fg='#7f8c8d')
        
        patient_var.trace('w', update_patient_info)
        
        # Row 3: Date and Follow-up Date side by side
        tk.Label(form_frame, text="Date:", font=('Arial', 10), bg='#f0f0f0').grid(row=3, column=0, sticky='w', padx=5, pady=8)
        date_entry = tk.Entry(form_frame, font=('Arial', 10), state='normal')
        date_entry.insert(0, get_current_date())
        date_entry.grid(row=4, column=0, sticky='ew', padx=5, pady=5)
        date_entry.bind('<Enter>', lambda e: date_entry.focus_set())
        date_entry.bind('<Button-1>', lambda e: date_entry.focus_set())
        
        tk.Label(form_frame, text="Follow-up Date (optional):", font=('Arial', 10), bg='#f0f0f0').grid(row=3, column=1, sticky='w', padx=5, pady=8)
        followup_entry = tk.Entry(form_frame, font=('Arial', 10), state='normal')
        followup_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=5)
        followup_entry.bind('<Enter>', lambda e: followup_entry.focus_set())
        followup_entry.bind('<Button-1>', lambda e: followup_entry.focus_set())
        
        # Row 5: Chief Complaints and Examination side by side
        tk.Label(form_frame, text="Chief Complaints / Symptoms:", font=('Arial', 10), bg='#f0f0f0').grid(row=5, column=0, sticky='w', padx=5, pady=8)
        complaints_text = tk.Text(form_frame, font=('Arial', 10), height=3, state='normal', wrap=tk.WORD)
        complaints_text.grid(row=6, column=0, sticky='nsew', padx=5, pady=5)
        complaints_text.bind('<Enter>', lambda e: complaints_text.focus_set())
        complaints_text.bind('<Button-1>', lambda e: complaints_text.focus_set())
        
        tk.Label(form_frame, text="Examination / Vitals:", font=('Arial', 10), bg='#f0f0f0').grid(row=5, column=1, sticky='w', padx=5, pady=8)
        examination_text = tk.Text(form_frame, font=('Arial', 10), height=3, state='normal', wrap=tk.WORD)
        examination_text.grid(row=6, column=1, sticky='nsew', padx=5, pady=5)
        examination_text.bind('<Enter>', lambda e: examination_text.focus_set())
        examination_text.bind('<Button-1>', lambda e: examination_text.focus_set())
        form_frame.rowconfigure(6, weight=0, minsize=60)
        
        # Row 7: Diagnosis (full width)
        tk.Label(form_frame, text="Diagnosis:", font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50').grid(row=7, column=0, columnspan=2, sticky='w', padx=5, pady=8)
        diagnosis_text = tk.Text(form_frame, font=('Arial', 10), height=3, state='normal', wrap=tk.WORD)
        diagnosis_text.grid(row=8, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        diagnosis_text.bind('<Enter>', lambda e: diagnosis_text.focus_set())
        diagnosis_text.bind('<Button-1>', lambda e: diagnosis_text.focus_set())
        form_frame.rowconfigure(8, weight=0, minsize=60)
        
        # Row 9: Notes (full width)
        tk.Label(form_frame, text="Notes / Additional Instructions:", font=('Arial', 10), bg='#f0f0f0').grid(row=9, column=0, columnspan=2, sticky='w', padx=5, pady=8)
        notes_text = tk.Text(form_frame, font=('Arial', 10), height=2, state='normal', wrap=tk.WORD)
        notes_text.grid(row=10, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        notes_text.bind('<Enter>', lambda e: notes_text.focus_set())
        notes_text.bind('<Button-1>', lambda e: notes_text.focus_set())
        form_frame.rowconfigure(10, weight=0, minsize=40)
        
        # Pre-populate fields if in edit mode (after all fields are created)
        if is_edit_mode and prescription_data:
            # Pre-populate patient
            patient_id_for_search = prescription_data.get('patient_id')
            for display_text, pid in patient_id_map.items():
                if pid == patient_id_for_search:
                    patient_var.set(display_text)
                    break
            
            # Pre-populate doctor
            doctor_id_for_search = prescription_data.get('doctor_id')
            for display_text, did in doctor_id_map.items():
                if did == doctor_id_for_search:
                    doctor_var.set(display_text)
                    break
            
            # Pre-populate date
            if prescription_data.get('prescription_date'):
                date_entry.delete(0, tk.END)
                date_entry.insert(0, prescription_data['prescription_date'])
            
            # Pre-populate text fields
            if prescription_data.get('chief_complaints'):
                complaints_text.insert('1.0', prescription_data['chief_complaints'])
            if prescription_data.get('examination'):
                examination_text.insert('1.0', prescription_data['examination'])
            if prescription_data.get('diagnosis'):
                diagnosis_text.insert('1.0', prescription_data['diagnosis'])
            if prescription_data.get('notes'):
                notes_text.insert('1.0', prescription_data['notes'])
            if prescription_data.get('follow_up_date'):
                followup_entry.insert(0, prescription_data['follow_up_date'])
            
            # Pre-populate medicines (will be added later after med_tree is created)
        
        # Medicines frame - don't expand to fill all space
        medicines_frame = tk.LabelFrame(main_frame, text="Medicines", font=('Arial', 10, 'bold'), bg='#f0f0f0')
        medicines_frame.pack(fill=tk.BOTH, expand=False, pady=10)  # Changed expand to False
        
        # Medicines list - limit height
        med_columns = ('Medicine', 'Form', 'Dosage', 'Frequency', 'Duration')
        med_tree = ttk.Treeview(medicines_frame, columns=med_columns, show='headings', height=4)  # Reduced height
        
        # Configure style for better visibility
        med_style = ttk.Style()
        med_style.configure("Treeview", font=('Arial', 9), rowheight=20)
        med_style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        # Configure column widths
        med_tree.heading('Medicine', text='Medicine')
        med_tree.column('Medicine', width=180)
        med_tree.heading('Form', text='Form')
        med_tree.column('Form', width=80)
        med_tree.heading('Dosage', text='Dosage')
        med_tree.column('Dosage', width=100)
        med_tree.heading('Frequency', text='Frequency')
        med_tree.column('Frequency', width=100)
        med_tree.heading('Duration', text='Duration')
        med_tree.column('Duration', width=100)
        # Frame for tree and scrollbar
        med_tree_frame = tk.Frame(medicines_frame, bg='#f0f0f0')
        med_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        med_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for medicine tree
        med_tree_scrollbar = ttk.Scrollbar(med_tree_frame, orient=tk.VERTICAL, command=med_tree.yview)
        med_tree.configure(yscrollcommand=med_tree_scrollbar.set)
        med_tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        medicines = []
        
        # Pre-populate medicines if in edit mode
        if is_edit_mode and existing_items:
            for item in existing_items:
                med_name = item.get('medicine_name', '')
                dosage = item.get('dosage', '')
                frequency = item.get('frequency', '')
                duration = item.get('duration', '')
                form_value = ''
                company_name = ''
                
                # Try to get company and form from medicines table
                if med_name:
                    med_info = self.db.get_medicine_by_name(med_name)
                    if med_info:
                        company_name = med_info.get('company_name', '')
                        form_value = med_info.get('form', '')
                
                # Display format
                if company_name:
                    display_name = f"{company_name} - {med_name}"
                else:
                    display_name = med_name
                
                # Add to tree
                med_tree.insert('', tk.END, values=(display_name, form_value, dosage, frequency, duration))
                medicines.append({
                    'medicine_name': med_name,
                    'company_name': company_name,
                    'form': form_value,
                    'dosage': dosage,
                    'frequency': frequency,
                    'duration': duration,
                    'instructions': item.get('instructions', '')
                })
        
        # Add medicine frame - use grid layout for better organization
        add_med_frame = tk.Frame(medicines_frame, bg='#f0f0f0')
        add_med_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Get all company names and medicines from database
        all_companies = self.db.get_all_company_names()
        all_medicines = self.db.get_all_medicines()
        all_medicine_names = list(set([med['medicine_name'] for med in all_medicines]))
        all_medicine_names.sort()
        
        # Row 1: Company and Medicine Name
        tk.Label(add_med_frame, text="Company (Optional):", font=('Arial', 10), bg='#f0f0f0').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        company_var = tk.StringVar()
        company_combo = ttk.Combobox(add_med_frame, textvariable=company_var, values=all_companies, font=('Arial', 10), width=20, state='normal')
        company_combo.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        add_med_frame.columnconfigure(0, weight=1)
        
        tk.Label(add_med_frame, text="Medicine Name *:", font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50').grid(row=0, column=1, sticky='w', padx=5, pady=5)
        med_name_var = tk.StringVar()
        med_name_entry = ttk.Combobox(add_med_frame, textvariable=med_name_var, values=all_medicine_names, font=('Arial', 10), width=30, state='normal')
        med_name_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        add_med_frame.columnconfigure(1, weight=2)
        
        # Row 2: Form, Dosage, Frequency, Duration
        tk.Label(add_med_frame, text="Form:", font=('Arial', 10), bg='#f0f0f0').grid(row=2, column=0, sticky='w', padx=5, pady=5)
        form_var = tk.StringVar()
        form_entry = tk.Entry(add_med_frame, textvariable=form_var, font=('Arial', 10), width=18, state='readonly', bg='#e8e8e8')
        form_entry.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
        
        tk.Label(add_med_frame, text="Dosage *:", font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50').grid(row=2, column=1, sticky='w', padx=5, pady=5)
        dosage_entry = tk.Entry(add_med_frame, font=('Arial', 10), width=18, state='normal')
        dosage_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        tk.Label(add_med_frame, text="Frequency *:", font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50').grid(row=2, column=2, sticky='w', padx=5, pady=5)
        frequency_entry = tk.Entry(add_med_frame, font=('Arial', 10), width=18, state='normal')
        frequency_entry.grid(row=3, column=2, sticky='ew', padx=5, pady=5)
        
        tk.Label(add_med_frame, text="Duration *:", font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50').grid(row=2, column=3, sticky='w', padx=5, pady=5)
        duration_entry = tk.Entry(add_med_frame, font=('Arial', 10), width=18, state='normal')
        duration_entry.grid(row=3, column=3, sticky='ew', padx=5, pady=5)
        add_med_frame.columnconfigure(2, weight=1)
        add_med_frame.columnconfigure(3, weight=1)
        
        # Company combobox functionality
        def filter_company(*args):
            value = company_var.get().lower()
            if value == '':
                company_combo['values'] = all_companies
            else:
                filtered = [comp for comp in all_companies if value in comp.lower()]
                company_combo['values'] = filtered
                if filtered:
                    company_combo.event_generate('<Button-1>')
        company_var.trace('w', filter_company)
        company_combo.bind('<Enter>', lambda e: company_combo.focus_set())
        company_combo.bind('<Button-1>', lambda e: company_combo.focus_set())
        
        # Update medicine list based on selected company
        def update_medicine_list(*args):
            selected_company = company_var.get().strip()
            if selected_company:
                company_medicines = self.db.get_medicines_by_company(selected_company)
                medicine_names = [med['medicine_name'] for med in company_medicines]
                med_name_entry['values'] = medicine_names
            else:
                med_name_entry['values'] = all_medicine_names
        company_var.trace('w', update_medicine_list)
        
        # Medicine combobox functionality
        def filter_medicine(*args):
            value = med_name_var.get().lower()
            current_values = list(med_name_entry['values'])
            if value == '':
                med_name_entry['values'] = current_values
            else:
                filtered = [med for med in current_values if value in med.lower()]
                med_name_entry['values'] = filtered
                if filtered:
                    med_name_entry.event_generate('<Button-1>')
        med_name_var.trace('w', filter_medicine)
        med_name_entry.bind('<Enter>', lambda e: med_name_entry.focus_set())
        med_name_entry.bind('<Button-1>', lambda e: med_name_entry.focus_set())
        
        # Auto-fill dosage and form when medicine is selected
        def on_medicine_select(event=None):
            selected_company = company_var.get().strip()
            selected_med = med_name_var.get().strip()
            if selected_med:
                medicine = self.db.get_medicine_by_name(selected_med, selected_company if selected_company else None)
                if medicine:
                    if medicine.get('common_dosage') and not dosage_entry.get():
                        dosage_entry.delete(0, tk.END)
                        dosage_entry.insert(0, medicine['common_dosage'])
                    if medicine.get('form'):
                        form_var.set(medicine['form'])
                    else:
                        form_var.set('')
        med_name_entry.bind('<<ComboboxSelected>>', on_medicine_select)
        med_name_entry.bind('<Return>', on_medicine_select)
        
        # Focus bindings for entries
        dosage_entry.bind('<Enter>', lambda e: dosage_entry.focus_set())
        dosage_entry.bind('<Button-1>', lambda e: dosage_entry.focus_set())
        frequency_entry.bind('<Enter>', lambda e: frequency_entry.focus_set())
        frequency_entry.bind('<Button-1>', lambda e: frequency_entry.focus_set())
        duration_entry.bind('<Enter>', lambda e: duration_entry.focus_set())
        duration_entry.bind('<Button-1>', lambda e: duration_entry.focus_set())
        
        def add_medicine():
            company_name = company_var.get().strip()
            med_name = med_name_var.get().strip()
            dosage = dosage_entry.get().strip()
            frequency = frequency_entry.get().strip()
            duration = duration_entry.get().strip()
            
            if not med_name:
                messagebox.showwarning("Warning", "Please enter or select a medicine name")
                med_name_entry.focus_set()
                return
            
            if not dosage:
                messagebox.showwarning("Warning", "Please enter dosage")
                dosage_entry.focus_set()
                return
            
            if not frequency:
                messagebox.showwarning("Warning", "Please enter frequency")
                frequency_entry.focus_set()
                return
            
            if not duration:
                messagebox.showwarning("Warning", "Please enter duration")
                duration_entry.focus_set()
                return
            
            # Get company name and medicine name from separate fields
            company_name = company_var.get().strip()
            med_name = med_name_var.get().strip()
            
            # Get form value
            form_value = form_var.get().strip()
            
            # Display format: "Company - Medicine" or just "Medicine"
            if company_name:
                display_name = f"{company_name} - {med_name}"
            else:
                display_name = med_name
            
            # Add to tree
            med_tree.insert('', tk.END, values=(display_name, form_value, dosage, frequency, duration))
            medicines.append({
                'medicine_name': med_name,
                'company_name': company_name,
                'form': form_value,
                'dosage': dosage,
                'frequency': frequency,
                'duration': duration,
                'instructions': ''
            })
            
            # Clear fields
            company_var.set('')
            med_name_var.set('')
            form_var.set('')
            dosage_entry.delete(0, tk.END)
            frequency_entry.delete(0, tk.END)
            duration_entry.delete(0, tk.END)
            
            # Reset medicine list to show all
            med_name_entry['values'] = all_medicine_names
            
            # Set focus back to company name for next entry
            company_combo.focus_set()
        
        # Remove Medicine button function
        def remove_medicine():
            selected_items = med_tree.selection()
            if not selected_items:
                messagebox.showwarning("Warning", "Please select a medicine to remove")
                return
            
            # Get all tree items to find indices
            all_items = med_tree.get_children()
            
            # Collect indices to remove (in reverse order to avoid index shifting issues)
            indices_to_remove = []
            for item in selected_items:
                try:
                    idx = all_items.index(item)
                    indices_to_remove.append(idx)
                except ValueError:
                    continue
            
            # Sort in reverse order so we remove from end to beginning
            indices_to_remove.sort(reverse=True)
            
            # Remove from medicines list and tree
            for idx in indices_to_remove:
                if 0 <= idx < len(medicines):
                    medicines.pop(idx)
                # Remove from tree using the item ID
                if idx < len(all_items):
                    med_tree.delete(all_items[idx])
        
        # Row 4: Add and Remove Medicine buttons
        add_med_btn = tk.Button(
            add_med_frame,
            text="+ Add Medicine",
            command=add_medicine,
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2',
            relief=tk.RAISED,
            bd=2,
            state=tk.NORMAL
        )
        add_med_btn.grid(row=4, column=0, columnspan=2, sticky='w', padx=5, pady=10)
        
        remove_med_btn = tk.Button(
            add_med_frame,
            text="🗑️ Remove Selected",
            command=remove_medicine,
            font=('Arial', 10, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2',
            relief=tk.RAISED,
            bd=2,
            state=tk.NORMAL
        )
        remove_med_btn.grid(row=4, column=2, columnspan=2, sticky='e', padx=5, pady=10)
        
        # Bind Delete key to remove medicine
        def on_delete_key(event):
            if med_tree.focus():
                remove_medicine()
            return "break"
        
        med_tree.bind('<Delete>', on_delete_key)
        med_tree.bind('<Double-1>', lambda e: remove_medicine())  # Double-click to remove
        
        # Bind Enter key to add medicine
        def on_med_enter(event):
            add_medicine()
            return "break"
        
        # Bind Enter key to add medicine (skip for combobox as it has its own handler)
        dosage_entry.bind('<Return>', on_med_enter)
        frequency_entry.bind('<Return>', on_med_enter)
        duration_entry.bind('<Return>', on_med_enter)
        
        # For combobox, Enter should add medicine after selection
        def on_med_combobox_return(event):
            if med_name_var.get():
                on_medicine_select()
                # Move focus to dosage
                dosage_entry.focus_set()
            return "break"
        
        med_name_entry.bind('<Return>', on_med_combobox_return)
        
        def save_prescription():
            # Get selected patient ID
            patient_display = patient_var.get()
            patient_id = None
            if patient_display in patient_id_map:
                patient_id = patient_id_map[patient_display]
            else:
                # Try to extract ID from display text (format: "PAT-XXX - Name")
                parts = patient_display.split(' - ')
                if parts and parts[0].startswith('PAT-'):
                    patient_id = parts[0]
            
            # Get selected doctor ID
            doctor_display = doctor_var.get()
            doctor_id = None
            if doctor_display in doctor_id_map:
                doctor_id = doctor_id_map[doctor_display]
            else:
                # Try to extract ID from display text (format: "DOC-XXX - Dr. Name")
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
            
            data = {
                'prescription_id': prescription_id,
                'patient_id': patient_id,
                'doctor_id': doctor_id,
                'prescription_date': date_entry.get() or get_current_date(),
                'chief_complaints': complaints_text.get('1.0', tk.END).strip(),
                'examination': examination_text.get('1.0', tk.END).strip(),
                'diagnosis': diagnosis_text.get('1.0', tk.END).strip(),
                'notes': notes_text.get('1.0', tk.END).strip(),
                'follow_up_date': followup_entry.get().strip()
            }
            
            # Use update or add based on mode
            success = False
            if is_edit_mode:
                success = self.db.update_prescription(prescription_id, data, medicines)
                success_message = "Prescription updated successfully"
            else:
                success = self.db.add_prescription(data, medicines)
                success_message = "Prescription created successfully"
            
            if success:
                # Release grab before destroying
                try:
                    dialog.grab_release()
                except:
                    pass
                dialog.destroy()
                
                # Process all pending events immediately - CRITICAL for immediate button response
                root = self.parent.winfo_toplevel()
                root.update_idletasks()
                root.update()
                root.update_idletasks()
                
                # Return focus to main window
                root.focus_force()
                root.update_idletasks()
                root.update()
                
                # Ensure all events are processed and UI is ready
                root.update_idletasks()
                
                # Final update to ensure buttons are immediately responsive
                root.update()
                root.update_idletasks()
                
                # Show message after dialog is closed (non-blocking) - delayed to not interfere
                root.after(150, lambda: messagebox.showinfo("Success", success_message))
                # Refresh list asynchronously
                root.after(250, self.refresh_list)
            else:
                messagebox.showerror("Error", f"Failed to {'update' if is_edit_mode else 'create'} prescription")
        
        # Button frame is already packed at the bottom above
        
        # Inner frame for button spacing
        inner_button_frame = tk.Frame(button_frame, bg='#f0f0f0')
        inner_button_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Save/Update Prescription button - make it prominent
        save_btn = tk.Button(
            inner_button_frame,
            text="💾 Update Prescription" if is_edit_mode else "💾 Save Prescription",
            command=save_prescription,
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='black',
            padx=30,
            pady=10,
            cursor='hand2',
            relief=tk.RAISED,
            bd=3,
            state=tk.NORMAL,
            activebackground='#229954',
            activeforeground='white'
        )
        save_btn.pack(side=tk.LEFT, padx=10)
        
        def close_dialog():
            try:
                dialog.grab_release()
            except:
                pass
            dialog.destroy()
            
            # Process all pending events immediately - CRITICAL for immediate button response
            root = self.parent.winfo_toplevel()
            root.update_idletasks()
            root.update()
            root.update_idletasks()
            
            # Return focus to main window
            root.focus_force()
            root.update_idletasks()
            root.update()
            
            # Ensure all events are processed and UI is ready
            root.update_idletasks()
        
        close_btn = tk.Button(
            inner_button_frame,
            text="Close",
            command=close_dialog,
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            padx=30,
            pady=8,
            cursor='hand2',
            state=tk.NORMAL,
            activebackground='#7f8c8d',
            activeforeground='white'
        )
        close_btn.pack(side=tk.LEFT, padx=10)
        
        # Bind Enter key on dialog to save prescription
        def on_dialog_return(event):
            # If focus is on a medicine field, add medicine
            focused = dialog.focus_get()
            if focused in [med_name_entry, dosage_entry, frequency_entry, duration_entry]:
                add_medicine()
            else:
                # Otherwise save prescription
                save_prescription()
            return "break"
        
        dialog.bind('<Return>', on_dialog_return)
        
        # Ensure all medicine entry fields are enabled and clickable
        def enable_medicine_fields():
            med_name_entry.config(state='normal', takefocus=1)
            dosage_entry.config(state='normal', takefocus=1)
            frequency_entry.config(state='normal', takefocus=1)
            duration_entry.config(state='normal', takefocus=1)
            # Make sure they can be clicked
            med_name_entry.bind('<Button-1>', lambda e: med_name_entry.focus_set())
            dosage_entry.bind('<Button-1>', lambda e: dosage_entry.focus_set())
            frequency_entry.bind('<Button-1>', lambda e: frequency_entry.focus_set())
            duration_entry.bind('<Button-1>', lambda e: duration_entry.focus_set())
        
        # Enable medicine fields after dialog is fully rendered
        dialog.update_idletasks()
        dialog.after(50, enable_medicine_fields)
        
        # Set focus on patient combo when dialog opens
        dialog.after(100, lambda: patient_combo.focus_set())
    
    def _show_print_dialog(self, text, title="Print"):
        """Show print dialog with formatted text"""
        print_dialog = tk.Toplevel(self.parent)
        print_dialog.title(title)
        print_dialog.geometry("700x600")
        print_dialog.configure(bg='#f0f0f0')
        print_dialog.transient(self.parent)
        
        # Text widget for display
        text_frame = tk.Frame(print_dialog, bg='#f0f0f0')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        text_widget = tk.Text(text_frame, font=('Courier', 10), wrap=tk.WORD, bg='white')
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert('1.0', text)
        text_widget.config(state=tk.DISABLED)
        
        # Button frame
        button_frame = tk.Frame(print_dialog, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def print_text():
            """Print the text"""
            try:
                import subprocess
                import platform
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
                temp_file.write(text)
                temp_file.close()
                
                # Print based on OS
                system = platform.system()
                if system == "Windows":
                    # On Windows, use notepad print or PowerShell
                    try:
                        # Try using PowerShell to print
                        subprocess.run(['powershell', '-Command', 
                                      f'Get-Content "{temp_file.name}" | Out-Printer'], 
                                     check=True, timeout=10)
                        messagebox.showinfo("Print", "Document sent to default printer!")
                    except:
                        # Fallback: open in notepad for manual printing
                        os.startfile(temp_file.name, 'print')
                        messagebox.showinfo("Print", "Print dialog opened. Please select your printer and click Print.")
                elif system == "Darwin":  # macOS
                    subprocess.run(['lpr', temp_file.name], check=True)
                    messagebox.showinfo("Print", "Document sent to default printer!")
                else:  # Linux
                    subprocess.run(['lp', temp_file.name], check=True)
                    messagebox.showinfo("Print", "Document sent to default printer!")
                
                # Clean up after a delay
                def cleanup():
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                print_dialog.after(5000, cleanup)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to print: {str(e)}\n\nYou can save the document and print it manually.")
        
        def save_as_pdf():
            """Save document as PDF"""
            try:
                # Generate default filename from title
                default_filename = title.replace(" - ", "_").replace(" ", "_") + ".pdf"
                
                # Try using reportlab if available
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                    from reportlab.lib.styles import getSampleStyleSheet
                    from reportlab.lib.units import inch
                    
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".pdf",
                        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                        title="Save Prescription as PDF",
                        initialfile=default_filename
                    )
                    
                    if filename:
                        doc = SimpleDocTemplate(filename, pagesize=letter)
                        styles = getSampleStyleSheet()
                        story = []
                        
                        # Add content line by line
                        for line in text.split('\n'):
                            if line.strip():
                                # Handle special characters
                                line = line.replace('╔', '=').replace('╗', '=')
                                line = line.replace('║', '|').replace('╚', '=')
                                line = line.replace('╝', '=').replace('━', '-')
                                line = line.replace('═', '=')
                                
                                if line.strip().startswith('PRESCRIPTION') or '━━━' in line:
                                    story.append(Paragraph(line, styles['Heading1']))
                                else:
                                    story.append(Paragraph(line, styles['Normal']))
                                story.append(Spacer(1, 0.1*inch))
                        
                        doc.build(story)
                        messagebox.showinfo("Success", f"Prescription saved as PDF:\n{filename}")
                    return
                except ImportError:
                    # reportlab not available - install it or use alternative
                    messagebox.showwarning(
                        "PDF Library Not Found",
                        "The 'reportlab' library is required to save as PDF.\n\n"
                        "Please install it using: pip install reportlab\n\n"
                        "Alternatively, you can save as text file and convert it manually."
                    )
                    
                    # Fallback: Save as text file
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".txt",
                        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                        title="Save Prescription",
                        initialfile=default_filename.replace(".pdf", ".txt")
                    )
                    
                    if filename:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(text)
                        messagebox.showinfo("Success", 
                            f"Prescription saved as text file:\n{filename}\n\n"
                            f"Note: Install reportlab (pip install reportlab) to save as PDF directly.")
                        
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")
        
        tk.Button(
            button_frame,
            text="🖨️ Print",
            command=print_text,
            font=('Arial', 11, 'bold'),
            bg='#e67e22',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="📄 Save as PDF",
            command=save_as_pdf,
            font=('Arial', 11, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        def close_dialog():
            print_dialog.destroy()
        
        tk.Button(
            button_frame,
            text="Close",
            command=close_dialog,
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)

