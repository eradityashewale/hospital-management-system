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
    
    def prescription_dialog(self):
        """Prescription form dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("New Prescription")
        dialog.geometry("700x650")  # Increased height to ensure buttons are visible
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.parent)
        
        # Make dialog modal but ensure input works
        dialog.lift()
        dialog.focus_force()
        try:
            dialog.grab_set_global(False)
        except:
            dialog.grab_set()
        
        # Main content frame - pack before button frame
        main_frame = tk.Frame(dialog, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        prescription_id = generate_id('PRES')
        tk.Label(main_frame, text=f"Prescription ID: {prescription_id}", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=5)
        
        # Form fields - don't expand to fill all space
        form_frame = tk.Frame(main_frame, bg='#f0f0f0')
        form_frame.pack(fill=tk.X, expand=False, pady=10)  # Changed to fill=tk.X, expand=False
        
        # Patient selection with searchable dropdown
        tk.Label(form_frame, text="Patient *:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        
        # Get all patients for dropdown
        all_patients = self.db.get_all_patients()
        patient_options = []
        patient_id_map = {}  # Map display string to patient_id
        
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
            width=37,
            state='normal'  # 'normal' allows typing to search
        )
        patient_combo.pack(fill=tk.X, pady=5)
        
        # Make patient combo auto-focus on mouse enter
        def on_patient_enter(event):
            patient_combo.focus_set()
        patient_combo.bind('<Enter>', on_patient_enter)
        
        # Make combobox searchable - filter as user types
        def filter_patient(*args):
            value = patient_var.get().lower()
            if value == '':
                patient_combo['values'] = patient_options
            else:
                filtered = [opt for opt in patient_options if value in opt.lower()]
                patient_combo['values'] = filtered
                # Open dropdown if there are matches
                if filtered:
                    patient_combo.event_generate('<Button-1>')
        
        patient_var.trace('w', filter_patient)
        
        # Doctor selection with searchable dropdown
        tk.Label(form_frame, text="Doctor *:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        
        # Get all doctors for dropdown
        all_doctors = self.db.get_all_doctors()
        doctor_options = []
        doctor_id_map = {}  # Map display string to doctor_id
        
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
            width=37,
            state='normal'  # 'normal' allows typing to search
        )
        doctor_combo.pack(fill=tk.X, pady=5)
        
        # Make doctor combo auto-focus on mouse enter
        def on_doctor_enter(event):
            doctor_combo.focus_set()
        doctor_combo.bind('<Enter>', on_doctor_enter)
        
        # Make combobox searchable - filter as user types
        def filter_doctor(*args):
            value = doctor_var.get().lower()
            if value == '':
                doctor_combo['values'] = doctor_options
            else:
                filtered = [opt for opt in doctor_options if value in opt.lower()]
                doctor_combo['values'] = filtered
                # Open dropdown if there are matches
                if filtered:
                    doctor_combo.event_generate('<Button-1>')
        
        doctor_var.trace('w', filter_doctor)
        
        tk.Label(form_frame, text="Date:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        date_entry = tk.Entry(form_frame, font=('Arial', 10), width=40, state='normal')
        date_entry.insert(0, get_current_date())
        date_entry.pack(fill=tk.X, pady=5)
        
        # Make date entry auto-focus on mouse enter
        def on_date_enter(event):
            date_entry.focus_set()
            date_entry.icursor(tk.END)  # Move cursor to end
        date_entry.bind('<Enter>', on_date_enter)
        date_entry.bind('<Button-1>', lambda e: date_entry.focus_set())
        
        tk.Label(form_frame, text="Diagnosis:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        diagnosis_text = tk.Text(form_frame, font=('Arial', 10), width=40, height=3, state='normal')
        diagnosis_text.pack(fill=tk.X, pady=5)
        
        # Make diagnosis text auto-focus on mouse enter
        def on_diagnosis_enter(event):
            diagnosis_text.focus_set()
        diagnosis_text.bind('<Enter>', on_diagnosis_enter)
        diagnosis_text.bind('<Button-1>', lambda e: diagnosis_text.focus_set())
        
        # Medicines frame - don't expand to fill all space
        medicines_frame = tk.LabelFrame(main_frame, text="Medicines", font=('Arial', 10, 'bold'), bg='#f0f0f0')
        medicines_frame.pack(fill=tk.BOTH, expand=False, pady=10)  # Changed expand to False
        
        # Medicines list - limit height
        med_columns = ('Medicine', 'Dosage', 'Frequency', 'Duration')
        med_tree = ttk.Treeview(medicines_frame, columns=med_columns, show='headings', height=4)  # Reduced height
        
        # Configure style for better visibility
        med_style = ttk.Style()
        med_style.configure("Treeview", font=('Arial', 9), rowheight=20)
        med_style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        for col in med_columns:
            med_tree.heading(col, text=col)
            med_tree.column(col, width=120)
        med_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        medicines = []
        
        # Add medicine frame
        add_med_frame = tk.Frame(medicines_frame, bg='#f0f0f0')
        add_med_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Medicine input fields with labels
        med_input_frame = tk.Frame(add_med_frame, bg='#f0f0f0')
        med_input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Medicine name
        tk.Label(med_input_frame, text="Medicine:", font=('Arial', 9), bg='#f0f0f0').pack(side=tk.LEFT, padx=2)
        med_name_entry = tk.Entry(med_input_frame, font=('Arial', 9), width=15, state='normal')
        med_name_entry.pack(side=tk.LEFT, padx=2)
        med_name_entry.config(state='normal', takefocus=1)  # Ensure it can receive focus
        
        # Auto-focus on mouse enter for medicine name
        def on_med_name_enter(event):
            med_name_entry.focus_set()
        med_name_entry.bind('<Enter>', on_med_name_enter)
        med_name_entry.bind('<Button-1>', lambda e: med_name_entry.focus_set())
        
        # Dosage
        tk.Label(med_input_frame, text="Dosage:", font=('Arial', 9), bg='#f0f0f0').pack(side=tk.LEFT, padx=2)
        dosage_entry = tk.Entry(med_input_frame, font=('Arial', 9), width=10, state='normal')
        dosage_entry.pack(side=tk.LEFT, padx=2)
        dosage_entry.config(state='normal', takefocus=1)  # Ensure it can receive focus
        
        # Auto-focus on mouse enter for dosage
        def on_dosage_enter(event):
            dosage_entry.focus_set()
        dosage_entry.bind('<Enter>', on_dosage_enter)
        dosage_entry.bind('<Button-1>', lambda e: dosage_entry.focus_set())
        
        # Frequency
        tk.Label(med_input_frame, text="Frequency:", font=('Arial', 9), bg='#f0f0f0').pack(side=tk.LEFT, padx=2)
        frequency_entry = tk.Entry(med_input_frame, font=('Arial', 9), width=10, state='normal')
        frequency_entry.pack(side=tk.LEFT, padx=2)
        frequency_entry.config(state='normal', takefocus=1)  # Ensure it can receive focus
        
        # Auto-focus on mouse enter for frequency
        def on_frequency_enter(event):
            frequency_entry.focus_set()
        frequency_entry.bind('<Enter>', on_frequency_enter)
        frequency_entry.bind('<Button-1>', lambda e: frequency_entry.focus_set())
        
        # Duration
        tk.Label(med_input_frame, text="Duration:", font=('Arial', 9), bg='#f0f0f0').pack(side=tk.LEFT, padx=2)
        duration_entry = tk.Entry(med_input_frame, font=('Arial', 9), width=10, state='normal')
        duration_entry.pack(side=tk.LEFT, padx=2)
        duration_entry.config(state='normal', takefocus=1)  # Ensure it can receive focus
        
        # Auto-focus on mouse enter for duration
        def on_duration_enter(event):
            duration_entry.focus_set()
        duration_entry.bind('<Enter>', on_duration_enter)
        duration_entry.bind('<Button-1>', lambda e: duration_entry.focus_set())
        
        def add_medicine():
            med_name = med_name_entry.get().strip()
            dosage = dosage_entry.get().strip()
            frequency = frequency_entry.get().strip()
            duration = duration_entry.get().strip()
            
            if not med_name:
                messagebox.showwarning("Warning", "Please enter medicine name")
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
            
            # Add to tree
            med_tree.insert('', tk.END, values=(med_name, dosage, frequency, duration))
            medicines.append({
                'medicine_name': med_name,
                'dosage': dosage,
                'frequency': frequency,
                'duration': duration,
                'instructions': ''
            })
            
            # Clear fields
            med_name_entry.delete(0, tk.END)
            dosage_entry.delete(0, tk.END)
            frequency_entry.delete(0, tk.END)
            duration_entry.delete(0, tk.END)
            
            # Set focus back to medicine name for next entry
            med_name_entry.focus_set()
        
        # Add Medicine button - make it more prominent
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
        add_med_btn.pack(side=tk.LEFT, padx=10)
        
        # Bind Enter key to add medicine
        def on_med_enter(event):
            add_medicine()
            return "break"
        
        med_name_entry.bind('<Return>', on_med_enter)
        dosage_entry.bind('<Return>', on_med_enter)
        frequency_entry.bind('<Return>', on_med_enter)
        duration_entry.bind('<Return>', on_med_enter)
        
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
                'diagnosis': diagnosis_text.get('1.0', tk.END).strip(),
                'notes': ''
            }
            
            if self.db.add_prescription(data, medicines):
                messagebox.showinfo("Success", "Prescription created successfully")
                # Release grab before destroying
                try:
                    dialog.grab_release()
                except:
                    pass
                dialog.destroy()
                dialog.update()
                # Return focus to main window
                root = self.parent.winfo_toplevel()
                root.focus_force()
                root.update_idletasks()
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Failed to create prescription")
        
        # Button frame - ensure it's always visible at bottom
        button_frame = tk.Frame(dialog, bg='#f0f0f0', relief=tk.RAISED, bd=2)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0, before=None)
        
        # Inner frame for button spacing
        inner_button_frame = tk.Frame(button_frame, bg='#f0f0f0')
        inner_button_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Save Prescription button - make it prominent
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
            dialog.update()
            # Return focus to main window
            root = self.parent.winfo_toplevel()
            root.focus_force()
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

