"""
Patient Management Module
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import generate_id, get_current_date
from logger import (log_button_click, log_dialog_open, log_dialog_close, 
                   log_database_operation, log_error, log_info, log_warning, log_debug)


class PatientModule:
    """Patient management interface"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        # Get root window for focus management
        self.root = parent.winfo_toplevel()
        
        self.create_ui()
        # Defer refresh to make UI appear faster
        self.parent.after(10, self.refresh_list)
    
    def create_ui(self):
        """Create user interface"""
        # Header with modern styling
        header = tk.Label(
            self.parent,
            text="Patient Management",
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
        self.search_var.trace('w', lambda *args: self.search_patients())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 11), width=30, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground='#d1d5db', highlightcolor='#6366f1')
        search_entry.pack(side=tk.LEFT, padx=8)
        
        # Add patient button with modern styling
        add_btn = tk.Button(
            top_frame,
            text="+ Add New Patient",
            command=self.add_patient,
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
        
        # Treeview for patient list
        columns = ('ID', 'Name', 'DOB', 'Gender', 'Phone', 'Email')
        
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
        
        # Configure column widths based on content - more appropriate sizes
        column_widths = {
            'ID': 150,
            'Name': 200,
            'DOB': 120,
            'Gender': 100,
            'Phone': 150,
            'Email': 220
        }
        
        # Minimum widths to ensure content is readable
        min_widths = {
            'ID': 120,
            'Name': 150,
            'DOB': 100,
            'Gender': 80,
            'Phone': 120,
            'Email': 150
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
        
        # Ensure tree can receive focus and clicks immediately after dialog closes
        self.tree.configure(takefocus=1)
        
        # Use pack layout like other modules for consistency and reliability
        # Pack horizontal scrollbar first at bottom, then treeview and vertical scrollbar
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Pack treeview and vertical scrollbar side by side
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double click (opens view mode)
        self.tree.bind('<Double-1>', self.view_patient)
        
        # Add right-click context menu for quick access
        context_menu = tk.Menu(self.parent, tearoff=0)
        context_menu.add_command(label="View Details", command=self.view_patient)
        context_menu.add_command(label="✏️ Edit Patient", command=self.edit_patient)
        context_menu.add_separator()
        context_menu.add_command(label="Delete Patient", command=self.delete_patient)
        
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
            command=self.view_patient,
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
            text="✏️ Edit Patient",
            command=self.edit_patient,
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
        # Store reference for potential focus management
        self.edit_button = edit_btn
        
        tk.Button(
            action_frame,
            text="Delete",
            command=self.delete_patient,
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
    
    def _focus_tree(self):
        """Ensure tree widget is immediately interactive for selection"""
        try:
            # Ensure root window has focus first
            self.root.focus_force()
            self.root.update_idletasks()
            self.root.update()
            
            # For Treeview, focus the widget to make it immediately interactive
            # Treeview widgets can receive clicks even without focus, but setting focus
            # ensures the widget is ready to receive events immediately
            self.tree.focus_set()
            
            # Force event processing to ensure tree is interactive
            self.root.update_idletasks()
            self.root.update()
            log_debug("Tree widget focused and ready for immediate selection")
        except Exception as e:
            log_debug(f"Could not focus tree: {e}")
    
    def refresh_list(self):
        """Refresh patient list - optimized for performance"""
        log_info("Refreshing patient list...")
        # Clear existing items efficiently
        self.tree.delete(*self.tree.get_children())
        
        # Get patients from database
        patients = self.db.get_all_patients()
        log_info(f"Retrieved {len(patients)} patients from database")
        
        # Insert items - treeview handles this efficiently
        for patient in patients:
            name = f"{patient['first_name']} {patient['last_name']}"
            self.tree.insert('', tk.END, values=(
                patient['patient_id'],
                name,
                patient['date_of_birth'],
                patient['gender'],
                patient['phone'],
                patient['email']
            ))
        log_info("Patient list refreshed successfully")
        
        # Return focus to tree after refresh for immediate selection
        self.root.after(10, self._focus_tree)
    
    def search_patients(self):
        """Search patients - optimized"""
        query = self.search_var.get()
        if not query:
            self.refresh_list()
            return
        
        # Clear existing items efficiently
        self.tree.delete(*self.tree.get_children())
        
        # Get search results
        patients = self.db.search_patients(query)
        
        # Insert items
        for patient in patients:
            name = f"{patient['first_name']} {patient['last_name']}"
            self.tree.insert('', tk.END, values=(
                patient['patient_id'],
                name,
                patient['date_of_birth'],
                patient['gender'],
                patient['phone'],
                patient['email']
            ))
    
    def get_selected_patient_id(self):
        """Get selected patient ID"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a patient")
            return None
        item = self.tree.item(selection[0])
        return item['values'][0]
    
    def add_patient(self):
        """Open add patient dialog"""
        log_button_click("Add New Patient", "PatientModule")
        self.patient_dialog(None)
    
    def view_patient(self, event=None):
        """View patient details"""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return
        
        patient = self.db.get_patient_by_id(patient_id)
        if not patient:
            messagebox.showerror("Error", "Patient not found")
            return
        
        self.patient_dialog(patient, view_only=True)
    
    def edit_patient(self):
        """Edit patient - explicitly opens in EDIT mode (not view_only)"""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return
        
        patient = self.db.get_patient_by_id(patient_id)
        if not patient:
            messagebox.showerror("Error", "Patient not found")
            return
        
        log_info(f"Editing patient: {patient_id}, data fields: {list(patient.keys())}")
        # Explicitly pass view_only=False to ensure fields are editable
        self.patient_dialog(patient, view_only=False)
    
    def delete_patient(self):
        """Delete patient"""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this patient?"):
            return
        
        # Note: In a real application, you'd want to check for related records
        # For now, we'll just show a message
        messagebox.showinfo("Info", "Delete functionality would check for related records first")
    
    def patient_dialog(self, patient=None, view_only=False):
        """Patient form dialog"""
        dialog_type = "Edit Patient" if patient else "Add New Patient"
        dialog_name = dialog_type  # Alias for use in closures
        log_dialog_open(dialog_type)
        log_info(f"Opening {dialog_type} dialog - view_only={view_only}")
        
        dialog = tk.Toplevel(self.parent)
        # Set title based on mode
        if view_only:
            dialog.title("View Patient Details")
        elif patient:
            dialog.title("Edit Patient - Editable")
        else:
            dialog.title("Add New Patient")
        dialog.geometry("600x700")
        dialog.configure(bg='#f5f7fa')
        dialog.transient(self.parent)
        
        # Make dialog modal but ensure input works
        dialog.lift()  # Bring dialog to front first
        dialog.focus_force()  # Force focus on dialog
        log_info("Dialog focus set")
        # Use grab_set_global=False to allow other windows to work
        try:
            dialog.grab_set_global(False)
            log_info("Dialog grab set (global=False)")
        except:
            dialog.grab_set()  # Fallback for older tkinter versions
            log_info("Dialog grab set (fallback)")
        
        # Form fields
        fields_frame = tk.Frame(dialog, bg='#f5f7fa')
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        entries = {}
        
        # Add mode indicator
        if view_only:
            mode_label = tk.Label(fields_frame, text="📖 VIEW MODE (Read Only)", 
                                 font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#ef4444')
            mode_label.pack(pady=5)
        elif patient:
            mode_label = tk.Label(fields_frame, text="✏️ EDIT MODE (Editable)", 
                                 font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#10b981')
            mode_label.pack(pady=5)
        
        if patient:
            patient_id = patient['patient_id']
            tk.Label(fields_frame, text=f"Patient ID: {patient_id}", font=('Segoe UI', 13, 'bold'), bg='#f5f7fa', fg='#1a237e').pack(pady=8)
        else:
            patient_id = generate_id('PAT')
            tk.Label(fields_frame, text=f"Patient ID: {patient_id}", font=('Segoe UI', 13, 'bold'), bg='#f5f7fa', fg='#1a237e').pack(pady=8)
        
        field_configs = [
            ('first_name', 'First Name', True),
            ('last_name', 'Last Name', True),
            ('date_of_birth', 'Date of Birth (YYYY-MM-DD)', True),
            ('gender', 'Gender', True),
            ('phone', 'Phone', False),
            ('email', 'Email', False),
            ('address', 'Address', False),
            ('emergency_contact', 'Emergency Contact', False),
            ('emergency_phone', 'Emergency Phone', False),
            ('blood_group', 'Blood Group', False),
            ('allergies', 'Allergies', False)
        ]
        
        for field, label, required in field_configs:
            frame = tk.Frame(fields_frame, bg='#f5f7fa')
            frame.pack(fill=tk.X, pady=10)
            
            tk.Label(frame, text=f"{label}{' *' if required else ''}:", font=('Segoe UI', 10, 'bold'), bg='#f5f7fa', fg='#374151', width=20, anchor='w').pack(side=tk.LEFT)
            
            if field == 'gender':
                # Get gender value from patient if available, otherwise empty string
                gender_value = ''
                if patient and field in patient:
                    gender_value = str(patient[field]) if patient[field] else ''
                var = tk.StringVar(value=gender_value)
                # For Combobox, use 'readonly' to allow dropdown selection but prevent typing
                # But make it 'normal' if not view_only to allow editing
                combo_state = 'readonly' if view_only else 'readonly'  # Keep readonly for dropdown
                combo = ttk.Combobox(frame, textvariable=var, values=['Male', 'Female', 'Other'], 
                                   state=combo_state, width=30)
                combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries[field] = var
            else:
                # Entry fields should be 'normal' (editable) when not in view_only mode
                # Always create in 'normal' state first, then set to readonly if needed
                entry_state = 'readonly' if view_only else 'normal'
                entry = tk.Entry(frame, font=('Segoe UI', 10), width=35, 
                               state=entry_state, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground='#d1d5db', highlightcolor='#6366f1')
                
                # Insert patient data BEFORE packing
                if patient and field in patient:
                    patient_value = patient[field]
                    if patient_value is not None:
                        # Temporarily set to normal to insert data if it's readonly
                        if entry_state == 'readonly':
                            entry.config(state='normal')
                        entry.insert(0, str(patient_value))
                        # Restore state after insertion
                        if entry_state == 'readonly':
                            entry.config(state='readonly')
                        log_debug(f"Inserted {field} = '{patient_value}' into entry field (state={entry_state})")
                    else:
                        log_debug(f"Field {field} is None in patient data")
                else:
                    if patient:
                        log_debug(f"Field {field} not found in patient data (available fields: {list(patient.keys())})")
                
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries[field] = entry
                
                # Final verification: ensure field is editable when not in view_only mode
                if not view_only:
                    current_state = entry.cget('state')
                    if current_state != 'normal':
                        log_warning(f"Field {field} state is '{current_state}', forcing to 'normal'")
                        entry.config(state='normal')
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#f5f7fa')
        button_frame.pack(fill=tk.X, padx=25, pady=25)
        
        if not view_only:
            def save_patient():
                # CRITICAL: Process events immediately when save button is clicked
                # This ensures the button click event is fully processed
                dialog.update_idletasks()
                dialog.update()
                dialog.update_idletasks()
                
                log_button_click("Save Patient", "PatientDialog")
                log_info(f"Save button clicked - attempting to save patient: {patient_id}")
                
                # Additional event processing to ensure everything is ready
                dialog.update_idletasks()
                
                data = {'patient_id': patient_id}
                for field, widget in entries.items():
                    if isinstance(widget, tk.StringVar):
                        data[field] = widget.get()
                    else:
                        data[field] = widget.get()
                
                log_info(f"Patient data collected: {list(data.keys())}")
                
                # Validation
                required_fields = ['first_name', 'last_name', 'date_of_birth', 'gender']
                for field in required_fields:
                    if not data.get(field):
                        log_warning(f"Validation failed: {field} is required")
                        messagebox.showerror("Error", f"{field.replace('_', ' ').title()} is required")
                        return
                
                log_info("Validation passed")
                
                if patient:
                    log_info(f"Updating existing patient: {patient_id}")
                    if self.db.update_patient(patient_id, data):
                        log_database_operation("UPDATE", "patients", True, f"Patient ID: {patient_id}")
                        # Release grab BEFORE destroying dialog
                        try:
                            dialog.grab_release()
                            log_debug("Dialog grab released")
                        except Exception as e:
                            log_debug(f"Error releasing grab: {e}")
                        
                        log_dialog_close("Edit Patient")
                        
                        # Destroy dialog first
                        dialog.destroy()
                        
                        # Process all pending events immediately - CRITICAL for immediate button response
                        self.root.update_idletasks()
                        self.root.update()
                        self.root.update_idletasks()
                        
                        # Return focus to main window immediately
                        self.root.focus_force()
                        self.root.update_idletasks()
                        self.root.update()
                        
                        # Ensure all events are processed and UI is ready
                        self.root.update_idletasks()
                        
                        # Final update to ensure buttons are immediately responsive
                        self.root.update()
                        self.root.update_idletasks()
                        
                        # CRITICAL: Explicitly ensure all navigation buttons are enabled
                        # Access the main app instance through root
                        try:
                            if hasattr(self.root, 'app_instance'):
                                app = self.root.app_instance
                                if hasattr(app, 'nav_buttons'):
                                    for button_name, btn in app.nav_buttons.items():
                                        if btn['state'] != tk.NORMAL:
                                            btn.config(state=tk.NORMAL)
                                    log_debug("Navigation buttons explicitly enabled after patient update")
                                    # Force one more update after enabling buttons
                                    self.root.update_idletasks()
                                    self.root.update()
                        except Exception as e:
                            log_debug(f"Could not access nav_buttons: {e}")
                        
                        # Additional event processing to ensure buttons are ready
                        self.root.update_idletasks()
                        self.root.update()
                        
                        # Focus tree immediately so user can select another patient right away
                        self._focus_tree()
                        
                        # Refresh list asynchronously (before showing messagebox to avoid focus issues)
                        self.root.after(50, self.refresh_list)
                        
                        # Show message after dialog is closed and list refreshed - delayed to not interfere
                        def show_success_and_refocus():
                            messagebox.showinfo("Success", "Patient updated successfully")
                            # Return focus to tree after messagebox closes
                            self._focus_tree()
                        self.root.after(300, show_success_and_refocus)
                        
                        log_info("Patient update process completed")
                    else:
                        log_database_operation("UPDATE", "patients", False, f"Patient ID: {patient_id}")
                        messagebox.showerror("Error", "Failed to update patient")
                else:
                    log_info(f"Adding new patient: {patient_id}")
                    if self.db.add_patient(data):
                        log_database_operation("INSERT", "patients", True, f"Patient ID: {patient_id}, Name: {data.get('first_name')} {data.get('last_name')}")
                        # Release grab BEFORE destroying dialog
                        try:
                            dialog.grab_release()
                            log_debug("Dialog grab released")
                        except Exception as e:
                            log_debug(f"Error releasing grab: {e}")
                        
                        log_dialog_close("Add New Patient")
                        
                        # Destroy dialog first
                        dialog.destroy()
                        
                        # Process all pending events immediately - CRITICAL for immediate button response
                        self.root.update_idletasks()
                        self.root.update()
                        self.root.update_idletasks()
                        
                        # Return focus to main window immediately
                        self.root.focus_force()
                        self.root.update_idletasks()
                        self.root.update()
                        
                        # Ensure all events are processed and UI is ready
                        self.root.update_idletasks()
                        
                        # Final update to ensure buttons are immediately responsive
                        self.root.update()
                        self.root.update_idletasks()
                        
                        # CRITICAL: Explicitly ensure all navigation buttons are enabled
                        # Access the main app instance through root
                        try:
                            if hasattr(self.root, 'app_instance'):
                                app = self.root.app_instance
                                if hasattr(app, 'nav_buttons'):
                                    for button_name, btn in app.nav_buttons.items():
                                        if btn['state'] != tk.NORMAL:
                                            btn.config(state=tk.NORMAL)
                                    log_debug("Navigation buttons explicitly enabled after patient add")
                                    # Force one more update after enabling buttons
                                    self.root.update_idletasks()
                                    self.root.update()
                        except Exception as e:
                            log_debug(f"Could not access nav_buttons: {e}")
                        
                        # Additional event processing to ensure buttons are ready
                        self.root.update_idletasks()
                        self.root.update()
                        
                        # Focus tree immediately so user can select another patient right away
                        self._focus_tree()
                        
                        # Refresh list asynchronously (before showing messagebox to avoid focus issues)
                        self.root.after(50, self.refresh_list)
                        
                        # Show message after dialog is closed and list refreshed - delayed to not interfere
                        def show_success_and_refocus():
                            messagebox.showinfo("Success", "Patient added successfully")
                            # Return focus to tree after messagebox closes
                            self._focus_tree()
                        self.root.after(300, show_success_and_refocus)
                        
                        log_info("Patient add process completed")
                    else:
                        log_database_operation("INSERT", "patients", False, f"Patient ID: {patient_id} - ID might already exist")
                        messagebox.showerror("Error", "Failed to add patient (ID might already exist)")
            
            # Create wrapper to ensure events are processed
            def on_save_button_click():
                """Wrapper to ensure events are processed before save"""
                log_info("Save button wrapper called - processing events")
                # Process events immediately
                dialog.update_idletasks()
                dialog.update()
                dialog.update_idletasks()
                # Call the actual save function
                save_patient()
            
            save_btn = tk.Button(
                button_frame,
                text="Save",
                command=on_save_button_click,
                font=('Segoe UI', 11, 'bold'),
                bg='#10b981',
                fg='white',
                padx=35,
                pady=10,
                cursor='hand2',
                state=tk.NORMAL,
                activebackground='#059669',
                activeforeground='white',
                relief=tk.FLAT,
                bd=0
            )
            save_btn.pack(side=tk.LEFT, padx=10)
            
            # Also bind to Button-1 event as backup to ensure it works
            def on_save_click_event(event):
                """Handle Button-1 click on save button"""
                log_info("Save button Button-1 event triggered")
                dialog.update_idletasks()
                dialog.update()
                on_save_button_click()
                return "break"  # Prevent default behavior
            
            save_btn.bind('<Button-1>', on_save_click_event)
            
            # Store save_btn reference for focus handlers
            dialog._save_btn = save_btn
        
        def close_dialog():
            log_button_click("Close Dialog", "PatientDialog")
            # Release grab BEFORE destroying
            try:
                dialog.grab_release()
                log_debug("Dialog grab released on close")
            except Exception as e:
                log_debug(f"Error releasing grab on close: {e}")
            
            log_dialog_close(dialog_name)
            
            # Destroy dialog
            dialog.destroy()
            
            # Process all pending events immediately - CRITICAL for immediate button response
            self.root.update_idletasks()
            self.root.update()
            self.root.update_idletasks()
            
            # Return focus to main window immediately
            self.root.focus_force()
            self.root.update_idletasks()
            self.root.update()
            
            # Ensure all events are processed and UI is ready
            self.root.update_idletasks()
            log_info("Dialog closed, focus returned to main window")
        
        close_btn = tk.Button(
            button_frame,
            text="Close",
            command=close_dialog,
            font=('Segoe UI', 11, 'bold'),
            bg='#6b7280',
            fg='white',
            padx=35,
            pady=10,
            cursor='hand2',
            state=tk.NORMAL,
            activebackground='#4b5563',
            activeforeground='white',
            relief=tk.FLAT,
            bd=0
        )
        close_btn.pack(side=tk.LEFT, padx=10)
        
        # Ensure everything is ready
        dialog.update_idletasks()
        
        # Make sure entry fields can receive input (they should already be in correct state)
        # This is a critical safety check to ensure fields are editable when not in view_only mode
        if not view_only:
            log_info("Ensuring all entry fields are editable (not view_only mode)")
            for field, widget in entries.items():
                if not isinstance(widget, tk.StringVar):
                    # Force state to normal for editable fields
                    current_state = widget.cget('state')
                    if current_state != 'normal':
                        log_warning(f"Field {field} was in state '{current_state}', forcing to 'normal'")
                        widget.config(state='normal')
                    # Verify it's actually normal now
                    final_state = widget.cget('state')
                    if final_state != 'normal':
                        log_error(f"Field {field} could not be set to 'normal', current state: '{final_state}'")
                    else:
                        log_debug(f"Field {field} confirmed editable (state='normal')")
                    widget.update_idletasks()
        else:
            log_info("Dialog is in view_only mode - fields should be readonly")
        
        # Set focus on first name field when adding new patient
        # Do this AFTER all widgets are created and dialog is updated
        if not patient and not view_only:
            # Find the first_name entry field
            first_name_entry = entries.get('first_name')
            if first_name_entry and not isinstance(first_name_entry, tk.StringVar):
                # Prevent other widgets from taking focus initially
                # Temporarily disable focus on other entry fields
                for field, widget in entries.items():
                    if field != 'first_name' and not isinstance(widget, tk.StringVar):
                        widget.config(takefocus=0)  # Disable focus temporarily
                
                # Set focus on dialog first to prevent other widgets from grabbing it
                dialog.focus_set()
                dialog.update_idletasks()
                
                # Use multiple attempts to ensure focus is set correctly
                def set_focus_initial():
                    # Make sure first_name entry is ready
                    first_name_entry.update_idletasks()
                    first_name_entry.focus_set()
                    first_name_entry.icursor(0)  # Set cursor at start
                    log_debug("Focus set on first_name field (initial)")
                
                def set_focus_backup():
                    # Backup focus set to ensure it sticks
                    first_name_entry.focus_set()
                    first_name_entry.icursor(0)
                    log_debug("Focus set on first_name field (backup)")
                
                def re_enable_focus():
                    # Re-enable focus on other fields after first_name has focus
                    for field, widget in entries.items():
                        if field != 'first_name' and not isinstance(widget, tk.StringVar):
                            widget.config(takefocus=1)  # Re-enable focus
                
                # Set focus after dialog is fully rendered
                dialog.after(50, set_focus_initial)
                dialog.after(150, set_focus_backup)
                dialog.after(200, re_enable_focus)
        
        # Bind Enter key to move to next field or Save
        if not view_only:
            def on_return(event):
                # Get the widget that has focus
                focused_widget = dialog.focus_get()
                
                # If focus is on an entry field, move to next field
                if isinstance(focused_widget, tk.Entry):
                    # Find current field index
                    field_list = list(entries.keys())
                    current_field = None
                    for field, widget in entries.items():
                        if widget == focused_widget:
                            current_field = field
                            break
                    
                    if current_field:
                        current_index = field_list.index(current_field)
                        # Move to next field
                        if current_index < len(field_list) - 1:
                            next_field = field_list[current_index + 1]
                            next_widget = entries[next_field]
                            if not isinstance(next_widget, tk.StringVar):
                                next_widget.focus_set()
                                return "break"  # Prevent default Enter behavior
                    
                    # If on last field or can't find next, save
                    save_patient()
                    return "break"
                else:
                    # If not on entry field, save
                    save_patient()
                    return "break"
            
            dialog.bind('<Return>', on_return)
            # Also bind to entry fields individually
            for field, widget in entries.items():
                if not isinstance(widget, tk.StringVar):
                    widget.bind('<Return>', on_return)
                    # Bind Tab to move to next field
                    def make_tab_handler(current_field):
                        def on_tab(event):
                            field_list = list(entries.keys())
                            current_index = field_list.index(current_field)
                            if current_index < len(field_list) - 1:
                                next_field = field_list[current_index + 1]
                                next_widget = entries[next_field]
                                if not isinstance(next_widget, tk.StringVar):
                                    next_widget.focus_set()
                                    return "break"
                            return None
                        return on_tab
                    widget.bind('<Tab>', make_tab_handler(field))
        
        def on_escape(event):
            log_info("Escape key pressed, closing dialog")
            try:
                dialog.grab_release()
            except:
                pass
            log_dialog_close(dialog_name)
            dialog.destroy()
            
            # Process all pending events immediately - CRITICAL for immediate button response
            self.root.update_idletasks()
            self.root.update()
            self.root.update_idletasks()
            
            # Return focus to main window immediately
            self.root.focus_force()
            self.root.update_idletasks()
            self.root.update()
            
            # Ensure all events are processed and UI is ready
            self.root.update_idletasks()
            return "break"
        dialog.bind('<Escape>', on_escape)
        
        # Ensure dialog releases grab when closed
        def on_close():
            log_info("Dialog window close (X) clicked")
            try:
                dialog.grab_release()
            except:
                pass
            log_dialog_close(dialog_name)
            dialog.destroy()
            
            # Process all pending events immediately - CRITICAL for immediate button response
            self.root.update_idletasks()
            self.root.update()
            self.root.update_idletasks()
            
            # Return focus to main window immediately
            self.root.focus_force()
            self.root.update_idletasks()
            self.root.update()
            
            # Ensure all events are processed and UI is ready
            self.root.update_idletasks()
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
        # Set up focus event handlers for dialog to ensure buttons work when dialog is active
        # Track last focus processing time to avoid excessive logging and processing
        dialog._last_focus_process = 0
        
        def on_dialog_focus_in(event):
            """Handle dialog gaining focus - process pending events"""
            import time
            current_time = time.time()
            # Only process if it's been at least 0.3 seconds since last processing
            if current_time - dialog._last_focus_process > 0.3:
                log_debug("Dialog gained focus - processing events")
                dialog._last_focus_process = current_time
                dialog.update_idletasks()
                # Ensure save button is enabled
                if not view_only and hasattr(dialog, '_save_btn'):
                    if dialog._save_btn['state'] != tk.NORMAL:
                        dialog._save_btn.config(state=tk.NORMAL)
                dialog.update_idletasks()
            return True
        
        def on_dialog_focus_out(event):
            """Handle dialog losing focus"""
            # Don't log every focus out event to reduce log spam
            return True
        
        # Bind focus events to dialog
        dialog.bind('<FocusIn>', on_dialog_focus_in)
        dialog.bind('<FocusOut>', on_dialog_focus_out)
        
        # Start periodic event processing for dialog to ensure save button always works
        def process_dialog_events_periodically():
            """Periodically process events in dialog to ensure buttons remain responsive"""
            try:
                # Check if dialog still exists
                if not dialog.winfo_exists():
                    return
                
                # Process pending idle tasks
                dialog.update_idletasks()
                
                # Ensure save button is enabled
                if not view_only and hasattr(dialog, '_save_btn'):
                    if dialog._save_btn['state'] != tk.NORMAL:
                        dialog._save_btn.config(state=tk.NORMAL)
                
                # Schedule next processing (every 300ms for dialog - more frequent than main window)
                dialog.after(300, process_dialog_events_periodically)
            except Exception as e:
                # If dialog is destroyed, stop processing
                log_debug(f"Dialog event processing stopped: {e}")
        
        # Start periodic processing after a short delay
        if not view_only:
            dialog.after(100, process_dialog_events_periodically)
            log_info("Dialog periodic event processing started")
        
        # Final update to ensure everything is interactive
        dialog.update()

