"""
Doctor Management Module
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import generate_id


class DoctorModule:
    """Doctor management interface"""
    
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
            text="Doctor Management",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        header.pack(pady=10)
        
        # Top frame
        top_frame = tk.Frame(self.parent, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add doctor button
        add_btn = tk.Button(
            top_frame,
            text="+ Add New Doctor",
            command=self.add_doctor,
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
        columns = ('ID', 'Name', 'Specialization', 'Qualification', 'Phone', 'Fee')
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
        
        self.tree.bind('<Double-1>', self.view_doctor)
        
        # Action buttons
        action_frame = tk.Frame(self.parent, bg='#f0f0f0')
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(
            action_frame,
            text="View Details",
            command=self.view_doctor,
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="Edit",
            command=self.edit_doctor,
            font=('Arial', 10),
            bg='#f39c12',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
    
    def refresh_list(self):
        """Refresh doctor list"""
        self.tree.delete(*self.tree.get_children())
        
        doctors = self.db.get_all_doctors()
        for doctor in doctors:
            name = f"{doctor['first_name']} {doctor['last_name']}"
            self.tree.insert('', tk.END, values=(
                doctor['doctor_id'],
                name,
                doctor['specialization'],
                doctor.get('qualification', ''),
                doctor.get('phone', ''),
                f"${doctor.get('consultation_fee', 0):.2f}"
            ))
    
    def get_selected_doctor_id(self):
        """Get selected doctor ID"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a doctor")
            return None
        item = self.tree.item(selection[0])
        return item['values'][0]
    
    def add_doctor(self):
        """Open add doctor dialog"""
        self.doctor_dialog(None)
    
    def view_doctor(self, event=None):
        """View doctor details"""
        doctor_id = self.get_selected_doctor_id()
        if not doctor_id:
            return
        
        doctor = self.db.get_doctor_by_id(doctor_id)
        if not doctor:
            messagebox.showerror("Error", "Doctor not found")
            return
        
        self.doctor_dialog(doctor, view_only=True)
    
    def edit_doctor(self):
        """Edit doctor"""
        doctor_id = self.get_selected_doctor_id()
        if not doctor_id:
            return
        
        doctor = self.db.get_doctor_by_id(doctor_id)
        if not doctor:
            messagebox.showerror("Error", "Doctor not found")
            return
        
        self.doctor_dialog(doctor)
    
    def doctor_dialog(self, doctor=None, view_only=False):
        """Doctor form dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Doctor Details" if doctor else "Add New Doctor")
        dialog.geometry("600x600")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.parent)
        dialog.grab_set()
        
        fields_frame = tk.Frame(dialog, bg='#f0f0f0')
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        entries = {}
        
        if doctor:
            doctor_id = doctor['doctor_id']
            tk.Label(fields_frame, text=f"Doctor ID: {doctor_id}", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=5)
        else:
            doctor_id = generate_id('DOC')
            tk.Label(fields_frame, text=f"Doctor ID: {doctor_id}", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=5)
        
        field_configs = [
            ('first_name', 'First Name', True),
            ('last_name', 'Last Name', True),
            ('specialization', 'Specialization', True),
            ('qualification', 'Qualification', False),
            ('phone', 'Phone', False),
            ('email', 'Email', False),
            ('address', 'Address', False),
            ('consultation_fee', 'Consultation Fee', False),
            ('available_days', 'Available Days', False),
            ('available_time', 'Available Time', False)
        ]
        
        for field, label, required in field_configs:
            frame = tk.Frame(fields_frame, bg='#f0f0f0')
            frame.pack(fill=tk.X, pady=8)
            
            tk.Label(frame, text=f"{label}{' *' if required else ''}:", font=('Arial', 10), bg='#f0f0f0', width=20, anchor='w').pack(side=tk.LEFT)
            
            entry = tk.Entry(frame, font=('Arial', 10), width=35, state='readonly' if view_only else 'normal')
            if doctor:
                entry.insert(0, str(doctor.get(field, '')))
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            entries[field] = entry
        
        if not view_only:
            button_frame = tk.Frame(dialog, bg='#f0f0f0')
            button_frame.pack(fill=tk.X, padx=20, pady=20)
            
            def save_doctor():
                data = {'doctor_id': doctor_id}
                for field, widget in entries.items():
                    value = widget.get()
                    if field == 'consultation_fee':
                        try:
                            data[field] = float(value) if value else 0
                        except:
                            data[field] = 0
                    else:
                        data[field] = value
                
                required_fields = ['first_name', 'last_name', 'specialization']
                for field in required_fields:
                    if not data.get(field):
                        messagebox.showerror("Error", f"{field.replace('_', ' ').title()} is required")
                        return
                
                if doctor:
                    messagebox.showinfo("Info", "Update functionality would be implemented here")
                else:
                    if self.db.add_doctor(data):
                        messagebox.showinfo("Success", "Doctor added successfully")
                        dialog.destroy()
                        self.refresh_list()
                    else:
                        messagebox.showerror("Error", "Failed to add doctor (ID might already exist)")
            
            tk.Button(
                button_frame,
                text="Save",
                command=save_doctor,
                font=('Arial', 11, 'bold'),
                bg='#27ae60',
                fg='white',
                padx=30,
                pady=8,
                cursor='hand2'
            ).pack(side=tk.LEFT, padx=10)
            
            tk.Button(
                button_frame,
                text="Close",
                command=dialog.destroy,
                font=('Arial', 11),
                bg='#95a5a6',
                fg='white',
                padx=30,
                pady=8,
                cursor='hand2'
            ).pack(side=tk.LEFT, padx=10)
        else:
            tk.Button(
                fields_frame,
                text="Close",
                command=dialog.destroy,
                font=('Arial', 11),
                bg='#95a5a6',
                fg='white',
                padx=30,
                pady=8,
                cursor='hand2'
            ).pack(pady=10)

