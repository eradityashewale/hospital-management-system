"""
Prescription Management Module
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime

# Backend imports
from backend.database import Database

# Utils imports
from utils.helpers import generate_id, get_current_date


class PrescriptionModule:
    """Prescription management interface"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        
        self.create_ui()
        # Defer refresh to make UI appear faster
        self.parent.after(10, self.apply_filters)
    
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
        
        # Filter frame
        filter_frame = tk.Frame(top_frame, bg='#f5f7fa')
        filter_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Search by patient name
        tk.Label(filter_frame, text="Search by Patient Name:", font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#374151').pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.apply_filters())
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var, font=('Segoe UI', 10), width=20, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground='#d1d5db', highlightcolor='#6366f1')
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Date filter with calendar button
        tk.Label(filter_frame, text="Filter by Date:", font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#374151').pack(side=tk.LEFT, padx=(15, 5))
        date_filter_frame = tk.Frame(filter_frame, bg='#f5f7fa')
        date_filter_frame.pack(side=tk.LEFT, padx=5)
        self.date_var = tk.StringVar(value="")
        date_entry = tk.Entry(date_filter_frame, textvariable=self.date_var, font=('Segoe UI', 10), width=15, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground='#d1d5db', highlightcolor='#6366f1')
        date_entry.pack(side=tk.LEFT)
        # Auto-filter when date changes
        self.date_var.trace('w', lambda *args: self.apply_filters())
        
        def open_calendar_for_filter():
            """Open calendar for date filter"""
            calendar_window = tk.Toplevel(self.parent)
            calendar_window.title("Select Date")
            calendar_window.geometry("300x280")
            calendar_window.configure(bg='#ffffff')
            calendar_window.transient(self.parent)
            calendar_window.grab_set()
            
            # Position calendar below the date filter button
            calendar_window.update_idletasks()
            # Get the position of the date filter frame
            date_filter_frame.update_idletasks()
            root_x = self.parent.winfo_rootx()
            root_y = self.parent.winfo_rooty()
            frame_x = date_filter_frame.winfo_x()
            frame_y = date_filter_frame.winfo_y()
            frame_width = date_filter_frame.winfo_width()
            frame_height = date_filter_frame.winfo_height()
            
            # Position below the date filter frame
            x = root_x + frame_x
            y = root_y + frame_y + frame_height + 5  # 5 pixels below
            
            # Make sure calendar doesn't go off screen
            screen_width = calendar_window.winfo_screenwidth()
            screen_height = calendar_window.winfo_screenheight()
            if x + 300 > screen_width:
                x = screen_width - 300 - 10
            if y + 280 > screen_height:
                y = root_y + frame_y - 280 - 5  # Show above if no space below
            
            calendar_window.geometry(f"300x280+{x}+{y}")
            
            # Header
            header_frame = tk.Frame(calendar_window, bg='#1e40af', height=40)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            tk.Label(
                header_frame,
                text="Select Date",
                font=('Segoe UI', 12, 'bold'),
                bg='#1e40af',
                fg='white'
            ).pack(pady=10)
            
            # Calendar frame
            cal_frame = tk.Frame(calendar_window, bg='#ffffff')
            cal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Get current date from entry or use today
            current_date_str = self.date_var.get()
            try:
                current_date = datetime.strptime(current_date_str, '%Y-%m-%d')
            except:
                current_date = datetime.now()
            
            # Variables for month and year
            month_var = tk.IntVar(value=current_date.month)
            year_var = tk.IntVar(value=current_date.year)
            
            # Month and year navigation
            nav_frame = tk.Frame(cal_frame, bg='#ffffff')
            nav_frame.pack(fill=tk.X, pady=(0, 10))
            
            def update_calendar():
                """Update calendar display"""
                # Clear existing calendar
                for widget in cal_days_frame.winfo_children():
                    widget.destroy()
                
                month = month_var.get()
                year = year_var.get()
                
                # Update month/year label
                month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                             'July', 'August', 'September', 'October', 'November', 'December']
                month_label.config(text=f"{month_names[month-1]} {year}")
                
                # Get first day of month and number of days
                first_day = datetime(year, month, 1)
                first_weekday = first_day.weekday()  # 0 = Monday, 6 = Sunday
                
                # Adjust to Sunday = 0
                first_weekday = (first_weekday + 1) % 7
                
                # Get number of days in month
                if month == 12:
                    next_month = datetime(year + 1, 1, 1)
                else:
                    next_month = datetime(year, month + 1, 1)
                days_in_month = (next_month - first_day).days
                
                # Day labels
                day_labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                for i, day in enumerate(day_labels):
                    label = tk.Label(
                        cal_days_frame,
                        text=day,
                        font=('Segoe UI', 9, 'bold'),
                        bg='#f3f4f6',
                        fg='#374151',
                        width=4
                    )
                    label.grid(row=0, column=i, padx=1, pady=1)
                
                # Fill empty cells before first day
                for i in range(first_weekday):
                    empty = tk.Label(cal_days_frame, text="", bg='#ffffff', width=4)
                    empty.grid(row=1, column=i, padx=1, pady=1)
                
                # Fill days
                row = 1
                col = first_weekday
                for day in range(1, days_in_month + 1):
                    day_str = str(day)
                    day_btn = tk.Button(
                        cal_days_frame,
                        text=day_str,
                        font=('Segoe UI', 9),
                        bg='#ffffff',
                        fg='#374151',
                        width=4,
                        relief=tk.FLAT,
                        cursor='hand2',
                        command=lambda d=day: select_date(d)
                    )
                    
                    # Highlight today
                    today = datetime.now()
                    if day == today.day and month == today.month and year == today.year:
                        day_btn.config(bg='#3b82f6', fg='white')
                    
                    # Highlight current selected date
                    try:
                        current_selected = datetime.strptime(self.date_var.get(), '%Y-%m-%d')
                        if day == current_selected.day and month == current_selected.month and year == current_selected.year:
                            day_btn.config(bg='#10b981', fg='white')
                    except:
                        pass
                    
                    day_btn.grid(row=row, column=col, padx=1, pady=1)
                    
                    col += 1
                    if col > 6:
                        col = 0
                        row += 1
            
            def select_date(day):
                """Select a date"""
                month = month_var.get()
                year = year_var.get()
                selected = datetime(year, month, day)
                date_str = selected.strftime('%Y-%m-%d')
                self.date_var.set(date_str)
                calendar_window.destroy()
            
            def prev_month():
                """Go to previous month"""
                month = month_var.get()
                year = year_var.get()
                if month == 1:
                    month_var.set(12)
                    year_var.set(year - 1)
                else:
                    month_var.set(month - 1)
                update_calendar()
            
            def next_month():
                """Go to next month"""
                month = month_var.get()
                year = year_var.get()
                if month == 12:
                    month_var.set(1)
                    year_var.set(year + 1)
                else:
                    month_var.set(month + 1)
                update_calendar()
            
            # Navigation buttons
            prev_btn = tk.Button(
                nav_frame,
                text="◀",
                command=prev_month,
                font=('Segoe UI', 10, 'bold'),
                bg='#e5e7eb',
                fg='#374151',
                width=3,
                relief=tk.FLAT,
                cursor='hand2'
            )
            prev_btn.pack(side=tk.LEFT, padx=5)
            
            month_label = tk.Label(
                nav_frame,
                text="",
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#1a237e'
            )
            month_label.pack(side=tk.LEFT, expand=True)
            
            next_btn = tk.Button(
                nav_frame,
                text="▶",
                command=next_month,
                font=('Segoe UI', 10, 'bold'),
                bg='#e5e7eb',
                fg='#374151',
                width=3,
                relief=tk.FLAT,
                cursor='hand2'
            )
            next_btn.pack(side=tk.LEFT, padx=5)
            
            # Calendar days frame
            cal_days_frame = tk.Frame(cal_frame, bg='#ffffff')
            cal_days_frame.pack(fill=tk.BOTH, expand=True)
            
            # Button frame
            btn_frame = tk.Frame(calendar_window, bg='#ffffff')
            btn_frame.pack(fill=tk.X, padx=10, pady=10)
            
            today_btn = tk.Button(
                btn_frame,
                text="Today",
                command=lambda: select_date(datetime.now().day),
                font=('Segoe UI', 9),
                bg='#3b82f6',
                fg='white',
                padx=15,
                pady=5,
                relief=tk.FLAT,
                cursor='hand2'
            )
            today_btn.pack(side=tk.LEFT, padx=5)
            
            cancel_btn = tk.Button(
                btn_frame,
                text="Cancel",
                command=calendar_window.destroy,
                font=('Segoe UI', 9),
                bg='#6b7280',
                fg='white',
                padx=15,
                pady=5,
                relief=tk.FLAT,
                cursor='hand2'
            )
            cancel_btn.pack(side=tk.RIGHT, padx=5)
            
            # Initialize calendar
            update_calendar()
        
        # Calendar button for date filter
        date_cal_btn = tk.Button(
            date_filter_frame,
            text="📅",
            command=open_calendar_for_filter,
            font=('Segoe UI', 12),
            bg='#3b82f6',
            fg='white',
            width=3,
            relief=tk.FLAT,
            cursor='hand2',
            padx=5
        )
        date_cal_btn.pack(side=tk.LEFT, padx=(5, 0))
        
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
        columns = ('ID', 'Patient ID', 'Patient Name', 'Doctor', 'Date', 'Diagnosis')
        
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
            'Patient ID': 120,
            'Patient Name': 180,
            'Doctor': 200,
            'Date': 150,
            'Diagnosis': 250
        }
        
        min_widths = {
            'ID': 120,
            'Patient ID': 100,
            'Patient Name': 150,
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
        """Refresh prescription list (shows all prescriptions)"""
        # Reset filters
        self.search_var.set("")
        self.date_var.set("")
        
        # apply_filters will be called automatically via trace
        self.apply_filters()
    
    def apply_filters(self, *args):
        """Apply patient name search and date filters automatically"""
        # Clear existing items
        self.tree.delete(*self.tree.get_children())
        
        patient_name = self.search_var.get().strip()
        date = self.date_var.get().strip()
        
        try:
            # Determine which filter to apply
            if patient_name and date:
                # Filter by both patient name and date
                prescriptions = self.db.get_prescriptions_by_patient_name(patient_name)
                # Filter by date in memory (since we don't have a combined method)
                prescriptions = [p for p in prescriptions if p.get('prescription_date') == date]
            elif patient_name:
                # Filter by patient name only
                prescriptions = self.db.get_prescriptions_by_patient_name(patient_name)
            elif date:
                # Filter by date only
                prescriptions = self.db.get_prescriptions_by_date(date)
            else:
                # No filters - show all
                prescriptions = self.db.get_all_prescriptions()
            
            # Add each prescription to the treeview
            for pres in prescriptions:
                # Get doctor name (fallback to doctor_id if name not available)
                doctor_display = pres.get('doctor_name', pres.get('doctor_id', 'Unknown'))
                
                # Get patient name (fallback to patient_id if name not available)
                patient_display = pres.get('patient_name', pres.get('patient_id', 'Unknown'))
                
                # Truncate diagnosis if too long for display
                diagnosis = pres.get('diagnosis', '')
                if len(diagnosis) > 50:
                    diagnosis = diagnosis[:47] + '...'
                
                self.tree.insert('', tk.END, values=(
                    pres['prescription_id'],
                    pres['patient_id'],
                    patient_display,
                    doctor_display,
                    pres['prescription_date'],
                    diagnosis
                ))
        except Exception as e:
            # Log error but don't crash
            print(f"Error applying filters: {e}")
    
    def search_prescriptions(self):
        """Search prescriptions by patient (deprecated - use apply_filters instead)"""
        self.apply_filters()
    
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
        
        # Create scrollable container with better background
        canvas = tk.Canvas(self.parent, bg='#f5f7fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f5f7fa')
        
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
        main_frame.configure(bg='#f5f7fa')
        
        # Header with back button - improved styling
        header_frame = tk.Frame(main_frame, bg='#1e40af', height=65)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        if not is_editing:
            prescription_id = generate_id('PRES')
        title_text = f"{'✏️ Edit' if is_editing else '➕ New'} Prescription - ID: {prescription_id}"
        title_label = tk.Label(
            header_frame,
            text=title_text,
            font=('Segoe UI', 14, 'bold'),
            bg='#1e40af',
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=25, pady=18)
        
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
            font=('Segoe UI', 10, 'bold'),
            bg='#3b82f6',
            fg='white',
            padx=18,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#2563eb',
            activeforeground='white'
        )
        back_btn.pack(side=tk.RIGHT, padx=25, pady=12)
        
        # Form container with padding
        form_container = tk.Frame(main_frame, bg='#ffffff')
        form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Two-column layout
        left_column = tk.Frame(form_container, bg='#ffffff')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_column = tk.Frame(form_container, bg='#ffffff')
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Form fields frame with better styling
        form_frame = tk.LabelFrame(
            left_column, 
            text="👤 Patient & Doctor Information", 
            font=('Segoe UI', 11, 'bold'), 
            bg='#ffffff', 
            fg='#1a237e',
            padx=20, 
            pady=15,
            relief=tk.RAISED,
            bd=2
        )
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Patient selection with searchable dropdown
        patient_label_frame = tk.Frame(form_frame, bg='#ffffff')
        patient_label_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(patient_label_frame, text="Patient *", font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        
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
            font=('Segoe UI', 10),
            state='normal',
            height=8
        )
        patient_combo.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
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
        doctor_label_frame = tk.Frame(form_frame, bg='#ffffff')
        doctor_label_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(doctor_label_frame, text="Doctor *", font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        
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
            font=('Segoe UI', 10),
            state='normal',
            height=8
        )
        doctor_combo.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
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
        appointment_label_frame = tk.Frame(form_frame, bg='#ffffff')
        appointment_label_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(appointment_label_frame, text="Appointment ID (Optional)", font=('Segoe UI', 10), bg='#ffffff', fg='#6b7280').pack(anchor='w')
        appointment_var = tk.StringVar()
        appointment_entry = tk.Entry(form_frame, textvariable=appointment_var, font=('Segoe UI', 10), relief=tk.SOLID, bd=1)
        appointment_entry.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Date with calendar picker
        date_label_frame = tk.Frame(form_frame, bg='#ffffff')
        date_label_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(date_label_frame, text="Date", font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        
        date_input_frame = tk.Frame(form_frame, bg='#ffffff')
        date_input_frame.pack(fill=tk.X, pady=(0, 15))
        
        date_entry = tk.Entry(date_input_frame, font=('Segoe UI', 10), relief=tk.SOLID, bd=1)
        date_entry.insert(0, get_current_date())
        date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 5))
        
        def open_calendar():
            """Open calendar date picker"""
            calendar_window = tk.Toplevel(self.parent)
            calendar_window.title("Select Date")
            calendar_window.geometry("300x280")
            calendar_window.configure(bg='#ffffff')
            calendar_window.transient(self.parent)
            calendar_window.grab_set()
            
            # Center the window
            calendar_window.update_idletasks()
            x = (calendar_window.winfo_screenwidth() // 2) - (300 // 2)
            y = (calendar_window.winfo_screenheight() // 2) - (280 // 2)
            calendar_window.geometry(f"300x280+{x}+{y}")
            
            # Header
            header_frame = tk.Frame(calendar_window, bg='#1e40af', height=40)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            tk.Label(
                header_frame,
                text="Select Date",
                font=('Segoe UI', 12, 'bold'),
                bg='#1e40af',
                fg='white'
            ).pack(pady=10)
            
            # Calendar frame
            cal_frame = tk.Frame(calendar_window, bg='#ffffff')
            cal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Get current date from entry or use today
            current_date_str = date_entry.get()
            try:
                current_date = datetime.strptime(current_date_str, '%Y-%m-%d')
            except:
                current_date = datetime.now()
            
            # Variables for month and year
            month_var = tk.IntVar(value=current_date.month)
            year_var = tk.IntVar(value=current_date.year)
            selected_date = tk.StringVar()
            
            # Month and year navigation
            nav_frame = tk.Frame(cal_frame, bg='#ffffff')
            nav_frame.pack(fill=tk.X, pady=(0, 10))
            
            def update_calendar():
                """Update calendar display"""
                # Clear existing calendar
                for widget in cal_days_frame.winfo_children():
                    widget.destroy()
                
                month = month_var.get()
                year = year_var.get()
                
                # Update month/year label
                month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                             'July', 'August', 'September', 'October', 'November', 'December']
                month_label.config(text=f"{month_names[month-1]} {year}")
                
                # Get first day of month and number of days
                first_day = datetime(year, month, 1)
                first_weekday = first_day.weekday()  # 0 = Monday, 6 = Sunday
                
                # Adjust to Sunday = 0
                first_weekday = (first_weekday + 1) % 7
                
                # Get number of days in month
                if month == 12:
                    next_month = datetime(year + 1, 1, 1)
                else:
                    next_month = datetime(year, month + 1, 1)
                days_in_month = (next_month - first_day).days
                
                # Day labels
                day_labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                for i, day in enumerate(day_labels):
                    label = tk.Label(
                        cal_days_frame,
                        text=day,
                        font=('Segoe UI', 9, 'bold'),
                        bg='#f3f4f6',
                        fg='#374151',
                        width=4
                    )
                    label.grid(row=0, column=i, padx=1, pady=1)
                
                # Fill empty cells before first day
                for i in range(first_weekday):
                    empty = tk.Label(cal_days_frame, text="", bg='#ffffff', width=4)
                    empty.grid(row=1, column=i, padx=1, pady=1)
                
                # Fill days
                row = 1
                col = first_weekday
                for day in range(1, days_in_month + 1):
                    day_str = str(day)
                    day_btn = tk.Button(
                        cal_days_frame,
                        text=day_str,
                        font=('Segoe UI', 9),
                        bg='#ffffff',
                        fg='#374151',
                        width=4,
                        relief=tk.FLAT,
                        cursor='hand2',
                        command=lambda d=day: select_date(d)
                    )
                    
                    # Highlight today
                    today = datetime.now()
                    if day == today.day and month == today.month and year == today.year:
                        day_btn.config(bg='#3b82f6', fg='white')
                    
                    # Highlight current selected date
                    try:
                        current_selected = datetime.strptime(date_entry.get(), '%Y-%m-%d')
                        if day == current_selected.day and month == current_selected.month and year == current_selected.year:
                            day_btn.config(bg='#10b981', fg='white')
                    except:
                        pass
                    
                    day_btn.grid(row=row, column=col, padx=1, pady=1)
                    
                    col += 1
                    if col > 6:
                        col = 0
                        row += 1
            
            def select_date(day):
                """Select a date"""
                month = month_var.get()
                year = year_var.get()
                selected = datetime(year, month, day)
                date_str = selected.strftime('%Y-%m-%d')
                date_entry.delete(0, tk.END)
                date_entry.insert(0, date_str)
                calendar_window.destroy()
            
            def prev_month():
                """Go to previous month"""
                month = month_var.get()
                year = year_var.get()
                if month == 1:
                    month_var.set(12)
                    year_var.set(year - 1)
                else:
                    month_var.set(month - 1)
                update_calendar()
            
            def next_month():
                """Go to next month"""
                month = month_var.get()
                year = year_var.get()
                if month == 12:
                    month_var.set(1)
                    year_var.set(year + 1)
                else:
                    month_var.set(month + 1)
                update_calendar()
            
            # Navigation buttons
            prev_btn = tk.Button(
                nav_frame,
                text="◀",
                command=prev_month,
                font=('Segoe UI', 10, 'bold'),
                bg='#e5e7eb',
                fg='#374151',
                width=3,
                relief=tk.FLAT,
                cursor='hand2'
            )
            prev_btn.pack(side=tk.LEFT, padx=5)
            
            month_label = tk.Label(
                nav_frame,
                text="",
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#1a237e'
            )
            month_label.pack(side=tk.LEFT, expand=True)
            
            next_btn = tk.Button(
                nav_frame,
                text="▶",
                command=next_month,
                font=('Segoe UI', 10, 'bold'),
                bg='#e5e7eb',
                fg='#374151',
                width=3,
                relief=tk.FLAT,
                cursor='hand2'
            )
            next_btn.pack(side=tk.LEFT, padx=5)
            
            # Calendar days frame
            cal_days_frame = tk.Frame(cal_frame, bg='#ffffff')
            cal_days_frame.pack(fill=tk.BOTH, expand=True)
            
            # Button frame
            btn_frame = tk.Frame(calendar_window, bg='#ffffff')
            btn_frame.pack(fill=tk.X, padx=10, pady=10)
            
            today_btn = tk.Button(
                btn_frame,
                text="Today",
                command=lambda: select_date(datetime.now().day),
                font=('Segoe UI', 9),
                bg='#3b82f6',
                fg='white',
                padx=15,
                pady=5,
                relief=tk.FLAT,
                cursor='hand2'
            )
            today_btn.pack(side=tk.LEFT, padx=5)
            
            cancel_btn = tk.Button(
                btn_frame,
                text="Cancel",
                command=calendar_window.destroy,
                font=('Segoe UI', 9),
                bg='#6b7280',
                fg='white',
                padx=15,
                pady=5,
                relief=tk.FLAT,
                cursor='hand2'
            )
            cancel_btn.pack(side=tk.RIGHT, padx=5)
            
            # Initialize calendar
            update_calendar()
        
        # Calendar button
        calendar_btn = tk.Button(
            date_input_frame,
            text="📅",
            command=open_calendar,
            font=('Segoe UI', 12),
            bg='#3b82f6',
            fg='white',
            width=3,
            relief=tk.FLAT,
            cursor='hand2',
            activebackground='#2563eb'
        )
        calendar_btn.pack(side=tk.LEFT)
        
        # Diagnosis
        diagnosis_label_frame = tk.Frame(form_frame, bg='#ffffff')
        diagnosis_label_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(diagnosis_label_frame, text="Diagnosis", font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        diagnosis_text = tk.Text(form_frame, font=('Segoe UI', 10), height=4, wrap=tk.WORD, relief=tk.SOLID, bd=1, padx=5, pady=5)
        diagnosis_text.pack(fill=tk.X, pady=(0, 10))
        
        # Additional Notes section
        notes_frame = tk.LabelFrame(
            right_column, 
            text="📝 Additional Notes", 
            font=('Segoe UI', 11, 'bold'), 
            bg='#ffffff', 
            fg='#1a237e',
            padx=20, 
            pady=15,
            relief=tk.RAISED,
            bd=2
        )
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        notes_label_frame = tk.Frame(notes_frame, bg='#ffffff')
        notes_label_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(notes_label_frame, text="Doctor's Notes", font=('Segoe UI', 10), bg='#ffffff', fg='#6b7280').pack(anchor='w')
        notes_text = tk.Text(notes_frame, font=('Segoe UI', 10), height=12, wrap=tk.WORD, relief=tk.SOLID, bd=1, padx=5, pady=5)
        notes_text.pack(fill=tk.BOTH, expand=True)
        
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
        
        # Medicines section - spans full width with better styling
        medicines_frame = tk.LabelFrame(
            main_frame, 
            text="💊 Prescribed Medicines", 
            font=('Segoe UI', 11, 'bold'), 
            bg='#ffffff', 
            fg='#1a237e',
            padx=20, 
            pady=15,
            relief=tk.RAISED,
            bd=2
        )
        medicines_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
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
        
        # Medicines list with remove button - better styling
        med_list_frame = tk.Frame(medicines_frame, bg='#ffffff')
        med_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Info label
        info_label = tk.Label(
            med_list_frame, 
            text="📋 Added Medicines (Double-click to remove)", 
            font=('Segoe UI', 9), 
            bg='#ffffff', 
            fg='#6b7280',
            anchor='w'
        )
        info_label.pack(fill=tk.X, pady=(0, 5))
        
        med_columns = ('Medicine', 'Type', 'Dosage', 'Frequency', 'Duration', 'Instructions')
        med_tree = ttk.Treeview(med_list_frame, columns=med_columns, show='headings', height=6)
        
        # Configure treeview style
        style = ttk.Style()
        style.configure("MedTreeview.Treeview", 
                       font=('Segoe UI', 9), 
                       rowheight=28,
                       background='#ffffff',
                       foreground='#374151',
                       fieldbackground='#ffffff')
        style.configure("MedTreeview.Treeview.Heading", 
                       font=('Segoe UI', 9, 'bold'), 
                       background='#6366f1', 
                       foreground='white',
                       relief='flat')
        style.map("MedTreeview.Treeview",
                 background=[('selected', '#6366f1')],
                 foreground=[('selected', 'white')])
        
        med_tree.configure(style="MedTreeview.Treeview")
        
        for col in med_columns:
            med_tree.heading(col, text=col)
            if col == 'Medicine':
                med_tree.column(col, width=200)
            elif col == 'Type':
                med_tree.column(col, width=90, anchor='center')
            elif col == 'Instructions':
                med_tree.column(col, width=200)
            else:
                med_tree.column(col, width=120)
        
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
        
        # Bind double-click to remove
        med_tree.bind('<Double-1>', lambda e: remove_selected_medicine())
        
        # Add Remove Selected button below the medicine list
        remove_btn_frame = tk.Frame(medicines_frame, bg='#ffffff')
        remove_btn_frame.pack(fill=tk.X, pady=(5, 15))
        
        remove_selected_btn = tk.Button(
            remove_btn_frame,
            text="🗑️ Remove Selected",
            command=remove_selected_medicine,
            font=('Segoe UI', 9, 'bold'),
            bg='#ef4444',
            fg='white',
            padx=15,
            pady=6,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#dc2626'
        )
        remove_selected_btn.pack(side=tk.LEFT)
        
        # Add medicine frame with better styling
        add_med_frame = tk.LabelFrame(
            medicines_frame, 
            text="➕ Add New Medicine", 
            font=('Segoe UI', 10, 'bold'), 
            bg='#ffffff', 
            fg='#1a237e',
            padx=15, 
            pady=12,
            relief=tk.GROOVE,
            bd=1
        )
        add_med_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Medicine name with searchable dropdown - improved layout
        med_name_frame = tk.Frame(add_med_frame, bg='#ffffff')
        med_name_frame.pack(fill=tk.X, pady=(0, 10))
        
        med_name_label_frame = tk.Frame(med_name_frame, bg='#ffffff')
        med_name_label_frame.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(med_name_label_frame, text="Medicine Name *", font=('Segoe UI', 9, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        
        med_name_input_frame = tk.Frame(med_name_frame, bg='#ffffff')
        med_name_input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        med_name_var = tk.StringVar()
        med_name_entry = tk.Entry(
            med_name_input_frame,
            textvariable=med_name_var,
            font=('Segoe UI', 10),
            relief=tk.SOLID,
            bd=1
        )
        med_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=4)
        
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
            
        # Button to open medicine selector - improved styling
        select_med_btn = tk.Button(
            med_name_input_frame,
            text="🔍 Browse",
            command=open_medicine_selector,
            font=('Segoe UI', 9, 'bold'),
            bg='#6366f1',
            fg='white',
            padx=12,
            pady=4,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#4f46e5',
            activeforeground='white'
        )
        select_med_btn.pack(side=tk.LEFT)
        
        # Medicine details in a grid - improved layout
        details_frame = tk.Frame(add_med_frame, bg='#ffffff')
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
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
        
        # Dosage field
        dosage_label_frame = tk.Frame(details_frame, bg='#ffffff')
        dosage_label_frame.grid(row=0, column=0, sticky='w', padx=(0, 8), pady=5)
        tk.Label(dosage_label_frame, text="Dosage *", font=('Segoe UI', 9, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        
        dosage_var = tk.StringVar()
        dosage_combo = ttk.Combobox(
            details_frame, 
            textvariable=dosage_var, 
            values=dosage_options, 
            font=('Segoe UI', 9), 
            width=20, 
            state='normal'
        )
        dosage_combo.grid(row=0, column=1, padx=(0, 15), pady=5, sticky='ew', ipady=3)
        
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
        
        # Frequency field
        frequency_label_frame = tk.Frame(details_frame, bg='#ffffff')
        frequency_label_frame.grid(row=0, column=2, sticky='w', padx=(0, 8), pady=5)
        tk.Label(frequency_label_frame, text="Frequency *", font=('Segoe UI', 9, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        
        frequency_var = tk.StringVar()
        frequency_combo = ttk.Combobox(
            details_frame, 
            textvariable=frequency_var, 
            values=frequency_options, 
            font=('Segoe UI', 9), 
            width=20, 
            state='normal'
        )
        frequency_combo.grid(row=0, column=3, padx=(0, 0), pady=5, sticky='ew', ipady=3)
        
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
        
        # Duration field
        duration_label_frame = tk.Frame(details_frame, bg='#ffffff')
        duration_label_frame.grid(row=1, column=0, sticky='w', padx=(0, 8), pady=5)
        tk.Label(duration_label_frame, text="Duration *", font=('Segoe UI', 9, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        
        duration_var = tk.StringVar()
        duration_combo = ttk.Combobox(
            details_frame, 
            textvariable=duration_var, 
            values=duration_options, 
            font=('Segoe UI', 9), 
            width=20, 
            state='normal'
        )
        duration_combo.grid(row=1, column=1, padx=(0, 15), pady=5, sticky='ew', ipady=3)
        
        # Make duration searchable
        def filter_duration(*args):
            value = duration_var.get().lower()
            if value == '':
                duration_combo['values'] = duration_options
            else:
                filtered = [opt for opt in duration_options if value in opt.lower()]
                duration_combo['values'] = filtered
        
        duration_var.trace('w', filter_duration)
        
        # Instructions field
        instructions_label_frame = tk.Frame(details_frame, bg='#ffffff')
        instructions_label_frame.grid(row=1, column=2, sticky='w', padx=(0, 8), pady=5)
        tk.Label(instructions_label_frame, text="Instructions", font=('Segoe UI', 9), bg='#ffffff', fg='#6b7280').pack(anchor='w')
        
        instructions_entry = tk.Entry(
            details_frame, 
            font=('Segoe UI', 9), 
            width=20,
            relief=tk.SOLID,
            bd=1
        )
        instructions_entry.grid(row=1, column=3, padx=(0, 0), pady=5, sticky='ew', ipady=3)
        
        details_frame.grid_columnconfigure(1, weight=1)
        details_frame.grid_columnconfigure(3, weight=1)
        
        def add_medicine():
            med_name = med_name_var.get().strip()
            dosage = dosage_var.get().strip()
            frequency = frequency_var.get().strip()
            duration = duration_var.get().strip()
            instructions = instructions_entry.get().strip()
            
            if not med_name:
                messagebox.showwarning("Missing Information", "Please enter the medicine name.\n\nTip: Use the 'Browse' button to search from the medicine database.")
                med_name_entry.focus_set()
                return
            
            if not dosage:
                messagebox.showwarning("Missing Information", "Please select or enter the dosage for the medicine.")
                dosage_combo.focus_set()
                return
            
            if not frequency:
                messagebox.showwarning("Missing Information", "Please select how often the medicine should be taken (e.g., 'Twice daily', 'Once daily').")
                frequency_combo.focus_set()
                return
            
            if not duration:
                messagebox.showwarning("Missing Information", "Please select how long the medicine should be taken (e.g., '7 days', '2 weeks').")
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
            
            # Set focus back to medicine name for quick entry
            med_name_entry.focus_set()
            
            # Show success feedback
            med_tree.see(item)  # Scroll to show the newly added item
        
        # Add Medicine button - improved styling
        add_med_btn_frame = tk.Frame(add_med_frame, bg='#ffffff')
        add_med_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        add_med_btn = tk.Button(
            add_med_btn_frame,
            text="➕ Add Medicine to List",
            command=add_medicine,
            font=('Segoe UI', 10, 'bold'),
            bg='#3b82f6',
            fg='white',
            padx=25,
            pady=10,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#2563eb',
            activeforeground='white'
        )
        add_med_btn.pack(side=tk.LEFT)
        
        # Quick tip label
        tip_label = tk.Label(
            add_med_btn_frame,
            text="💡 Tip: Press Enter after filling fields to quickly add",
            font=('Segoe UI', 8),
            bg='#ffffff',
            fg='#6b7280'
        )
        tip_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Bind Enter key to add medicine - improved navigation
        def on_med_enter(event):
            add_medicine()
            return "break"
        
        def on_med_tab(event):
            """Handle Tab key - move to next field or add if all filled"""
            widget = event.widget
            if widget == med_name_entry:
                dosage_combo.focus_set()
                return "break"
            elif widget == dosage_combo:
                frequency_combo.focus_set()
                return "break"
            elif widget == frequency_combo:
                duration_combo.focus_set()
                return "break"
            elif widget == duration_combo:
                instructions_entry.focus_set()
                return "break"
            elif widget == instructions_entry:
                # If all fields filled, add medicine
                if (med_name_var.get().strip() and dosage_var.get().strip() and 
                    frequency_var.get().strip() and duration_var.get().strip()):
                    add_medicine()
                return "break"
        
        med_name_entry.bind('<Return>', on_med_enter)
        med_name_entry.bind('<Tab>', on_med_tab)
        dosage_combo.bind('<Return>', on_med_enter)
        dosage_combo.bind('<Tab>', on_med_tab)
        frequency_combo.bind('<Return>', on_med_enter)
        frequency_combo.bind('<Tab>', on_med_tab)
        duration_combo.bind('<Return>', on_med_enter)
        duration_combo.bind('<Tab>', on_med_tab)
        instructions_entry.bind('<Return>', on_med_enter)
        instructions_entry.bind('<Tab>', on_med_tab)
        
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
        
        # Save and Cancel buttons at bottom - improved styling
        button_frame = tk.Frame(main_frame, bg='#f8f9fa', relief=tk.RAISED, bd=1)
        button_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        inner_button_frame = tk.Frame(button_frame, bg='#f8f9fa')
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
                messagebox.showerror("Validation Error", "Please select a patient from the dropdown list.\n\nYou can type to search for a patient.")
                patient_combo.focus_set()
                return
            
            if not doctor_id:
                messagebox.showerror("Validation Error", "Please select a doctor from the dropdown list.\n\nYou can type to search for a doctor.")
                doctor_combo.focus_set()
                return
            
            if not medicines:
                messagebox.showerror("Validation Error", "Please add at least one medicine to the prescription.\n\nUse the 'Add Medicine' section below to add medicines.")
                med_name_entry.focus_set()
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
        
        def print_prescription():
            """Generate and print professional prescription PDF"""
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
                messagebox.showwarning("Warning", "Please select a patient to print prescription")
                return
            
            if not doctor_id:
                messagebox.showwarning("Warning", "Please select a doctor to print prescription")
                return
            
            if not medicines:
                messagebox.showwarning("Warning", "Please add at least one medicine to print prescription")
                return
            
            # Get patient and doctor details
            patient = self.db.get_patient_by_id(patient_id)
            doctor = self.db.get_doctor_by_id(doctor_id)
            
            if not patient or not doctor:
                messagebox.showerror("Error", "Could not retrieve patient or doctor information")
                return
            
            # Get prescription details
            prescription_date = date_entry.get() or get_current_date()
            diagnosis = diagnosis_text.get('1.0', tk.END).strip()
            notes = notes_text.get('1.0', tk.END).strip()
            
            # Try to generate PDF using reportlab
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.units import mm
                from reportlab.lib import colors
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont
                
                # Ask user where to save PDF
                filename = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialfile=f"Prescription_{prescription_id}_{prescription_date.replace('-', '')}.pdf"
                )
                
                if not filename:
                    return  # User cancelled
                
                # Create PDF document
                doc = SimpleDocTemplate(filename, pagesize=A4,
                                      rightMargin=15*mm, leftMargin=15*mm,
                                      topMargin=15*mm, bottomMargin=15*mm)
                
                # Container for the 'Flowable' objects
                elements = []
                
                # Define styles
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=18,
                    textColor=colors.HexColor('#1a237e'),
                    spaceAfter=12,
                    alignment=TA_CENTER,
                    fontName='Helvetica-Bold'
                )
                
                heading_style = ParagraphStyle(
                    'CustomHeading',
                    parent=styles['Heading2'],
                    fontSize=12,
                    textColor=colors.HexColor('#1a237e'),
                    spaceAfter=6,
                    spaceBefore=12,
                    fontName='Helvetica-Bold'
                )
                
                normal_style = ParagraphStyle(
                    'CustomNormal',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=colors.black,
                    spaceAfter=6,
                    fontName='Helvetica'
                )
                
                small_style = ParagraphStyle(
                    'CustomSmall',
                    parent=styles['Normal'],
                    fontSize=9,
                    textColor=colors.black,
                    spaceAfter=4,
                    fontName='Helvetica'
                )
                
                # Header - Doctor info on left, Clinic info on right
                doctor_name = f"Dr. {doctor.get('first_name', '')} {doctor.get('last_name', '')}".strip()
                doctor_qual = doctor.get('qualification', '')
                doctor_spec = doctor.get('specialization', '')
                
                # Calculate patient age
                patient_age = ""
                patient_gender = patient.get('gender', '')
                if patient.get('date_of_birth'):
                    try:
                        dob = datetime.strptime(patient['date_of_birth'], '%Y-%m-%d')
                        age = (datetime.now() - dob).days // 365
                        patient_age = f"{age}"
                    except:
                        pass
                
                patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip().upper()
                
                # Format date for display
                try:
                    date_obj = datetime.strptime(prescription_date, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%d.%m.%Y')
                except:
                    formatted_date = prescription_date
                
                # Header table
                header_data = [
                    [
                        Paragraph(f"<b>{doctor_name}</b><br/>"
                                 f"{doctor_qual}<br/>"
                                 f"Specialization: {doctor_spec}<br/>"
                                 f"Mobile: {doctor.get('phone', 'N/A')}<br/>"
                                 f"Email: {doctor.get('email', 'N/A')}", 
                                 normal_style),
                        Paragraph(f"<b>PRESCRIPTION</b><br/>"
                                 f"Date: {formatted_date}<br/>"
                                 f"Prescription ID: {prescription_id}", 
                                 normal_style)
                    ]
                ]
                
                header_table = Table(header_data, colWidths=[90*mm, 90*mm])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(header_table)
                elements.append(Spacer(1, 8*mm))
                
                # Patient Information
                patient_info_data = [
                    ['Name:', patient_name],
                    ['Age/Gender:', f"{patient_age}/{patient_gender}" if patient_age else patient_gender],
                    ['Patient ID:', patient_id],
                ]
                if patient.get('phone'):
                    patient_info_data.append(['Phone:', patient.get('phone')])
                if patient.get('address'):
                    patient_info_data.append(['Address:', patient.get('address')])
                
                patient_table = Table(patient_info_data, colWidths=[30*mm, 150*mm])
                patient_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                elements.append(Paragraph("<b>PATIENT INFORMATION</b>", heading_style))
                elements.append(patient_table)
                elements.append(Spacer(1, 6*mm))
                
                # Diagnosis
                if diagnosis:
                    elements.append(Paragraph("<b>DIAGNOSIS</b>", heading_style))
                    elements.append(Paragraph(diagnosis.replace('\n', '<br/>'), normal_style))
                    elements.append(Spacer(1, 6*mm))
                
                # Medicines
                elements.append(Paragraph("<b>PRESCRIBED MEDICINES</b>", heading_style))
                
                med_data = [['R', 'Medicine Name', 'Dosage', 'Frequency', 'Duration', 'Instructions']]
                for idx, med in enumerate(medicines, 1):
                    med_data.append([
                        str(idx),
                        med['medicine_name'],
                        med['dosage'],
                        med['frequency'],
                        med['duration'],
                        med.get('instructions', '')
                    ])
                
                med_table = Table(med_data, colWidths=[8*mm, 50*mm, 25*mm, 35*mm, 25*mm, 37*mm])
                med_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                    ('ALIGN', (5, 1), (5, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
                ]))
                elements.append(med_table)
                elements.append(Spacer(1, 8*mm))
                
                # Doctor's Notes
                if notes:
                    elements.append(Paragraph("<b>DOCTOR'S NOTES</b>", heading_style))
                    elements.append(Paragraph(notes.replace('\n', '<br/>'), normal_style))
                    elements.append(Spacer(1, 8*mm))
                
                # Footer
                footer_data = [
                    ['Signature: _________________________', f'Date: {formatted_date}']
                ]
                footer_table = Table(footer_data, colWidths=[90*mm, 90*mm])
                footer_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 20),
                ]))
                elements.append(footer_table)
                
                # Build PDF
                doc.build(elements)
                messagebox.showinfo("Success", f"Prescription saved successfully!\n\n{filename}")
                
                # Ask if user wants to open the PDF
                import platform
                import subprocess
                if messagebox.askyesno("Open PDF", "Do you want to open the PDF now?"):
                    system = platform.system()
                    if system == "Windows":
                        os.startfile(filename)
                    elif system == "Darwin":  # macOS
                        subprocess.run(['open', filename])
                    else:  # Linux
                        subprocess.run(['xdg-open', filename])
                        
            except ImportError:
                # Fallback to text printing if reportlab not available
                messagebox.showwarning("PDF Library Not Found", 
                    "reportlab library is not installed.\n\n"
                    "Please install it using: pip install reportlab\n\n"
                    "Falling back to text format...")
                _generate_text_prescription(patient, doctor, prescription_id, prescription_date, 
                                          diagnosis, notes, medicines, patient_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}\n\nFalling back to text format...")
                _generate_text_prescription(patient, doctor, prescription_id, prescription_date, 
                                          diagnosis, notes, medicines, patient_id)
        
        def _generate_text_prescription(patient, doctor, prescription_id, prescription_date, 
                                       diagnosis, notes, medicines, patient_id):
            """Fallback text prescription generator"""
            patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip()
            doctor_name = f"Dr. {doctor.get('first_name', '')} {doctor.get('last_name', '')}".strip()
            
            # Calculate age
            patient_age = ""
            if patient.get('date_of_birth'):
                try:
                    dob = datetime.strptime(patient['date_of_birth'], '%Y-%m-%d')
                    age = (datetime.now() - dob).days // 365
                    patient_age = f"{age} years"
                except:
                    pass
            
            print_text = f"""
================================================================
                    PRESCRIPTION
================================================================

Prescription ID: {prescription_id}
Date: {prescription_date}

----------------------------------------------------------------
DOCTOR INFORMATION
----------------------------------------------------------------
  Name: {doctor_name}
  Specialization: {doctor.get('specialization', 'N/A')}
  Qualification: {doctor.get('qualification', 'N/A')}

----------------------------------------------------------------
PATIENT INFORMATION
----------------------------------------------------------------
  Name: {patient_name}
  Patient ID: {patient_id}
  Age: {patient_age if patient_age else 'N/A'}
  Gender: {patient.get('gender', 'N/A')}
  Phone: {patient.get('phone', 'N/A')}

----------------------------------------------------------------
DIAGNOSIS
----------------------------------------------------------------
{diagnosis if diagnosis else 'N/A'}

----------------------------------------------------------------
PRESCRIBED MEDICINES
----------------------------------------------------------------
"""
            
            for idx, med in enumerate(medicines, 1):
                print_text += f"""
{idx}. {med['medicine_name']}
   Dosage: {med['dosage']}
   Frequency: {med['frequency']}
   Duration: {med['duration']}"""
                if med.get('instructions'):
                    print_text += f"\n   Instructions: {med['instructions']}"
                print_text += "\n"
            
            if notes:
                print_text += f"""
----------------------------------------------------------------
DOCTOR'S NOTES
----------------------------------------------------------------
{notes}
"""
            
            print_text += f"""
----------------------------------------------------------------

Signature: _________________________

Date: {prescription_date}
"""
            
            _show_print_dialog(print_text, f"Prescription - {prescription_id}", self.parent)
        
        def _show_print_dialog(text, title="Print", parent_window=None):
            """Show print dialog with formatted text"""
            import tempfile
            import os
            import subprocess
            import platform
            
            # Use parent_window if provided, otherwise use self.parent from closure
            dialog_parent = parent_window if parent_window else self.parent
            
            print_dialog = tk.Toplevel(dialog_parent)
            print_dialog.title(title)
            print_dialog.geometry("700x600")
            print_dialog.configure(bg='#f0f0f0')
            print_dialog.transient(dialog_parent)
            
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
                    # Create temporary file with UTF-8 encoding for proper character support
                    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8', newline='')
                    temp_file.write(text)
                    temp_file.flush()  # Ensure all data is written
                    temp_file.close()
                    
                    # Print based on OS
                    system = platform.system()
                    if system == "Windows":
                        # On Windows, use PowerShell to print
                        try:
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
                        subprocess.run(['lpr', temp_file.name], check=True)
                        messagebox.showinfo("Print", "Document sent to default printer!")
                    
                    # Clean up temp file after a delay
                    try:
                        import time
                        time.sleep(2)
                        os.unlink(temp_file.name)
                    except:
                        pass
                except Exception as e:
                    messagebox.showerror("Print Error", f"Failed to print: {str(e)}\n\nYou can copy the text and print manually.")
            
            print_btn = tk.Button(
                button_frame,
                text="🖨️ Print",
                command=print_text,
                font=('Segoe UI', 10, 'bold'),
                bg='#f59e0b',
                fg='white',
                padx=20,
                pady=8,
                cursor='hand2',
                relief=tk.FLAT,
                activebackground='#d97706'
            )
            print_btn.pack(side=tk.LEFT, padx=5)
            
            close_btn = tk.Button(
                button_frame,
                text="Close",
                command=print_dialog.destroy,
                font=('Segoe UI', 10),
                bg='#6b7280',
                fg='white',
                padx=20,
                pady=8,
                cursor='hand2',
                relief=tk.FLAT,
                activebackground='#4b5563'
            )
            close_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = tk.Button(
            inner_button_frame,
            text="💾 Save Prescription",
            command=save_prescription,
            font=('Segoe UI', 11, 'bold'),
            bg='#10b981',
            fg='white',
            padx=35,
            pady=12,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#059669',
            activeforeground='white'
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        print_btn = tk.Button(
            inner_button_frame,
            text="🖨️ Print Prescription",
            command=print_prescription,
            font=('Segoe UI', 10, 'bold'),
            bg='#f59e0b',
            fg='white',
            padx=30,
            pady=12,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#d97706',
            activeforeground='white'
        )
        print_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(
            inner_button_frame,
            text="❌ Cancel",
            command=back_to_list,
            font=('Segoe UI', 10),
            bg='#6b7280',
            fg='white',
            padx=30,
            pady=12,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#4b5563',
            activeforeground='white'
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # Set focus on patient combo when form opens
        self.parent.after(100, lambda: patient_combo.focus_set())
        
        # Add keyboard shortcut hints
        shortcut_frame = tk.Frame(main_frame, bg='#f5f7fa')
        shortcut_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        shortcuts_text = "💡 Keyboard Shortcuts: Enter/Tab to navigate | Enter in medicine fields to add | Double-click medicine to remove"
        shortcuts_label = tk.Label(
            shortcut_frame,
            text=shortcuts_text,
            font=('Segoe UI', 8),
            bg='#f5f7fa',
            fg='#6b7280',
            anchor='w'
        )
        shortcuts_label.pack(fill=tk.X, padx=10, pady=5)
        
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

