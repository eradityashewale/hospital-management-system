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
        # Header with modern styling
        header = tk.Label(
            self.parent,
            text="Doctor Management",
            font=('Segoe UI', 24, 'bold'),
            bg='#f5f7fa',
            fg='#1a237e'
        )
        header.pack(pady=20)
        
        # Top frame
        top_frame = tk.Frame(self.parent, bg='#f5f7fa')
        top_frame.pack(fill=tk.X, padx=25, pady=15)
        
        # Add doctor button with modern styling
        add_btn = tk.Button(
            top_frame,
            text="+ Add New Doctor",
            command=self.add_doctor,
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
        columns = ('ID', 'Name', 'Specialization', 'Qualification', 'Phone', 'Fee')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure style for modern look
        style = ttk.Style()
        style.configure("Treeview", font=('Segoe UI', 10), rowheight=30, background='white', foreground='#374151')
        style.configure("Treeview.Heading", font=('Segoe UI', 11, 'bold'), background='#6366f1', foreground='white')
        style.map("Treeview.Heading", background=[('active', '#4f46e5')])
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<Double-1>', self.view_doctor)
        
        # Action buttons with modern styling
        action_frame = tk.Frame(self.parent, bg='#f5f7fa')
        action_frame.pack(fill=tk.X, padx=25, pady=15)
        
        tk.Button(
            action_frame,
            text="View Details",
            command=self.view_doctor,
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
            text="Edit",
            command=self.edit_doctor,
            font=('Segoe UI', 10, 'bold'),
            bg='#f59e0b',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#d97706',
            activeforeground='white'
        ).pack(side=tk.LEFT, padx=6)
    
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
        
        fields_frame = tk.Frame(dialog, bg='#f5f7fa')
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        entries = {}
        
        if doctor:
            doctor_id = doctor['doctor_id']
            tk.Label(fields_frame, text=f"Doctor ID: {doctor_id}", font=('Segoe UI', 13, 'bold'), bg='#f5f7fa', fg='#1a237e').pack(pady=8)
        else:
            doctor_id = generate_id('DOC')
            tk.Label(fields_frame, text=f"Doctor ID: {doctor_id}", font=('Segoe UI', 13, 'bold'), bg='#f5f7fa', fg='#1a237e').pack(pady=8)
        
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
            frame = tk.Frame(fields_frame, bg='#f5f7fa')
            frame.pack(fill=tk.X, pady=10)
            
            tk.Label(frame, text=f"{label}{' *' if required else ''}:", font=('Segoe UI', 10, 'bold'), bg='#f5f7fa', fg='#374151', width=20, anchor='w').pack(side=tk.LEFT)
            
            entry = tk.Entry(frame, font=('Segoe UI', 10), width=35, state='readonly' if view_only else 'normal', relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground='#d1d5db', highlightcolor='#6366f1')
            if doctor:
                entry.insert(0, str(doctor.get(field, '')))
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            entries[field] = entry
        
        if not view_only:
            button_frame = tk.Frame(dialog, bg='#f5f7fa')
            button_frame.pack(fill=tk.X, padx=25, pady=25)
            
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
                        root.after(150, lambda: messagebox.showinfo("Success", "Doctor added successfully"))
                        # Refresh list asynchronously
                        root.after(250, self.refresh_list)
                    else:
                        messagebox.showerror("Error", "Failed to add doctor (ID might already exist)")
            
            tk.Button(
                button_frame,
                text="Save",
                command=save_doctor,
                font=('Segoe UI', 11, 'bold'),
                bg='#10b981',
                fg='white',
                padx=35,
                pady=10,
                cursor='hand2',
                relief=tk.FLAT,
                bd=0,
                activebackground='#059669',
                activeforeground='white'
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
                font=('Segoe UI', 11, 'bold'),
                bg='#6b7280',
                fg='white',
                padx=35,
                pady=10,
                cursor='hand2',
                relief=tk.FLAT,
                bd=0,
                activebackground='#4b5563',
                activeforeground='white'
            ).pack(side=tk.LEFT, padx=10)
        else:
            def close_dialog():
                # Release grab BEFORE destroying
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
            
            tk.Button(
                fields_frame,
                text="Close",
                command=close_dialog,
                font=('Segoe UI', 11, 'bold'),
                bg='#6b7280',
                fg='white',
                padx=35,
                pady=10,
                cursor='hand2',
                relief=tk.FLAT,
                bd=0,
                activebackground='#4b5563',
                activeforeground='white'
            ).pack(pady=10)
        
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

