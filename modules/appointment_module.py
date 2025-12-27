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
        # Header
        header = tk.Label(
            self.parent,
            text="Appointment Management",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        header.pack(pady=10)
        
        # Top frame
        top_frame = tk.Frame(self.parent, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Date filter
        filter_frame = tk.Frame(top_frame, bg='#f0f0f0')
        filter_frame.pack(side=tk.LEFT)
        
        tk.Label(filter_frame, text="Filter by Date:", font=('Arial', 10), bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        self.date_var = tk.StringVar(value=get_current_date())
        date_entry = tk.Entry(filter_frame, textvariable=self.date_var, font=('Arial', 10), width=15)
        date_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            filter_frame,
            text="Filter",
            command=self.filter_by_date,
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            padx=10,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            filter_frame,
            text="Show All",
            command=self.refresh_list,
            font=('Arial', 10),
            bg='#95a5a6',
            fg='white',
            padx=10,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        # Add appointment button
        add_btn = tk.Button(
            top_frame,
            text="+ Schedule Appointment",
            command=self.add_appointment,
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
        columns = ('ID', 'Patient', 'Doctor', 'Date', 'Time', 'Status')
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
        
        self.tree.bind('<Double-1>', self.view_appointment)
        
        # Action buttons
        action_frame = tk.Frame(self.parent, bg='#f0f0f0')
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(
            action_frame,
            text="View Details",
            command=self.view_appointment,
            font=('Arial', 10),
            bg='#3498db',
            fg='black',
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="Mark Complete",
            command=self.mark_complete,
            font=('Arial', 10),
            bg='#2ecc71',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="Cancel",
            command=self.cancel_appointment,
            font=('Arial', 10),
            bg='#e74c3c',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
    
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
        dialog.geometry("500x400")
        dialog.configure(bg='#f0f0f0')
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
        
        fields_frame = tk.Frame(dialog, bg='#f0f0f0')
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        if appointment:
            appointment_id = appointment['appointment_id']
        else:
            appointment_id = generate_id('APT')
        
        tk.Label(fields_frame, text=f"Appointment ID: {appointment_id}", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=5)
        
        # Patient selection
        tk.Label(fields_frame, text="Patient ID *:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        patient_entry = tk.Entry(fields_frame, font=('Arial', 10), width=40)
        patient_entry.pack(fill=tk.X, pady=5)
        
        # Doctor selection
        tk.Label(fields_frame, text="Doctor ID *:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        doctor_entry = tk.Entry(fields_frame, font=('Arial', 10), width=40)
        doctor_entry.pack(fill=tk.X, pady=5)
        
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
            data = {
                'appointment_id': appointment_id,
                'patient_id': patient_entry.get(),
                'doctor_id': doctor_entry.get(),
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
        
        button_frame = tk.Frame(dialog, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(
            button_frame,
            text="Save",
            command=save_appointment,
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='black',
            padx=30,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
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
        
        tk.Button(
            button_frame,
            text="Close",
            command=close_dialog,
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            padx=30,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
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

