"""
Appointment Management Module
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Backend imports
from backend.database import Database

# Utils imports
from utils.helpers import generate_id, get_current_date, get_current_datetime


class AppointmentModule:
    """Appointment management interface"""
    
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
            text="Appointment Management",
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
        self.patient_name_var = tk.StringVar()
        self.patient_name_var.trace('w', lambda *args: self.apply_filters())
        patient_name_entry = tk.Entry(filter_frame, textvariable=self.patient_name_var, font=('Segoe UI', 10), width=20, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground='#d1d5db', highlightcolor='#6366f1')
        patient_name_entry.pack(side=tk.LEFT, padx=5)
        
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
        
        # Status filter
        tk.Label(filter_frame, text="Status:", font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#374151').pack(side=tk.LEFT, padx=(10, 5))
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=["All", "Scheduled", "Completed", "Cancelled"],
            font=('Segoe UI', 10),
            width=12,
            state='readonly'
        )
        status_combo.pack(side=tk.LEFT, padx=5)
        # Auto-filter when status changes
        self.status_var.trace('w', lambda *args: self.apply_filters())
        
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
        
        # Action buttons with modern styling - Doctor-friendly (BEFORE list so they're visible)
        action_frame = tk.Frame(self.parent, bg='#f5f7fa')
        action_frame.pack(fill=tk.X, padx=25, pady=15)
        
        # Label for quick actions
        tk.Label(
            action_frame,
            text="Quick Actions:",
            font=('Segoe UI', 11, 'bold'),
            bg='#f5f7fa',
            fg='#374151'
        ).pack(side=tk.LEFT, padx=(0, 15))
        
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
            text="✏️ Edit Appointment",
            command=self.edit_appointment,
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
        
        tk.Button(
            action_frame,
            text="Delete",
            command=self.delete_appointment,
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
        
        tk.Button(
            action_frame,
            text="✅ Mark Complete",
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
            text="❌ Cancel Appointment",
            command=self.cancel_appointment,
            font=('Segoe UI', 10, 'bold'),
            bg='#f97316',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#ea580c',
            activeforeground='white'
        ).pack(side=tk.LEFT, padx=6)
        
        # List frame (AFTER action buttons)
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
    
    def refresh_list(self):
        """Refresh appointment list (shows all appointments)"""
        # Reset filters to show all
        self.patient_name_var.set("")
        self.date_var.set("")
        self.status_var.set("All")
        
        # apply_filters will be called automatically via trace
        self.apply_filters()
    
    def filter_by_date(self):
        """Filter appointments by date (deprecated - use apply_filters instead)"""
        self.apply_filters()
    
    def apply_filters(self, *args):
        """Apply patient name, date and status filters automatically"""
        self.tree.delete(*self.tree.get_children())
        
        patient_name = self.patient_name_var.get().strip()
        date = self.date_var.get().strip()
        status = self.status_var.get()
        
        # Determine which filter combination to apply
        has_patient = patient_name and patient_name != ""
        has_date = date and date != ""
        has_status = status != "All"
        
        if has_patient and has_date and has_status:
            # All three filters
            appointments = self.db.get_appointments_by_patient_name_date_and_status(patient_name, date, status)
        elif has_patient and has_date:
            # Patient name and date
            appointments = self.db.get_appointments_by_patient_name_and_date(patient_name, date)
        elif has_patient and has_status:
            # Patient name and status
            appointments = self.db.get_appointments_by_patient_name_and_status(patient_name, status)
        elif has_patient:
            # Patient name only
            appointments = self.db.get_appointments_by_patient_name(patient_name)
        elif has_date and has_status:
            # Date and status
            appointments = self.db.get_appointments_by_date_and_status(date, status)
        elif has_date:
            # Date only
            appointments = self.db.get_appointments_by_date(date)
        elif has_status:
            # Status only
            appointments = self.db.get_appointments_by_status(status)
        else:
            # No filters - show all
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
    
    def show_appointment_selection_popup(self, title, action_callback):
        """Show popup to select an appointment"""
        popup = tk.Toplevel(self.parent)
        popup.title(title)
        popup.geometry("1000x650")
        popup.configure(bg='#f5f7fa')
        popup.transient(self.parent)
        popup.grab_set()
        
        # Center the window
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (1000 // 2)
        y = (popup.winfo_screenheight() // 2) - (650 // 2)
        popup.geometry(f"1000x650+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(popup, bg='#1e40af', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text=title,
            font=('Segoe UI', 14, 'bold'),
            bg='#1e40af',
            fg='white'
        ).pack(pady=18)
        
        # Search frame
        search_frame = tk.Frame(popup, bg='#f5f7fa', padx=20, pady=15)
        search_frame.pack(fill=tk.X)
        
        tk.Label(
            search_frame,
            text="Search by Patient Name, Doctor, or Date:",
            font=('Segoe UI', 10, 'bold'),
            bg='#f5f7fa',
            fg='#374151'
        ).pack(side=tk.LEFT, padx=5)
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=search_var,
            font=('Segoe UI', 10),
            width=30,
            relief=tk.FLAT,
            bd=2,
            highlightthickness=1,
            highlightbackground='#d1d5db',
            highlightcolor='#6366f1'
        )
        search_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True, ipady=5)
        search_entry.focus_set()
        
        # Appointment list
        list_frame = tk.Frame(popup, bg='#f5f7fa', padx=20, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Patient', 'Doctor', 'Date', 'Time', 'Status', 'Reason')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            if col == 'ID':
                tree.column(col, width=150)
            elif col in ['Patient', 'Doctor']:
                tree.column(col, width=180)
            elif col == 'Date':
                tree.column(col, width=120)
            elif col == 'Time':
                tree.column(col, width=100)
            elif col == 'Status':
                tree.column(col, width=120)
            else:
                tree.column(col, width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def load_appointments():
            """Load appointments based on search"""
            tree.delete(*tree.get_children())
            search_text = search_var.get().strip().lower()
            
            try:
                all_appointments = self.db.get_all_appointments()
                for apt in all_appointments:
                    patient_name = apt.get('patient_name', apt.get('patient_id', 'Unknown'))
                    doctor_name = apt.get('doctor_name', apt.get('doctor_id', 'Unknown'))
                    date = apt.get('appointment_date', '')
                    time = apt.get('appointment_time', '')
                    status = apt.get('status', 'Scheduled')
                    reason = apt.get('reason', '')
                    
                    if (not search_text or 
                        search_text in apt.get('appointment_id', '').lower() or
                        search_text in patient_name.lower() or
                        search_text in doctor_name.lower() or
                        search_text in date.lower() or
                        search_text in status.lower()):
                        tree.insert('', tk.END, values=(
                            apt['appointment_id'],
                            patient_name,
                            doctor_name,
                            date,
                            time,
                            status,
                            reason[:50] + '...' if len(reason) > 50 else reason
                        ))
            except Exception as e:
                print(f"Error loading appointments: {e}")
        
        search_var.trace('w', lambda *args: load_appointments())
        load_appointments()  # Initial load
        
        # Button frame
        button_frame = tk.Frame(popup, bg='#f5f7fa', padx=20, pady=15)
        button_frame.pack(fill=tk.X)
        
        def on_select():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an appointment")
                return
            
            item = tree.item(selection[0])
            appointment_id = item['values'][0]
            popup.destroy()
            action_callback(appointment_id)
        
        # Bind double-click to select
        tree.bind('<Double-1>', lambda e: on_select())
        
        select_btn = tk.Button(
            button_frame,
            text="Select",
            command=on_select,
            font=('Segoe UI', 10, 'bold'),
            bg='#10b981',
            fg='white',
            padx=30,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#059669'
        )
        select_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
            font=('Segoe UI', 10),
            bg='#6b7280',
            fg='white',
            padx=30,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#4b5563'
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to select
        search_entry.bind('<Return>', lambda e: on_select())
        popup.bind('<Return>', lambda e: on_select())
    
    def edit_appointment(self):
        """Edit selected appointment - opens in EDIT mode"""
        appointment_id = self.get_selected_appointment_id()
        if not appointment_id:
            # If no selection, show selection popup
            self.show_appointment_selection_popup(
                "Select Appointment to Edit",
                lambda aid: self.edit_appointment_by_id(aid)
            )
            return
        
        # Directly edit the selected appointment
        self.edit_appointment_by_id(appointment_id)
    
    def edit_appointment_by_id(self, appointment_id):
        """Edit appointment by ID - explicitly opens in EDIT mode"""
        appointment = self.db.get_appointment_by_id(appointment_id)
        if not appointment:
            messagebox.showerror("Error", "Appointment not found")
            return
        
        # Explicitly pass view_only=False to ensure fields are editable
        self.appointment_dialog(appointment, view_only=False)
    
    def mark_complete(self):
        """Mark selected appointment as complete"""
        appointment_id = self.get_selected_appointment_id()
        if not appointment_id:
            return
        
        appointment = self.db.get_appointment_by_id(appointment_id)
        if not appointment:
            messagebox.showerror("Error", "Appointment not found")
            return
        
        # Get appointment details for confirmation
        patient_name = appointment.get('patient_name', appointment.get('patient_id', 'Unknown'))
        date = appointment.get('appointment_date', '')
        time = appointment.get('appointment_time', '')
        
        # Confirm before marking as complete
        confirm_msg = f"Mark this appointment as COMPLETED?\n\n"
        confirm_msg += f"Patient: {patient_name}\n"
        confirm_msg += f"Date: {date}\n"
        confirm_msg += f"Time: {time}\n"
        
        if messagebox.askyesno("Confirm", confirm_msg):
            try:
                if self.db.update_appointment(appointment_id, {'status': 'Completed'}):
                    messagebox.showinfo("Success", "Appointment marked as completed successfully")
                    self.refresh_list()
                else:
                    messagebox.showerror("Error", "Failed to update appointment status")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to mark appointment as complete: {str(e)}")
    
    def delete_appointment(self):
        """Delete selected appointment"""
        appointment_id = self.get_selected_appointment_id()
        if not appointment_id:
            # If no selection, show selection popup
            self.show_appointment_selection_popup(
                "Select Appointment to Delete",
                lambda aid: self.delete_appointment_by_id(aid)
            )
            return
        
        # Directly delete the selected appointment
        self.delete_appointment_by_id(appointment_id)
    
    def delete_appointment_by_id(self, appointment_id):
        """Delete appointment by ID"""
        appointment = self.db.get_appointment_by_id(appointment_id)
        if not appointment:
            messagebox.showerror("Error", "Appointment not found")
            return
        
        # Show confirmation with appointment details
        patient_name = appointment.get('patient_name', appointment.get('patient_id', 'Unknown'))
        date = appointment.get('appointment_date', '')
        time = appointment.get('appointment_time', '')
        
        confirm_msg = f"Are you sure you want to DELETE this appointment?\n\n"
        confirm_msg += f"Patient: {patient_name}\n"
        confirm_msg += f"Date: {date}\n"
        confirm_msg += f"Time: {time}\n\n"
        confirm_msg += "This action cannot be undone!"
        
        if messagebox.askyesno("Confirm Delete", confirm_msg, icon='warning'):
            try:
                # Try to delete from database
                if hasattr(self.db, 'delete_appointment'):
                    if self.db.delete_appointment(appointment_id):
                        messagebox.showinfo("Success", "Appointment deleted successfully")
                        self.refresh_list()
                    else:
                        messagebox.showerror("Error", "Failed to delete appointment")
                else:
                    # If delete method doesn't exist, update status to cancelled
                    if self.db.update_appointment(appointment_id, {'status': 'Cancelled'}):
                        messagebox.showinfo("Success", "Appointment cancelled successfully")
                        self.refresh_list()
                    else:
                        messagebox.showerror("Error", "Failed to cancel appointment")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete appointment: {str(e)}")
    
    def cancel_appointment(self):
        """Cancel appointment (change status to Cancelled)"""
        appointment_id = self.get_selected_appointment_id()
        if not appointment_id:
            return
        
        appointment = self.db.get_appointment_by_id(appointment_id)
        if not appointment:
            messagebox.showerror("Error", "Appointment not found")
            return
        
        if messagebox.askyesno("Confirm", "Cancel this appointment? Status will be changed to 'Cancelled'."):
            try:
                if self.db.update_appointment(appointment_id, {'status': 'Cancelled'}):
                    messagebox.showinfo("Success", "Appointment cancelled successfully")
                    self.refresh_list()
                else:
                    messagebox.showerror("Error", "Failed to cancel appointment")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel appointment: {str(e)}")
    
    def appointment_dialog(self, appointment=None, view_only=False):
        """Appointment form dialog"""
        dialog = tk.Toplevel(self.parent)
        # Set title based on mode
        if view_only:
            dialog.title("View Appointment Details")
        elif appointment:
            dialog.title("Edit Appointment - Editable")
        else:
            dialog.title("Schedule Appointment")
        dialog.geometry("550x600")  # Increased height to accommodate status field
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
        
        # Main content frame
        main_frame = tk.Frame(dialog, bg='#f5f7fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        fields_frame = tk.Frame(main_frame, bg='#f5f7fa')
        fields_frame.pack(fill=tk.X, expand=False, pady=10)
        
        # Add mode indicator
        if view_only:
            mode_label = tk.Label(fields_frame, text="📖 VIEW MODE (Read Only)", 
                                 font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#ef4444')
            mode_label.pack(pady=5)
        elif appointment:
            mode_label = tk.Label(fields_frame, text="✏️ EDIT MODE (Editable)", 
                                 font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#10b981')
            mode_label.pack(pady=5)
        
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
        # Set state based on view_only
        combo_state = 'readonly' if view_only else 'normal'
        patient_combo = ttk.Combobox(
            fields_frame, 
            textvariable=patient_var,
            values=patient_options,
            font=('Arial', 10),
            width=37,
            state=combo_state
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
            state=combo_state
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
        
        # Date with calendar button
        tk.Label(fields_frame, text="Date (YYYY-MM-DD) *:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        date_frame = tk.Frame(fields_frame, bg='#f5f7fa')
        date_frame.pack(fill=tk.X, pady=5)
        # Set entry state based on view_only
        entry_state = 'readonly' if view_only else 'normal'
        date_entry = tk.Entry(date_frame, font=('Arial', 10), width=35, state=entry_state)
        if appointment:
            date_entry.insert(0, appointment.get('appointment_date', get_current_date()))
        else:
            date_entry.insert(0, get_current_date())
        date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def open_calendar_for_date():
            """Open calendar for date entry"""
            calendar_window = tk.Toplevel(dialog)
            calendar_window.title("Select Date")
            calendar_window.geometry("300x280")
            calendar_window.configure(bg='#ffffff')
            calendar_window.transient(dialog)
            calendar_window.grab_set()
            
            # Position calendar below the date entry field
            calendar_window.update_idletasks()
            # Get the position of the date entry field
            date_entry.update_idletasks()
            dialog_x = dialog.winfo_rootx()
            dialog_y = dialog.winfo_rooty()
            entry_x = date_entry.winfo_x()
            entry_y = date_entry.winfo_y()
            entry_width = date_entry.winfo_width()
            entry_height = date_entry.winfo_height()
            
            # Position below the date entry field
            x = dialog_x + entry_x
            y = dialog_y + entry_y + entry_height + 5  # 5 pixels below
            
            # Make sure calendar doesn't go off screen
            screen_width = calendar_window.winfo_screenwidth()
            screen_height = calendar_window.winfo_screenheight()
            if x + 300 > screen_width:
                x = screen_width - 300 - 10
            if y + 280 > screen_height:
                y = dialog_y + entry_y - 280 - 5  # Show above if no space below
            
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
        
        date_cal_btn = tk.Button(
            date_frame,
            text="📅",
            command=open_calendar_for_date if not view_only else lambda: None,
            font=('Segoe UI', 12),
            bg='#3b82f6',
            fg='white',
            width=3,
            relief=tk.FLAT,
            cursor='hand2' if not view_only else 'arrow',
            padx=5,
            state='normal' if not view_only else 'disabled'
        )
        date_cal_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Time with clock button
        tk.Label(fields_frame, text="Time (HH:MM) *:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        time_frame = tk.Frame(fields_frame, bg='#f5f7fa')
        time_frame.pack(fill=tk.X, pady=5)
        time_entry = tk.Entry(time_frame, font=('Arial', 10), width=35, state=entry_state)
        if appointment:
            time_entry.insert(0, appointment.get('appointment_time', ''))
        time_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def open_time_picker():
            """Open time picker dialog"""
            time_window = tk.Toplevel(dialog)
            time_window.title("Select Time")
            time_window.geometry("280x350")
            time_window.configure(bg='#ffffff')
            time_window.transient(dialog)
            time_window.grab_set()
            
            # Center the window
            time_window.update_idletasks()
            x = (time_window.winfo_screenwidth() // 2) - (280 // 2)
            y = (time_window.winfo_screenheight() // 2) - (350 // 2)
            time_window.geometry(f"280x350+{x}+{y}")
            
            # Header
            header_frame = tk.Frame(time_window, bg='#1e40af', height=40)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            tk.Label(
                header_frame,
                text="Select Time",
                font=('Segoe UI', 12, 'bold'),
                bg='#1e40af',
                fg='white'
            ).pack(pady=10)
            
            # Time picker frame
            time_picker_frame = tk.Frame(time_window, bg='#ffffff')
            time_picker_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Get current time from entry or use current time
            current_time_str = time_entry.get()
            try:
                if current_time_str:
                    time_parts = current_time_str.split(':')
                    current_hour = int(time_parts[0])
                    current_minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                else:
                    now = datetime.now()
                    current_hour = now.hour
                    current_minute = now.minute
            except:
                now = datetime.now()
                current_hour = now.hour
                current_minute = now.minute
            
            # Variables for hour and minute
            hour_var = tk.IntVar(value=current_hour)
            minute_var = tk.IntVar(value=current_minute)
            
            # Hour selection
            hour_frame = tk.Frame(time_picker_frame, bg='#ffffff')
            hour_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(
                hour_frame,
                text="Hour:",
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#374151'
            ).pack(side=tk.LEFT, padx=5)
            
            hour_spinbox = tk.Spinbox(
                hour_frame,
                from_=0,
                to=23,
                textvariable=hour_var,
                font=('Segoe UI', 12),
                width=5,
                justify=tk.CENTER,
                relief=tk.SOLID,
                bd=1
            )
            hour_spinbox.pack(side=tk.LEFT, padx=10)
            
            # Minute selection
            minute_frame = tk.Frame(time_picker_frame, bg='#ffffff')
            minute_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(
                minute_frame,
                text="Minute:",
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#374151'
            ).pack(side=tk.LEFT, padx=5)
            
            minute_spinbox = tk.Spinbox(
                minute_frame,
                from_=0,
                to=59,
                textvariable=minute_var,
                font=('Segoe UI', 12),
                width=5,
                justify=tk.CENTER,
                relief=tk.SOLID,
                bd=1,
                increment=5
            )
            minute_spinbox.pack(side=tk.LEFT, padx=10)
            
            # Quick time buttons
            quick_times_frame = tk.Frame(time_picker_frame, bg='#ffffff')
            quick_times_frame.pack(fill=tk.X, pady=20)
            
            tk.Label(
                quick_times_frame,
                text="Quick Select:",
                font=('Segoe UI', 10, 'bold'),
                bg='#ffffff',
                fg='#6b7280'
            ).pack(anchor='w', pady=(0, 5))
            
            quick_times = [
                ("09:00", "9:00 AM"),
                ("10:00", "10:00 AM"),
                ("11:00", "11:00 AM"),
                ("12:00", "12:00 PM"),
                ("13:00", "1:00 PM"),
                ("14:00", "2:00 PM"),
                ("15:00", "3:00 PM"),
                ("16:00", "4:00 PM"),
                ("17:00", "5:00 PM")
            ]
            
            quick_buttons_frame = tk.Frame(quick_times_frame, bg='#ffffff')
            quick_buttons_frame.pack(fill=tk.X)
            
            for i, (time_val, time_label) in enumerate(quick_times):
                btn = tk.Button(
                    quick_buttons_frame,
                    text=time_label,
                    command=lambda t=time_val: select_time_from_quick(t),
                    font=('Segoe UI', 9),
                    bg='#e5e7eb',
                    fg='#374151',
                    relief=tk.FLAT,
                    cursor='hand2',
                    padx=8,
                    pady=5
                )
                btn.grid(row=i // 3, column=i % 3, padx=3, pady=3, sticky='ew')
                quick_buttons_frame.columnconfigure(i % 3, weight=1)
            
            def select_time_from_quick(time_str):
                """Select time from quick buttons"""
                time_parts = time_str.split(':')
                hour_var.set(int(time_parts[0]))
                minute_var.set(int(time_parts[1]))
                select_time()
            
            def select_time():
                """Select the time"""
                hour = hour_var.get()
                minute = minute_var.get()
                time_str = f"{hour:02d}:{minute:02d}"
                time_entry.delete(0, tk.END)
                time_entry.insert(0, time_str)
                time_window.destroy()
            
            # Button frame
            btn_frame = tk.Frame(time_window, bg='#ffffff')
            btn_frame.pack(fill=tk.X, padx=10, pady=10)
            
            now_btn = tk.Button(
                btn_frame,
                text="Now",
                command=lambda: select_time_from_quick(datetime.now().strftime('%H:%M')),
                font=('Segoe UI', 9),
                bg='#3b82f6',
                fg='white',
                padx=15,
                pady=5,
                relief=tk.FLAT,
                cursor='hand2'
            )
            now_btn.pack(side=tk.LEFT, padx=5)
            
            ok_btn = tk.Button(
                btn_frame,
                text="OK",
                command=select_time,
                font=('Segoe UI', 9, 'bold'),
                bg='#10b981',
                fg='white',
                padx=20,
                pady=5,
                relief=tk.FLAT,
                cursor='hand2'
            )
            ok_btn.pack(side=tk.RIGHT, padx=5)
            
            cancel_btn = tk.Button(
                btn_frame,
                text="Cancel",
                command=time_window.destroy,
                font=('Segoe UI', 9),
                bg='#6b7280',
                fg='white',
                padx=15,
                pady=5,
                relief=tk.FLAT,
                cursor='hand2'
            )
            cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        time_clock_btn = tk.Button(
            time_frame,
            text="🕐",
            command=open_time_picker if not view_only else lambda: None,
            font=('Segoe UI', 12),
            bg='#3b82f6',
            fg='white',
            width=3,
            relief=tk.FLAT,
            cursor='hand2' if not view_only else 'arrow',
            padx=5,
            state='normal' if not view_only else 'disabled'
        )
        time_clock_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Notes
        tk.Label(fields_frame, text="Notes:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        notes_text = tk.Text(fields_frame, font=('Arial', 10), width=40, height=4, state=entry_state)
        if appointment:
            notes_text.insert('1.0', appointment.get('notes', ''))
            if view_only:
                notes_text.config(state='disabled')
        notes_text.pack(fill=tk.X, pady=5)
        
        # Status dropdown (only shown when editing)
        status_var = tk.StringVar()
        status_combo = None  # Initialize variable
        if appointment:
            tk.Label(fields_frame, text="Status *:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
            # Set current status
            current_status = appointment.get('status', 'Scheduled')
            status_var.set(current_status)
            
            # Create a frame for the status selector
            status_selector_frame = tk.Frame(fields_frame, bg='#f5f7fa')
            status_selector_frame.pack(fill=tk.X, pady=5)
            
            if view_only:
                # For view mode, use a label instead of menubutton
                status_label = tk.Label(
                    status_selector_frame,
                    text=current_status,
                    font=('Arial', 10),
                    bg='#f9fafb',
                    fg='#374151',
                    relief=tk.SOLID,
                    borderwidth=1,
                    anchor='w',
                    padx=10,
                    pady=5
                )
                status_label.pack(fill=tk.X, expand=True)
            else:
                # Use Menubutton for more reliable dropdown behavior
                status_menu_btn = tk.Menubutton(
                    status_selector_frame,
                    textvariable=status_var,
                    font=('Arial', 10),
                    width=35,
                    relief=tk.SOLID,
                    borderwidth=1,
                    bg='white',
                    activebackground='#e5e7eb',
                    anchor='w'
                )
                status_menu_btn.pack(fill=tk.X, expand=True)
                
                # Create the menu
                status_menu = tk.Menu(status_menu_btn, tearoff=0)
                status_menu_btn.config(menu=status_menu)
                
                # Add menu items
                for status_option in ["Scheduled", "Completed", "Cancelled"]:
                    status_menu.add_command(
                        label=status_option,
                        command=lambda s=status_option: status_var.set(s)
                    )
        else:
            # For new appointments, status is always 'Scheduled'
            status_var.set('Scheduled')
        
        # Populate patient and doctor fields if editing
        if appointment:
            # Set patient
            patient_id = appointment.get('patient_id', '')
            for display_text, pid in patient_id_map.items():
                if pid == patient_id:
                    patient_var.set(display_text)
                    break
            
            # Set doctor
            doctor_id = appointment.get('doctor_id', '')
            for display_text, did in doctor_id_map.items():
                if did == doctor_id:
                    doctor_var.set(display_text)
                    break
        
        # Button frame - only show save button if not view_only
        if not view_only:
            button_frame = tk.Frame(dialog, bg='#f5f7fa', relief=tk.FLAT, bd=0)
            button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)
            
            # Inner frame for button spacing
            inner_button_frame = tk.Frame(button_frame, bg='#f5f7fa')
            inner_button_frame.pack(padx=25, pady=20)
        
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
            
            # Determine if we're adding or updating
            is_edit = appointment is not None
            success = False
            success_message = ""
            
            if is_edit:
                # Update existing appointment
                # Use status from dropdown
                data['status'] = status_var.get()
                success = self.db.update_appointment(appointment_id, data)
                success_message = "Appointment updated successfully!"
            else:
                # Add new appointment
                data['status'] = status_var.get()  # Always 'Scheduled' for new appointments
                success = self.db.add_appointment(data)
                success_message = "Appointment scheduled successfully!"
            
            if success:
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
                root.after(150, lambda: messagebox.showinfo("Success", success_message))
                # Refresh list asynchronously
                root.after(250, self.refresh_list)
            else:
                error_message = "Failed to update appointment" if is_edit else "Failed to schedule appointment"
                messagebox.showerror("Error", error_message)
        
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
        
        # Only show save button if not in view_only mode
        if not view_only:
            button_text = "Update Appointment" if appointment else "Schedule Appointment"
            save_btn = tk.Button(
                inner_button_frame,
                text=button_text,
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
            save_btn.pack(side=tk.LEFT, padx=10)
        
        # Close button - always show
        close_btn = tk.Button(
            inner_button_frame if not view_only else main_frame,
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
        if view_only:
            close_btn.pack(pady=20)
        else:
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
    
