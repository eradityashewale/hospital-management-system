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
        # Header
        header = tk.Label(
            self.parent,
            text="Patient Management",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        header.pack(pady=10)
        
        # Top frame for search and add button
        top_frame = tk.Frame(self.parent, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Search frame
        search_frame = tk.Frame(top_frame, bg='#f0f0f0')
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(search_frame, text="Search:", font=('Arial', 10), bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_patients())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Arial', 11), width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Add patient button
        add_btn = tk.Button(
            top_frame,
            text="+ Add New Patient",
            command=self.add_patient,
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='black',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        add_btn.pack(side=tk.RIGHT, padx=10)
        
        # List frame
        list_frame = tk.Frame(self.parent, bg='#f0f0f0')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview for patient list
        columns = ('ID', 'Name', 'DOB', 'Gender', 'Phone', 'Email')
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
        
        # Ensure tree can receive focus and clicks immediately after dialog closes
        self.tree.configure(takefocus=1)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double click
        self.tree.bind('<Double-1>', self.view_patient)
        
        # Action buttons
        action_frame = tk.Frame(self.parent, bg='#f0f0f0')
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(
            action_frame,
            text="View Details",
            command=self.view_patient,
            font=('Arial', 10),
            bg='#3498db',
            fg='black',
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="Edit",
            command=self.edit_patient,
            font=('Arial', 10),
            bg='#f39c12',
            fg='black',
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="Delete",
            command=self.delete_patient,
            font=('Arial', 10),
            bg='#e74c3c',
            fg='black',
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
    
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
        """Edit patient"""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return
        
        patient = self.db.get_patient_by_id(patient_id)
        if not patient:
            messagebox.showerror("Error", "Patient not found")
            return
        
        self.patient_dialog(patient)
    
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
        log_info(f"Opening {dialog_type} dialog")
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Patient Details" if patient else "Add New Patient")
        dialog.geometry("600x700")
        dialog.configure(bg='#f0f0f0')
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
        fields_frame = tk.Frame(dialog, bg='#f0f0f0')
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        entries = {}
        
        if patient:
            patient_id = patient['patient_id']
            tk.Label(fields_frame, text=f"Patient ID: {patient_id}", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=5)
        else:
            patient_id = generate_id('PAT')
            tk.Label(fields_frame, text=f"Patient ID: {patient_id}", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=5)
        
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
            frame = tk.Frame(fields_frame, bg='#f0f0f0')
            frame.pack(fill=tk.X, pady=8)
            
            tk.Label(frame, text=f"{label}{' *' if required else ''}:", font=('Arial', 10), bg='#f0f0f0', width=20, anchor='w').pack(side=tk.LEFT)
            
            if field == 'gender':
                var = tk.StringVar(value=patient[field] if patient else '')
                # For Combobox, use 'readonly' to allow dropdown selection but prevent typing
                combo = ttk.Combobox(frame, textvariable=var, values=['Male', 'Female', 'Other'], 
                                   state='readonly', width=30)
                combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries[field] = var
            else:
                # Entry fields should be 'normal' (editable) when not in view_only mode
                entry_state = 'normal' if not view_only else 'readonly'
                entry = tk.Entry(frame, font=('Arial', 10), width=35, 
                               state=entry_state)
                
                # Ensure entry is enabled and can receive focus
                if not view_only:
                    entry.config(state='normal')
                
                if patient:
                    entry.insert(0, str(patient.get(field, '')))
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries[field] = entry
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
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
                font=('Arial', 11, 'bold'),
                bg='#27ae60',
                fg='black',
                padx=30,
                pady=8,
                cursor='hand2',
                state=tk.NORMAL,
                activebackground='#229954',
                activeforeground='white',
                relief=tk.RAISED,
                bd=2
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
        
        # Ensure everything is ready
        dialog.update_idletasks()
        
        # Make sure entry fields can receive input
        if not view_only:
            for field, widget in entries.items():
                if not isinstance(widget, tk.StringVar):
                    widget.config(state='normal')
                    widget.update_idletasks()
        
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

