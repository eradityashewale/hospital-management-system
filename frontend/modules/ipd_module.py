"""
IPD (In-Patient Department) Management Module
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Backend imports
from backend.database import Database

# Utils imports
from utils.helpers import generate_id, get_current_date
from utils.logger import (log_button_click, log_dialog_open, log_dialog_close, 
                   log_database_operation, log_error, log_info, log_warning, log_debug)

# Import admission notes window
from frontend.modules.admission_module import AdmissionNotesWindow


class IPDModule:
    """IPD (In-Patient Department) management interface"""
    
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
            text="IPD Management",
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
        self.search_var.trace('w', lambda *args: self.search_admissions())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 11), width=30, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground='#d1d5db', highlightcolor='#6366f1')
        search_entry.pack(side=tk.LEFT, padx=8)
        
        # Filter by status
        filter_frame = tk.Frame(top_frame, bg='#f5f7fa')
        filter_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(filter_frame, text="Status:", font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#374151').pack(side=tk.LEFT, padx=5)
        self.status_filter = tk.StringVar(value="All")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_filter, values=["All", "Admitted", "Discharged"], state="readonly", width=12)
        status_combo.pack(side=tk.LEFT, padx=5)
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_list())
        
        # Filter by date
        date_filter_frame = tk.Frame(top_frame, bg='#f5f7fa')
        date_filter_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(date_filter_frame, text="Date:", font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#374151').pack(side=tk.LEFT, padx=5)
        self.date_filter = tk.StringVar()
        date_entry = tk.Entry(date_filter_frame, textvariable=self.date_filter, font=('Segoe UI', 11), width=12, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground='#d1d5db', highlightcolor='#6366f1')
        date_entry.pack(side=tk.LEFT, padx=5)
        date_entry.bind('<KeyRelease>', lambda e: self.refresh_list())
        # Add placeholder text
        date_entry.insert(0, "YYYY-MM-DD")
        date_entry.config(fg='#9ca3af')
        
        def on_date_focus_in(event):
            if date_entry.get() == "YYYY-MM-DD":
                date_entry.delete(0, tk.END)
                date_entry.config(fg='#000000')
        
        def on_date_focus_out(event):
            if not date_entry.get().strip():
                date_entry.insert(0, "YYYY-MM-DD")
                date_entry.config(fg='#9ca3af')
                self.refresh_list()  # Refresh to show all when cleared
        
        date_entry.bind('<FocusIn>', on_date_focus_in)
        date_entry.bind('<FocusOut>', on_date_focus_out)
        
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
            current_date_str = self.date_filter.get()
            try:
                if current_date_str and current_date_str != "YYYY-MM-DD":
                    current_date = datetime.strptime(current_date_str, '%Y-%m-%d')
                else:
                    current_date = datetime.now()
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
                        current_selected_str = self.date_filter.get()
                        if current_selected_str and current_selected_str != "YYYY-MM-DD":
                            current_selected = datetime.strptime(current_selected_str, '%Y-%m-%d')
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
                self.date_filter.set(date_str)
                date_entry.config(fg='#000000')  # Change text color when date is selected
                calendar_window.destroy()
                self.refresh_list()
            
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
        
        # Add admission button with modern styling
        add_btn = tk.Button(
            top_frame,
            text="+ Admit Patient",
            command=self.admit_patient,
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
        
        # Use grid layout to ensure buttons are always visible
        content_container.grid_rowconfigure(0, weight=1)  # List frame gets expandable space
        content_container.grid_rowconfigure(1, weight=0)  # Action frame gets fixed space
        content_container.grid_columnconfigure(0, weight=1)
        
        # List frame - use grid to control space better
        list_frame = tk.Frame(content_container, bg='#f5f7fa')
        list_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        
        # Treeview for admissions list
        columns = ('Admission ID', 'Patient Name', 'Patient ID', 'Admission Date', 'Status', 'Ward', 'Bed', 'Doctor', 'Days')
        
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
        
        # Configure column widths
        column_widths = {
            'Admission ID': 150,
            'Patient Name': 200,
            'Patient ID': 150,
            'Admission Date': 130,
            'Status': 100,
            'Ward': 100,
            'Bed': 80,
            'Doctor': 180,
            'Days': 80
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 120), anchor='w')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Action buttons frame - ensure it's always visible at the bottom
        # Create a separator frame first
        separator = tk.Frame(content_container, bg='#d1d5db', height=2)
        separator.grid(row=1, column=0, sticky='ew', pady=(5, 10))
        
        action_frame = tk.Frame(content_container, bg='#ffffff', relief=tk.RAISED, bd=2)
        action_frame.grid(row=2, column=0, sticky='ew', pady=(0, 0))
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=0)
        
        # Left side buttons
        left_buttons = tk.Frame(action_frame, bg='#ffffff')
        left_buttons.grid(row=0, column=0, sticky='w', padx=10, pady=10)
        
        tk.Button(
            left_buttons,
            text="View Details",
            command=self.view_admission,
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
            left_buttons,
            text="📋 Daily Notes",
            command=self.open_daily_notes,
            font=('Segoe UI', 10, 'bold'),
            bg='#8b5cf6',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#7c3aed',
            activeforeground='white'
        ).pack(side=tk.LEFT, padx=6)
        
        # Right side buttons (Discharge and Refresh) - ensure they're visible
        right_buttons = tk.Frame(action_frame, bg='#ffffff')
        right_buttons.grid(row=0, column=1, sticky='e', padx=10, pady=10)
        
        # Store discharge button reference for enabling/disabling
        self.discharge_btn = tk.Button(
            right_buttons,
            text="🚪 Discharge Patient",
            command=self.discharge_admission,
            font=('Segoe UI', 12, 'bold'),
            bg='#ef4444',
            fg='white',
            padx=30,
            pady=12,
            cursor='hand2',
            relief=tk.RAISED,
            bd=2,
            activebackground='#dc2626',
            activeforeground='white'
        )
        self.discharge_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            right_buttons,
            text="Refresh",
            command=self.refresh_list,
            font=('Segoe UI', 10, 'bold'),
            bg='#6b7280',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#4b5563',
            activeforeground='white'
        ).pack(side=tk.LEFT, padx=6)
        
        # Add right-click context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="View Details", command=self.view_admission)
        self.context_menu.add_command(label="Daily Notes", command=self.open_daily_notes)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Discharge Patient", command=self.discharge_admission)
        
        def show_context_menu(event):
            """Show context menu on right-click"""
            selection = self.tree.selection()
            if selection:
                try:
                    self.context_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    self.context_menu.grab_release()
        
        self.tree.bind("<Button-3>", show_context_menu)  # Right-click on Windows
        self.tree.bind("<Button-2>", show_context_menu)  # Right-click on Mac/Linux
        
        # Update button states when selection changes
        def on_selection_change(event):
            """Update button states based on selected admission"""
            selection = self.tree.selection()
            if selection:
                item = self.tree.item(selection[0])
                values = item.get('values', [])
                if len(values) > 4:  # Status is 5th column (index 4)
                    status = values[4]
                    # Enable discharge only for admitted patients
                    if 'Admitted' in status or '🟢' in status:
                        self.discharge_btn.config(state=tk.NORMAL)
                    else:
                        self.discharge_btn.config(state=tk.DISABLED)
            else:
                self.discharge_btn.config(state=tk.NORMAL)  # Enable by default
        
        self.tree.bind("<<TreeviewSelect>>", on_selection_change)
    
    def refresh_list(self):
        """Refresh admissions list"""
        self.tree.delete(*self.tree.get_children())
        
        try:
            # Get all patients to get patient names
            all_patients = {p['patient_id']: f"{p['first_name']} {p['last_name']}" for p in self.db.get_all_patients()}
            
            # Get all admissions
            all_admissions = []
            all_patients_list = self.db.get_all_patients()
            
            for patient in all_patients_list:
                patient_admissions = self.db.get_admissions_by_patient(patient['patient_id'])
                for admission in patient_admissions:
                    admission['patient_name'] = f"{patient['first_name']} {patient['last_name']}"
                    admission['patient_id'] = patient['patient_id']
                    all_admissions.append(admission)
            
            # Sort by admission date (newest first)
            all_admissions.sort(key=lambda x: x.get('admission_date', ''), reverse=True)
            
            # Apply status filter
            status_filter = self.status_filter.get()
            if status_filter != "All":
                all_admissions = [a for a in all_admissions if a.get('status', '') == status_filter]
            
            # Apply date filter
            date_filter = self.date_filter.get().strip()
            if date_filter and date_filter != "YYYY-MM-DD":
                try:
                    # Validate date format
                    filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                    all_admissions = [a for a in all_admissions 
                                    if a.get('admission_date') and 
                                    datetime.strptime(a.get('admission_date'), '%Y-%m-%d').date() == filter_date]
                except ValueError:
                    # Invalid date format, ignore filter
                    pass
            
            # Calculate days admitted for active admissions
            for admission in all_admissions:
                admission_id = admission.get('admission_id', '')
                patient_name = admission.get('patient_name', 'Unknown')
                patient_id = admission.get('patient_id', '')
                admission_date = admission.get('admission_date', '')
                status = admission.get('status', 'Unknown')
                ward = admission.get('ward', '') or 'N/A'
                bed = admission.get('bed', '') or 'N/A'
                doctor_name = admission.get('doctor_name', '') or 'N/A'
                
                # Calculate days
                days = 'N/A'
                if status == 'Admitted' and admission_date:
                    try:
                        adm_date = datetime.strptime(admission_date, '%Y-%m-%d')
                        days_admitted = (datetime.now() - adm_date).days
                        days = f"Day {days_admitted + 1}" if days_admitted >= 0 else "Today"
                    except:
                        days = 'N/A'
                elif status == 'Discharged':
                    discharge_date = admission.get('discharge_date', '')
                    if discharge_date and admission_date:
                        try:
                            adm_date = datetime.strptime(admission_date, '%Y-%m-%d')
                            dis_date = datetime.strptime(discharge_date, '%Y-%m-%d')
                            days_admitted = (dis_date - adm_date).days
                            days = f"{days_admitted} days"
                        except:
                            days = 'N/A'
                
                # Color code status
                status_display = status
                if status == 'Admitted':
                    status_display = f"🟢 {status}"
                elif status == 'Discharged':
                    status_display = f"⚪ {status}"
                
                self.tree.insert('', tk.END, values=(
                    admission_id,
                    patient_name,
                    patient_id,
                    admission_date,
                    status_display,
                    ward,
                    bed,
                    doctor_name,
                    days
                ))
        except Exception as e:
            log_error("Failed to refresh admissions list", e)
            messagebox.showerror("Error", f"Failed to load admissions: {str(e)}")
    
    def search_admissions(self):
        """Search admissions"""
        query = self.search_var.get().lower()
        if not query:
            self.refresh_list()
            return
        
        # Get all items and filter
        all_items = self.tree.get_children()
        for item in all_items:
            values = self.tree.item(item, 'values')
            # Search in all columns
            search_text = ' '.join(str(v) for v in values).lower()
            if query in search_text:
                # Item matches, keep it visible (already in tree)
                pass
            else:
                # Item doesn't match, remove it
                self.tree.delete(item)
    
    def get_selected_admission_id(self):
        """Get selected admission ID"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an admission")
            return None
        item = self.tree.item(selection[0])
        return item['values'][0]  # Admission ID is first column
    
    def get_selected_patient_id(self):
        """Get selected patient ID"""
        selection = self.tree.selection()
        if not selection:
            return None
        item = self.tree.item(selection[0])
        return item['values'][2]  # Patient ID is third column
    
    def view_admission(self):
        """View admission details"""
        admission_id = self.get_selected_admission_id()
        if not admission_id:
            return
        
        try:
            # Get admission details
            all_patients = self.db.get_all_patients()
            admission = None
            patient = None
            
            for p in all_patients:
                admissions = self.db.get_admissions_by_patient(p['patient_id'])
                for adm in admissions:
                    if adm['admission_id'] == admission_id:
                        admission = adm
                        patient = p
                        break
                if admission:
                    break
            
            if not admission:
                messagebox.showerror("Error", "Admission not found")
                return
            
            # Create details window
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Admission Details - {admission_id}")
            details_window.geometry("600x500")
            details_window.configure(bg='#f5f7fa')
            details_window.transient(self.root)
            
            # Header
            header = tk.Label(
                details_window,
                text=f"Admission Details",
                font=('Segoe UI', 18, 'bold'),
                bg='#f5f7fa',
                fg='#1a237e'
            )
            header.pack(pady=20)
            
            # Details frame
            details_frame = tk.Frame(details_window, bg='#ffffff', relief=tk.FLAT, bd=1)
            details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            details_inner = tk.Frame(details_frame, bg='#ffffff')
            details_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Display details
            details = [
                ("Admission ID:", admission.get('admission_id', 'N/A')),
                ("Patient:", f"{patient.get('first_name', '')} {patient.get('last_name', '')} ({patient.get('patient_id', '')})"),
                ("Admission Date:", admission.get('admission_date', 'N/A')),
                ("Status:", admission.get('status', 'N/A')),
                ("Ward:", admission.get('ward', 'N/A') or 'N/A'),
                ("Bed:", admission.get('bed', 'N/A') or 'N/A'),
                ("Doctor:", admission.get('doctor_name', 'N/A') or 'N/A'),
                ("Expected Days:", str(admission.get('expected_days', 'N/A'))),
                ("Reason/Diagnosis:", admission.get('reason', 'N/A') or 'N/A'),
            ]
            
            if admission.get('discharge_date'):
                details.append(("Discharge Date:", admission.get('discharge_date', 'N/A')))
            if admission.get('discharge_summary'):
                details.append(("Discharge Summary:", admission.get('discharge_summary', 'N/A')))
            
            for i, (label, value) in enumerate(details):
                row = tk.Frame(details_inner, bg='#ffffff')
                row.pack(fill=tk.X, pady=8)
                
                tk.Label(
                    row,
                    text=label,
                    font=('Segoe UI', 11, 'bold'),
                    bg='#ffffff',
                    fg='#374151',
                    anchor='w',
                    width=20
                ).pack(side=tk.LEFT)
                
                tk.Label(
                    row,
                    text=str(value),
                    font=('Segoe UI', 11),
                    bg='#ffffff',
                    fg='#6b7280',
                    anchor='w',
                    wraplength=400
                ).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Close button
            tk.Button(
                details_window,
                text="Close",
                command=details_window.destroy,
                font=('Segoe UI', 10, 'bold'),
                bg='#6b7280',
                fg='white',
                padx=20,
                pady=8,
                cursor='hand2',
                relief=tk.FLAT,
                bd=0
            ).pack(pady=20)
            
        except Exception as e:
            log_error("Failed to view admission details", e)
            messagebox.showerror("Error", f"Failed to load admission details: {str(e)}")
    
    def open_daily_notes(self):
        """Open daily notes window for selected admission"""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return
        
        try:
            AdmissionNotesWindow(self.root, self.db, patient_id)
        except Exception as e:
            log_error("Failed to open daily notes", e)
            messagebox.showerror("Error", f"Failed to open daily notes: {str(e)}")
    
    def discharge_admission(self):
        """Discharge selected admission"""
        admission_id = self.get_selected_admission_id()
        if not admission_id:
            messagebox.showwarning("Warning", "Please select an admission to discharge")
            return
        
        # Get admission to check status
        all_patients = self.db.get_all_patients()
        admission = None
        
        for p in all_patients:
            admissions = self.db.get_admissions_by_patient(p['patient_id'])
            for adm in admissions:
                if adm['admission_id'] == admission_id:
                    admission = adm
                    break
            if admission:
                break
        
        if not admission:
            messagebox.showerror("Error", "Admission not found")
            return
        
        if admission.get('status') != 'Admitted':
            messagebox.showwarning("Warning", "This admission is already discharged. Only active admissions can be discharged.")
            return
        
        # Create discharge dialog
        discharge_window = tk.Toplevel(self.root)
        discharge_window.title("Discharge Patient")
        discharge_window.geometry("520x360")
        discharge_window.configure(bg="#f5f7fa")
        discharge_window.transient(self.root)
        discharge_window.lift()
        discharge_window.focus_force()
        
        frm = tk.Frame(discharge_window, bg="#f5f7fa")
        frm.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)
        
        tk.Label(frm, text=f"Admission: {admission_id}", font=("Segoe UI", 11, "bold"), bg="#f5f7fa", fg="#1a237e").pack(anchor="w", pady=(0, 10))
        
        row = tk.Frame(frm, bg="#f5f7fa")
        row.pack(fill=tk.X, pady=6)
        tk.Label(row, text="Discharge Date:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").pack(side=tk.LEFT)
        discharge_date_var = tk.StringVar(value=get_current_date())
        tk.Entry(row, textvariable=discharge_date_var, width=18).pack(side=tk.LEFT, padx=10)
        
        tk.Label(frm, text="Discharge Summary:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").pack(anchor="w", pady=(10, 4))
        summary = tk.Text(frm, height=8, width=48, wrap="word")
        summary.pack(fill=tk.BOTH, expand=True)
        
        btns = tk.Frame(frm, bg="#f5f7fa")
        btns.pack(fill=tk.X, pady=12)
        
        def do_discharge():
            try:
                ok = self.db.discharge_admission(
                    admission_id,
                    discharge_date=discharge_date_var.get().strip(),
                    discharge_summary=summary.get("1.0", "end").strip(),
                )
                if ok:
                    messagebox.showinfo("Success", "Patient discharged successfully")
                    discharge_window.destroy()
                    self.refresh_list()
                else:
                    messagebox.showerror("Error", "Failed to discharge")
            except Exception as e:
                log_error("Discharge failed", e)
                messagebox.showerror("Error", f"Failed to discharge: {e}")
        
        tk.Button(
            btns,
            text="Confirm Discharge",
            command=do_discharge,
            font=("Segoe UI", 10, "bold"),
            bg="#ef4444",
            fg="white",
            padx=16,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#dc2626",
            activeforeground="white",
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btns,
            text="Cancel",
            command=discharge_window.destroy,
            font=("Segoe UI", 10, "bold"),
            bg="#6b7280",
            fg="white",
            padx=16,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#4b5563",
            activeforeground="white",
        ).pack(side=tk.LEFT, padx=8)
    
    def admit_patient(self):
        """Open dialog to admit a new patient"""
        # Create patient selection dialog
        select_window = tk.Toplevel(self.root)
        select_window.title("Admit Patient")
        select_window.geometry("600x500")
        select_window.configure(bg="#f5f7fa")
        select_window.transient(self.root)
        select_window.lift()
        select_window.focus_force()
        
        header = tk.Label(
            select_window,
            text="Select Patient to Admit",
            font=("Segoe UI", 16, "bold"),
            bg="#f5f7fa",
            fg="#1a237e",
        )
        header.pack(pady=16)
        
        # Search frame
        search_frame = tk.Frame(select_window, bg="#f5f7fa")
        search_frame.pack(fill=tk.X, padx=18, pady=(0, 10))
        
        tk.Label(search_frame, text="Search:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").pack(side=tk.LEFT, padx=(0, 8))
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=8)
        
        # Patient list
        list_frame = tk.Frame(select_window, bg="#f5f7fa")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=10)
        
        columns = ('ID', 'Name', 'DOB', 'Gender', 'Phone')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='w')
        
        tree.column('ID', width=150)
        tree.column('Name', width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def load_patients():
            tree.delete(*tree.get_children())
            patients = self.db.get_all_patients()
            query = search_var.get().lower()
            
            for patient in patients:
                if query and query not in f"{patient['patient_id']} {patient['first_name']} {patient['last_name']}".lower():
                    continue
                
                # Check if patient already has active admission
                active_adm = self.db.get_active_admission_by_patient(patient['patient_id'])
                if active_adm:
                    continue  # Skip patients with active admissions
                
                tree.insert('', tk.END, values=(
                    patient['patient_id'],
                    f"{patient['first_name']} {patient['last_name']}",
                    patient.get('date_of_birth', ''),
                    patient.get('gender', ''),
                    patient.get('phone', '')
                ))
        
        search_var.trace('w', lambda *args: load_patients())
        load_patients()
        
        def proceed_to_admit():
            try:
                selection = tree.selection()
                if not selection:
                    messagebox.showwarning("Warning", "Please select a patient from the list")
                    return
                
                item = tree.item(selection[0])
                values = item.get('values', [])
                if not values or len(values) == 0:
                    messagebox.showwarning("Warning", "Invalid patient selection")
                    return
                
                patient_id = values[0]  # Patient ID is first column
                if not patient_id:
                    messagebox.showwarning("Warning", "Could not get patient ID")
                    return
                
                log_info(f"Proceeding to admit patient: {patient_id}")
                select_window.destroy()
                
                # Open admission dialog
                self._open_admit_dialog(patient_id)
            except Exception as e:
                log_error("Error in proceed_to_admit", e)
                messagebox.showerror("Error", f"Failed to proceed: {str(e)}")
        
        # Add double-click handler for tree
        def on_double_click(event):
            proceed_to_admit()
        
        tree.bind('<Double-1>', on_double_click)
        
        # Buttons
        btn_frame = tk.Frame(select_window, bg="#f5f7fa")
        btn_frame.pack(fill=tk.X, padx=18, pady=10)
        
        tk.Button(
            btn_frame,
            text="Admit Selected Patient",
            command=proceed_to_admit,
            font=("Segoe UI", 10, "bold"),
            bg="#10b981",
            fg="white",
            padx=16,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#059669",
            activeforeground="white"
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=select_window.destroy,
            font=("Segoe UI", 10, "bold"),
            bg="#6b7280",
            fg="white",
            padx=16,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=8)
    
    def _open_admit_dialog(self, patient_id: str):
        """Open admission dialog for a specific patient"""
        try:
            log_info(f"Opening admit dialog for patient: {patient_id}")
            patient = self.db.get_patient_by_id(patient_id)
            if not patient:
                messagebox.showerror("Error", f"Patient not found: {patient_id}")
                return
            
            # Check for active admission
            active = self.db.get_active_admission_by_patient(patient_id)
            if active:
                messagebox.showwarning("Already Admitted", f"Patient already has an active admission: {active['admission_id']}")
                return
            
            dialog = tk.Toplevel(self.root)
            dialog.title("Admit Patient (IPD)")
            dialog.geometry("520x420")
            dialog.configure(bg="#f5f7fa")
            dialog.transient(self.root)
            dialog.lift()
            dialog.focus_force()
            dialog.grab_set()  # Make dialog modal
            
            frm = tk.Frame(dialog, bg="#f5f7fa")
            frm.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)
            
            # Patient context (read-only)
            patient_name = f"{patient.get('first_name','')} {patient.get('last_name','')}".strip()
            if not patient_name:
                patient_name = "(Unknown)"
            tk.Label(
                frm,
                text=f"Patient: {patient_name} ({patient_id})",
                font=("Segoe UI", 11, "bold"),
                bg="#f5f7fa",
                fg="#1a237e",
            ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
            
            doctors = self.db.get_all_doctors()
            doctor_labels = ["(None)"] + [f"{d['doctor_id']} - Dr. {d['first_name']} {d['last_name']}" for d in doctors]
            
            tk.Label(frm, text="Assigned Doctor (optional):", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").grid(row=1, column=0, sticky="w", pady=8)
            doctor_var = tk.StringVar(value=doctor_labels[0])
            doctor_combo = ttk.Combobox(frm, textvariable=doctor_var, values=doctor_labels, state="readonly", width=34)
            doctor_combo.grid(row=1, column=1, sticky="w", pady=8)
            
            tk.Label(frm, text="Admission Date:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").grid(row=2, column=0, sticky="w", pady=8)
            adm_date_var = tk.StringVar(value=get_current_date())
            tk.Entry(frm, textvariable=adm_date_var, width=18).grid(row=2, column=1, sticky="w", pady=8)
            
            tk.Label(frm, text="Expected Days:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").grid(row=3, column=0, sticky="w", pady=8)
            exp_days_var = tk.StringVar(value="3")
            tk.Entry(frm, textvariable=exp_days_var, width=10).grid(row=3, column=1, sticky="w", pady=8)
            
            tk.Label(frm, text="Ward:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").grid(row=4, column=0, sticky="w", pady=8)
            ward_var = tk.StringVar()
            tk.Entry(frm, textvariable=ward_var, width=22).grid(row=4, column=1, sticky="w", pady=8)
            
            tk.Label(frm, text="Bed:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").grid(row=5, column=0, sticky="w", pady=8)
            bed_var = tk.StringVar()
            tk.Entry(frm, textvariable=bed_var, width=22).grid(row=5, column=1, sticky="w", pady=8)
            
            tk.Label(frm, text="Reason / Diagnosis:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").grid(row=6, column=0, sticky="nw", pady=8)
            reason_txt = tk.Text(frm, height=5, width=34, wrap="word")
            reason_txt.grid(row=6, column=1, sticky="w", pady=8)
            
            btns = tk.Frame(frm, bg="#f5f7fa")
            btns.grid(row=7, column=0, columnspan=2, sticky="w", pady=(14, 0))
            
            def do_save():
                try:
                    doctor_id = None
                    if doctor_var.get() != "(None)":
                        doctor_id = doctor_var.get().split(" - ", 1)[0].strip()
                    
                    admission_id = generate_id("ADM")
                    data = {
                        "admission_id": admission_id,
                        "patient_id": patient_id,
                        "doctor_id": doctor_id,
                        "admission_date": adm_date_var.get().strip(),
                        "expected_days": exp_days_var.get().strip(),
                        "ward": ward_var.get().strip(),
                        "bed": bed_var.get().strip(),
                        "reason": reason_txt.get("1.0", "end").strip(),
                    }
                    
                    if not data["admission_date"]:
                        messagebox.showerror("Error", "Admission date is required")
                        return
                    
                    ok = self.db.add_admission(data)
                    if ok:
                        log_info(f"Admitted patient {patient_id} => {admission_id}")
                        messagebox.showinfo("Success", f"Patient admitted: {admission_id}")
                        dialog.destroy()
                        self.refresh_list()
                    else:
                        messagebox.showerror("Error", "Failed to admit patient")
                except Exception as e:
                    log_error("Admit failed", e)
                    messagebox.showerror("Error", f"Failed to admit patient: {e}")
            
            tk.Button(
                btns,
                text="Save Admission",
                command=do_save,
                font=("Segoe UI", 10, "bold"),
                bg="#10b981",
                fg="white",
                padx=16,
                pady=8,
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                activebackground="#059669",
                activeforeground="white",
            ).pack(side=tk.LEFT)
            
            tk.Button(
                btns,
                text="Cancel",
                command=dialog.destroy,
                font=("Segoe UI", 10, "bold"),
                bg="#6b7280",
                fg="white",
                padx=16,
                pady=8,
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                activebackground="#4b5563",
                activeforeground="white",
            ).pack(side=tk.LEFT, padx=8)
            
            # Ensure dialog is visible
            dialog.update_idletasks()
            log_info(f"Admit dialog opened for patient: {patient_id}")
        except Exception as e:
            log_error("Failed to open admit dialog", e)
            messagebox.showerror("Error", f"Failed to open admission dialog: {str(e)}")

