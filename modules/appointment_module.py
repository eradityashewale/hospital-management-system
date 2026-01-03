"""
Appointment Management Module
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import generate_id, get_current_date


class AppointmentModule:
    """Appointment management interface"""
    
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
            text="Appointment Management",
            font=('Segoe UI', 24, 'bold'),
            bg='#f5f7fa',
            fg='#1a237e'
        )
        header.pack(pady=20)
        
        # Top frame
        top_frame = tk.Frame(self.parent, bg='#f5f7fa')
        top_frame.pack(fill=tk.X, padx=25, pady=15)
        
        # Date filter
        filter_frame = tk.Frame(top_frame, bg='#f5f7fa')
        filter_frame.pack(side=tk.LEFT)
        
        tk.Label(filter_frame, text="Filter by Date:", font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#374151').pack(side=tk.LEFT, padx=5)
        self.date_var = tk.StringVar(value=get_current_date())
        date_entry = tk.Entry(filter_frame, textvariable=self.date_var, font=('Segoe UI', 10), width=15, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground='#d1d5db', highlightcolor='#6366f1')
        date_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            filter_frame,
            text="Filter",
            command=self.filter_by_date,
            font=('Segoe UI', 10, 'bold'),
            bg='#3b82f6',
            fg='white',
            padx=15,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#2563eb',
            activeforeground='white'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            filter_frame,
            text="Show All",
            command=self.refresh_list,
            font=('Segoe UI', 10, 'bold'),
            bg='#6b7280',
            fg='white',
            padx=15,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#4b5563',
            activeforeground='white'
        ).pack(side=tk.LEFT, padx=5)
        
        # Add appointment button with modern styling
        add_btn = tk.Button(
            top_frame,
            text="+ Schedule Appointment",
            command=self.add_appointment,
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
        columns = ('ID', 'Patient', 'Doctor', 'Date', 'Time', 'Status')
        
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
            'Patient': 200,
            'Doctor': 200,
            'Date': 150,
            'Time': 120,
            'Status': 120
        }
        
        min_widths = {
            'ID': 120,
            'Patient': 150,
            'Doctor': 150,
            'Date': 120,
            'Time': 100,
            'Status': 100
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
        
        self.tree.bind('<Double-1>', self.view_appointment)
        
        # Action buttons with modern styling
        action_frame = tk.Frame(self.parent, bg='#f5f7fa')
        action_frame.pack(fill=tk.X, padx=25, pady=15)
        
        tk.Button(
            action_frame,
            text="View Details",
            command=self.view_appointment,
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
        
        tk.Button(
            action_frame,
            text="Mark Complete",
            command=self.mark_complete,
            font=('Segoe UI', 10, 'bold'),
            bg='#10b981',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#059669',
            activeforeground='white'
        ).pack(side=tk.LEFT, padx=6)
        
        tk.Button(
            action_frame,
            text="Cancel",
            command=self.cancel_appointment,
            font=('Segoe UI', 10, 'bold'),
            bg='#ef4444',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#dc2626',
            activeforeground='white'
        ).pack(side=tk.LEFT, padx=6)
    
    def refresh_list(self):
        """Refresh appointment list"""
        self.tree.delete(*self.tree.get_children())
        
        appointments = self.db.get_all_appointments()
        for apt in appointments:
            self.tree.insert('', tk.END, values=(
                apt['appointment_id'],
                apt.get('patient_name', ''),
                apt.get('doctor_name', ''),
                apt['appointment_date'],
                apt['appointment_time'],
                apt['status']
            ))
    
    def filter_by_date(self):
        """Filter appointments by date"""
        date = self.date_var.get()
        if not date:
            return
        
        self.tree.delete(*self.tree.get_children())
        
        appointments = self.db.get_appointments_by_date(date)
        for apt in appointments:
            self.tree.insert('', tk.END, values=(
                apt['appointment_id'],
                apt.get('patient_name', ''),
                apt.get('doctor_name', ''),
                apt['appointment_date'],
                apt['appointment_time'],
                apt['status']
            ))
    
    def get_selected_appointment_id(self):
        """Get selected appointment ID"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment")
            return None
        item = self.tree.item(selection[0])
        return item['values'][0]
    
    def add_appointment(self):
        """Open add appointment dialog"""
        self.appointment_dialog(None)
    
    def view_appointment(self, event=None):
        """View appointment details"""
        appointment_id = self.get_selected_appointment_id()
        if not appointment_id:
            return
        messagebox.showinfo("Appointment", f"View details for {appointment_id}")
    
    def mark_complete(self):
        """Mark appointment as complete"""
        appointment_id = self.get_selected_appointment_id()
        if not appointment_id:
            return
        messagebox.showinfo("Info", "Mark complete functionality would update status")
        self.refresh_list()
    
    def cancel_appointment(self):
        """Cancel appointment"""
        appointment_id = self.get_selected_appointment_id()
        if not appointment_id:
            return
        if messagebox.askyesno("Confirm", "Cancel this appointment?"):
            messagebox.showinfo("Info", "Cancel functionality would update status")
            self.refresh_list()
    
    def appointment_dialog(self, appointment=None):
        """Appointment form dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Schedule Appointment" if not appointment else "Edit Appointment")
        dialog.geometry("550x550")  # Increased height to ensure buttons are visible
        dialog.configure(bg='#f5f7fa')
        dialog.transient(self.parent)
        
        # Get root window for focus management
        root = self.parent.winfo_toplevel()
        
        # Make dialog modal but ensure input works
        dialog.lift()
        dialog.focus_force()
        # Use grab_set_global=False to allow other windows to work
        try:
            dialog.grab_set_global(False)
        except:
            dialog.grab_set()  # Fallback for older tkinter versions
        
        # Button frame - pack first at bottom to ensure visibility
        button_frame = tk.Frame(dialog, bg='#f5f7fa', relief=tk.FLAT, bd=0)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)
        
        # Inner frame for button spacing
        inner_button_frame = tk.Frame(button_frame, bg='#f5f7fa')
        inner_button_frame.pack(padx=25, pady=20)
        
        # Main content frame - pack after button frame
        main_frame = tk.Frame(dialog, bg='#f5f7fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        fields_frame = tk.Frame(main_frame, bg='#f5f7fa')
        fields_frame.pack(fill=tk.X, expand=False, pady=10)
        
        if appointment:
            appointment_id = appointment['appointment_id']
        else:
            appointment_id = generate_id('APT')
        
        tk.Label(fields_frame, text=f"Appointment ID: {appointment_id}", font=('Segoe UI', 13, 'bold'), bg='#f5f7fa', fg='#1a237e').pack(pady=8)
        
        # Patient selection with searchable dropdown
        tk.Label(fields_frame, text="Patient ID *:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        
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
            fields_frame, 
            textvariable=patient_var,
            values=patient_options,
            font=('Arial', 10),
            width=37,
            state='normal'  # 'normal' allows typing to search
        )
        patient_combo.pack(fill=tk.X, pady=5)
        
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
        tk.Label(fields_frame, text="Doctor ID *:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        
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
            fields_frame,
            textvariable=doctor_var,
            values=doctor_options,
            font=('Arial', 10),
            width=37,
            state='normal'  # 'normal' allows typing to search
        )
        doctor_combo.pack(fill=tk.X, pady=5)
        
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
        
        # Date
        tk.Label(fields_frame, text="Date (YYYY-MM-DD) *:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        date_entry = tk.Entry(fields_frame, font=('Arial', 10), width=40)
        date_entry.insert(0, get_current_date())
        date_entry.pack(fill=tk.X, pady=5)
        
        # Time
        tk.Label(fields_frame, text="Time (HH:MM) *:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        time_entry = tk.Entry(fields_frame, font=('Arial', 10), width=40)
        time_entry.pack(fill=tk.X, pady=5)
        
        # Notes
        tk.Label(fields_frame, text="Notes:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        notes_text = tk.Text(fields_frame, font=('Arial', 10), width=40, height=4)
        notes_text.pack(fill=tk.X, pady=5)
        
        def save_appointment():
            # Get selected patient and doctor IDs from combobox
            patient_display = patient_var.get()
            doctor_display = doctor_var.get()
            
            # Extract IDs from display text
            patient_id_value = patient_id_map.get(patient_display, '')
            doctor_id_value = doctor_id_map.get(doctor_display, '')
            
            # If not found in map, try to extract from display text directly (fallback)
            if not patient_id_value and patient_display:
                # Try to extract ID if user typed it directly (format: "PAT-XXX - Name")
                parts = patient_display.split(' - ')
                if parts:
                    patient_id_value = parts[0].strip()
            
            if not doctor_id_value and doctor_display:
                # Try to extract ID if user typed it directly (format: "DOC-XXX - Name")
                parts = doctor_display.split(' - ')
                if parts:
                    doctor_id_value = parts[0].strip()
            
            data = {
                'appointment_id': appointment_id,
                'patient_id': patient_id_value,
                'doctor_id': doctor_id_value,
                'appointment_date': date_entry.get(),
                'appointment_time': time_entry.get(),
                'notes': notes_text.get('1.0', tk.END).strip()
            }
            
            if not all([data['patient_id'], data['doctor_id'], data['appointment_date'], data['appointment_time']]):
                messagebox.showerror("Error", "Please fill all required fields")
                return
            
            # Verify patient and doctor exist
            if not self.db.get_patient_by_id(data['patient_id']):
                messagebox.showerror("Error", "Patient not found")
                return
            
            if not self.db.get_doctor_by_id(data['doctor_id']):
                messagebox.showerror("Error", "Doctor not found")
                return
            
            if self.db.add_appointment(data):
                # Release grab BEFORE destroying dialog
                try:
                    dialog.grab_release()
                except:
                    pass
                
                dialog.destroy()
                
                # Process all pending events immediately - CRITICAL for immediate button response
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
                root.after(150, lambda: messagebox.showinfo("Success", "Appointment scheduled successfully"))
                # Refresh list asynchronously
                root.after(250, self.refresh_list)
            else:
                messagebox.showerror("Error", "Failed to schedule appointment")
        
        # Schedule Appointment button - primary action
        schedule_btn = tk.Button(
            inner_button_frame,
            text="Schedule Appointment",
            command=save_appointment,
            font=('Segoe UI', 12, 'bold'),
            bg='#10b981',
            fg='white',
            padx=40,
            pady=12,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#059669',
            activeforeground='white'
        )
        schedule_btn.pack(side=tk.LEFT, padx=10)
        
        def close_dialog():
            # Release grab BEFORE destroying
            try:
                dialog.grab_release()
            except:
                pass
            
            dialog.destroy()
            
            # Process all pending events immediately - CRITICAL for immediate button response
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
            font=('Segoe UI', 11, 'bold'),
            bg='#6b7280',
            fg='white',
            padx=35,
            pady=12,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#4b5563',
            activeforeground='white'
        )
        close_btn.pack(side=tk.LEFT, padx=10)
        
        # Ensure dialog releases grab when closed via window close button
        def on_close():
            try:
                dialog.grab_release()
            except:
                pass
            dialog.destroy()
            
            # Process all pending events immediately
            root.update_idletasks()
            root.update()
            root.update_idletasks()
            
            root.focus_force()
            root.update_idletasks()
            root.update()
            root.update_idletasks()
        dialog.protocol("WM_DELETE_WINDOW", on_close)

