"""
Doctor Management Module
"""
import tkinter as tk
from tkinter import ttk, messagebox

# Backend imports
from backend.database import Database

# Utils imports
from utils.helpers import generate_id


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
        
        # Top frame for search and add button
        top_frame = tk.Frame(self.parent, bg='#f5f7fa')
        top_frame.pack(fill=tk.X, padx=25, pady=15)
        
        # Search frame
        search_frame = tk.Frame(top_frame, bg='#f5f7fa')
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(search_frame, text="Search:", font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#374151').pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_doctors())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 11), width=30, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground='#d1d5db', highlightcolor='#6366f1')
        search_entry.pack(side=tk.LEFT, padx=8)
        
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
        
        # Container for list and buttons to ensure both are visible
        content_container = tk.Frame(self.parent, bg='#f5f7fa')
        content_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)
        
        # List frame - fixed height to ensure buttons are visible
        list_frame = tk.Frame(content_container, bg='#f5f7fa')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview
        columns = ('ID', 'Name', 'Specialization', 'Qualification', 'Phone', 'Fee')
        
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
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
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
        
        # Configure column widths based on content - wider sizes for readability
        column_widths = {
            'ID': 150,
            'Name': 200,
            'Specialization': 180,
            'Qualification': 150,
            'Phone': 150,
            'Fee': 120
        }
        
        # Minimum widths to ensure content is readable
        min_widths = {
            'ID': 120,
            'Name': 150,
            'Specialization': 130,
            'Qualification': 100,
            'Phone': 120,
            'Fee': 80
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = column_widths.get(col, 150)
            minwidth = min_widths.get(col, 100)
            # All columns should stretch to fill available space, but respect minimum width
            # This ensures columns are always visible and readable
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
        
        self.tree.bind('<Double-1>', self.view_doctor)
        
        # Add right-click context menu for quick access
        context_menu = tk.Menu(self.parent, tearoff=0)
        context_menu.add_command(label="View Details", command=self.view_doctor)
        context_menu.add_command(label="✏️ Edit Doctor", command=self.edit_doctor)
        context_menu.add_separator()
        context_menu.add_command(label="Delete Doctor", command=self.delete_doctor)
        
        def show_context_menu(event):
            """Show context menu on right-click"""
            try:
                # Select the item under cursor if not already selected
                item = self.tree.identify_row(event.y)
                if item:
                    self.tree.selection_set(item)
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        self.tree.bind('<Button-3>', show_context_menu)  # Right-click on Windows
        self.tree.bind('<Button-2>', show_context_menu)  # Right-click on Mac/Linux
        
        # Action buttons with modern styling - placed in container AFTER list frame so always visible
        action_frame = tk.Frame(content_container, bg='#f5f7fa')
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
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
        
        edit_btn = tk.Button(
            action_frame,
            text="✏️ Edit Doctor",
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
        )
        edit_btn.pack(side=tk.LEFT, padx=6)
        # Store reference
        self.edit_button = edit_btn
        
        tk.Button(
            action_frame,
            text="Delete",
            command=self.delete_doctor,
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
    
    def search_doctors(self):
        """Search doctors"""
        query = self.search_var.get()
        if not query:
            self.refresh_list()
            return
        
        # Clear existing items
        self.tree.delete(*self.tree.get_children())
        
        # Get all doctors and filter
        doctors = self.db.get_all_doctors()
        for doctor in doctors:
            name = f"{doctor['first_name']} {doctor['last_name']}"
            # Search in name, ID, specialization, qualification, phone
            search_text = f"{doctor['doctor_id']} {name} {doctor['specialization']} {doctor.get('qualification', '')} {doctor.get('phone', '')}".lower()
            if query.lower() in search_text:
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
        """Edit doctor - explicitly opens in EDIT mode (not view_only)"""
        doctor_id = self.get_selected_doctor_id()
        if not doctor_id:
            return
        
        doctor = self.db.get_doctor_by_id(doctor_id)
        if not doctor:
            messagebox.showerror("Error", "Doctor not found")
            return
        
        # Explicitly pass view_only=False to ensure fields are editable
        self.doctor_dialog(doctor, view_only=False)
    
    def delete_doctor(self):
        """Delete doctor"""
        doctor_id = self.get_selected_doctor_id()
        if not doctor_id:
            return
        
        # Get doctor name for confirmation message
        doctor = self.db.get_doctor_by_id(doctor_id)
        if not doctor:
            messagebox.showerror("Error", "Doctor not found")
            return
        
        doctor_name = f"{doctor.get('first_name', '')} {doctor.get('last_name', '')}".strip()
        if not doctor_name:
            doctor_name = doctor_id
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete doctor '{doctor_name}' (ID: {doctor_id})?\n\nThis action cannot be undone."):
            return
        
        # Check for related records (appointments, prescriptions)
        # Note: In a real application, you'd want to check for related records
        # For now, we'll proceed with deletion
        
        if self.db.delete_doctor(doctor_id):
            messagebox.showinfo("Success", f"Doctor '{doctor_name}' deleted successfully")
            self.refresh_list()
        else:
            messagebox.showerror("Error", "Failed to delete doctor. There may be related records (appointments, prescriptions) that need to be handled first.")
    
    def doctor_dialog(self, doctor=None, view_only=False):
        """Doctor form dialog"""
        dialog = tk.Toplevel(self.parent)
        # Set title based on mode
        if view_only:
            dialog.title("View Doctor Details")
        elif doctor:
            dialog.title("Edit Doctor - Editable")
        else:
            dialog.title("Add New Doctor")
        dialog.geometry("600x700")
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
        
        # Main container for all content
        main_container = tk.Frame(dialog, bg='#f5f7fa')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Fields frame - will expand but leave room for buttons at bottom
        fields_frame = tk.Frame(main_container, bg='#f5f7fa')
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=(25, 0))
        
        entries = {}
        
        # Add mode indicator
        if view_only:
            mode_label = tk.Label(fields_frame, text="📖 VIEW MODE (Read Only)", 
                                 font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#ef4444')
            mode_label.pack(pady=5)
        elif doctor:
            mode_label = tk.Label(fields_frame, text="✏️ EDIT MODE (Editable)", 
                                 font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#10b981')
            mode_label.pack(pady=5)
        
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
            
            # Entry fields should be 'normal' (editable) when not in view_only mode
            entry_state = 'readonly' if view_only else 'normal'
            entry = tk.Entry(frame, font=('Segoe UI', 10), width=35, 
                           state=entry_state, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground='#d1d5db', highlightcolor='#6366f1')
            
            # Insert doctor data BEFORE packing
            if doctor and field in doctor:
                doctor_value = doctor[field]
                if doctor_value is not None:
                    # Temporarily set to normal to insert data if it's readonly
                    if entry_state == 'readonly':
                        entry.config(state='normal')
                    entry.insert(0, str(doctor_value))
                    # Restore state after insertion
                    if entry_state == 'readonly':
                        entry.config(state='readonly')
            
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            entries[field] = entry
            
            # Final verification: ensure field is editable when not in view_only mode
            if not view_only:
                current_state = entry.cget('state')
                if current_state != 'normal':
                    entry.config(state='normal')
        
        if not view_only:
            # Button frame at bottom - always visible
            button_frame = tk.Frame(main_container, bg='#f5f7fa')
            button_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=25, pady=(0, 25))
            
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
                    # Update existing doctor
                    if self.db.update_doctor(doctor_id, data):
                        # Release grab BEFORE destroying dialog
                        try:
                            dialog.grab_release()
                        except:
                            pass
                        
                        dialog.destroy()
                        
                        # Process all pending events immediately
                        root.update_idletasks()
                        root.update()
                        root.update_idletasks()
                        
                        # Return focus to main window
                        root.focus_force()
                        root.update_idletasks()
                        root.update()
                        root.update_idletasks()
                        
                        # Show message after dialog is closed
                        root.after(150, lambda: messagebox.showinfo("Success", "Doctor updated successfully"))
                        # Refresh list asynchronously
                        root.after(250, self.refresh_list)
                    else:
                        messagebox.showerror("Error", "Failed to update doctor")
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

