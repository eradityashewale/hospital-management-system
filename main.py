"""
Hospital Management System - Main Application
Offline Desktop Application for Hospital Management
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from logger import log_button_click, log_navigation, log_error, log_info, log_debug, log_warning
import sys

# Import modules
from modules.patient_module import PatientModule
from modules.doctor_module import DoctorModule
from modules.appointment_module import AppointmentModule
from modules.prescription_module import PrescriptionModule
from modules.billing_module import BillingModule
from modules.reports_module import ReportsModule


class HospitalManagementSystem:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Management System")
        self.root.geometry("1400x800")
        # Modern gradient-like background
        self.root.configure(bg='#f5f7fa')
        
        log_info("=" * 60)
        log_info("Hospital Management System Starting")
        log_info("=" * 60)
        
        # Create UI first to make buttons immediately responsive
        log_info("Creating main layout...")
        self.create_main_layout()
        
        # Set up focus and event processing handlers
        self._setup_focus_handlers()
        
        # Ensure all navigation buttons are enabled immediately
        for button_name, btn in self.nav_buttons.items():
            btn.config(state=tk.NORMAL)
        
        # Show window and process events immediately so buttons work RIGHT AWAY
        self.root.update_idletasks()
        self.root.update()
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        
        # Process events multiple times to ensure UI is fully rendered and interactive
        self.root.update_idletasks()
        self.root.update()
        self.root.update_idletasks()
        self.root.update()
        
        # Initialize database - must be done before modules can load
        # SQLite is fast, but we show window first so UI appears immediately
        log_info("Initializing database...")
        self.db = Database()
        log_info("Database initialized successfully")
        
        # Schedule dashboard loading after UI is fully ready
        # This ensures buttons are responsive immediately
        log_info("Scheduling dashboard load...")
        self.root.after(10, self._load_dashboard_after_startup)
        
        # Start periodic event processing to ensure buttons always work
        self._start_periodic_event_processing()
        
        # Final event processing to ensure everything is interactive
        self.root.update_idletasks()
        self.root.update()
        
        log_info("Application startup complete - buttons ready immediately")
    
    def _load_dashboard_after_startup(self):
        """Load dashboard after UI is fully initialized"""
        try:
            log_info("Loading dashboard...")
            self.show_dashboard()
            # Ensure buttons remain enabled after dashboard loads
            for button_name, btn in self.nav_buttons.items():
                btn.config(state=tk.NORMAL)
            self.root.update_idletasks()
            log_info("Dashboard loaded successfully")
        except Exception as e:
            log_error("Failed to load dashboard during startup", e)
    
    def _setup_focus_handlers(self):
        """Set up focus event handlers to ensure buttons work when window is active"""
        def on_focus_in(event):
            """Handle window gaining focus - process pending events and ensure buttons work"""
            log_debug("Window gained focus - processing events")
            # Process all pending events
            self.root.update_idletasks()
            # Ensure all buttons are enabled
            for button_name, btn in self.nav_buttons.items():
                if btn['state'] != tk.NORMAL:
                    btn.config(state=tk.NORMAL)
            # Process events again
            self.root.update_idletasks()
            return True
        
        def on_focus_out(event):
            """Handle window losing focus"""
            log_debug("Window lost focus")
            return True
        
        def on_map(event):
            """Handle window being mapped - ensure buttons are ready immediately"""
            log_debug("Window mapped - ensuring buttons are ready")
            # Ensure all buttons are enabled when window becomes visible
            for button_name, btn in self.nav_buttons.items():
                if btn['state'] != tk.NORMAL:
                    btn.config(state=tk.NORMAL)
            # Process events to ensure buttons are interactive
            self.root.update_idletasks()
            return True
        
        # Bind focus events
        self.root.bind('<FocusIn>', on_focus_in)
        self.root.bind('<FocusOut>', on_focus_out)
        # Bind map event to ensure buttons work as soon as window is visible
        self.root.bind('<Map>', on_map)
    
    def _start_periodic_event_processing(self):
        """Start periodic event processing to ensure buttons always work"""
        def process_events_periodically():
            """Periodically process events to ensure buttons remain responsive"""
            try:
                # Process pending idle tasks
                self.root.update_idletasks()
                
                # Ensure all buttons are enabled
                for button_name, btn in self.nav_buttons.items():
                    if btn['state'] != tk.NORMAL:
                        btn.config(state=tk.NORMAL)
                
                # Schedule next processing (every 500ms - frequent enough but not too heavy)
                self.root.after(500, process_events_periodically)
            except Exception as e:
                # If there's an error, still schedule next processing
                log_debug(f"Error in periodic event processing: {e}")
                self.root.after(500, process_events_periodically)
        
        # Start periodic processing after a short delay
        self.root.after(100, process_events_periodically)
        log_info("Periodic event processing started")
    
    def create_main_layout(self):
        """Create main application layout"""
        # Modern top menu bar with gradient effect
        menu_frame = tk.Frame(self.root, bg='#1a237e', height=70)
        menu_frame.pack(fill=tk.X, padx=0, pady=0)
        menu_frame.pack_propagate(False)
        
        # Title with modern font
        title_label = tk.Label(
            menu_frame,
            text="🏥 Hospital Management System",
            font=('Segoe UI', 20, 'bold'),
            bg='#1a237e',
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=25, pady=20)
        
        # Navigation buttons
        nav_frame = tk.Frame(menu_frame, bg='#1a237e')
        nav_frame.pack(side=tk.RIGHT, padx=20)
        
        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Patients", self.show_patients),
            ("Doctors", self.show_doctors),
            ("Appointments", self.show_appointments),
            ("Prescriptions", self.show_prescriptions),
            ("Billing", self.show_billing),
            ("Reports", self.show_reports)
        ]
        
        # Store button references
        self.nav_buttons = {}
        
        # Create buttons with direct method binding and logging
        self.current_module = "Dashboard"
        # Store button commands mapping
        self.button_commands = {}
        for text, command in buttons:
            self.button_commands[text] = command
            
            # Create a closure that properly captures the button name
            def make_handler(btn_name):
                def handler():
                    self._handle_navigation(btn_name)
                return handler
            
            # Modern button styling with hover effects
            btn = tk.Button(
                nav_frame,
                text=text,
                command=make_handler(text),
                font=('Segoe UI', 11, 'bold'),
                bg='#3949ab',
                fg='white',
                activebackground='#5c6bc0',
                activeforeground='white',
                relief=tk.FLAT,
                bd=0,
                padx=20,
                pady=12,
                cursor='hand2',
                highlightthickness=0,
                state=tk.NORMAL,
                takefocus=0
            )
            btn.pack(side=tk.LEFT, padx=4)
            self.nav_buttons[text] = btn
            # Ensure button is immediately enabled and ready
            btn.config(state=tk.NORMAL)
            # Force button widget to process its configuration immediately
            try:
                btn.update_idletasks()
            except:
                pass  # Ignore errors during initialization
            log_debug(f"Navigation button '{text}' created and bound to {command.__name__}")
        
        log_info("Main layout created successfully")
        
        # Main content area with modern background
        self.content_frame = tk.Frame(self.root, bg='#f5f7fa')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    def _handle_navigation(self, button_name):
        """Handle navigation button clicks"""
        # Process events immediately when button is clicked - ensures responsiveness
        self.root.update_idletasks()
        
        log_button_click(button_name, "Navigation")
        log_info(f"Button '{button_name}' clicked - executing command")
        log_navigation(self.current_module, button_name)
        
        # Check if button exists
        if button_name not in self.button_commands:
            log_error(f"Button '{button_name}' not found in button_commands", None)
            messagebox.showerror("Error", f"Button '{button_name}' command not found")
            return
        
        command = self.button_commands[button_name]
        if command is None:
            log_error(f"Command for '{button_name}' is None", None)
            messagebox.showerror("Error", f"Command for '{button_name}' is None")
            return
        
        # Check if button is disabled and re-enable it
        if button_name in self.nav_buttons:
            btn = self.nav_buttons[button_name]
            if btn['state'] != tk.NORMAL:
                log_warning(f"Button '{button_name}' is disabled, state: {btn['state']}")
                # Re-enable the button
                btn.config(state=tk.NORMAL)
                self.root.update_idletasks()
                self.root.update()
            
        try:
            log_info(f"Loading {button_name} module...")
            # Ensure UI is ready before executing command
            self.root.update_idletasks()
            self.root.update()
            command()
            self.current_module = button_name
            # Force UI update after module loads
            self.root.update_idletasks()
            self.root.update()
            
            # Ensure all navigation buttons remain enabled and responsive
            for btn_name, btn in self.nav_buttons.items():
                if btn['state'] != tk.NORMAL:
                    btn.config(state=tk.NORMAL)
            
            # Final update to ensure buttons are ready
            self.root.update_idletasks()
            self.root.update()
            log_info(f"{button_name} module loaded successfully")
        except Exception as e:
            log_error(f"Error executing {button_name}", e)
            messagebox.showerror("Error", f"Error executing {button_name}: {str(e)}")
            # Ensure buttons remain enabled after error
            if button_name in self.nav_buttons:
                self.nav_buttons[button_name].config(state=tk.NORMAL)
            # Process events after error
            self.root.update_idletasks()
            self.root.update()
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        # Force immediate UI update after clearing
        self.root.update_idletasks()
        self.root.update()
    
    def show_dashboard(self):
        """Show dashboard with statistics"""
        try:
            log_info("show_dashboard() called")
            self.clear_content()
            log_info("Dashboard content cleared")
            # Ensure UI is ready
            self.root.update_idletasks()
            
            # Dashboard title with modern styling
            title = tk.Label(
                self.content_frame,
                text="Dashboard",
                font=('Segoe UI', 28, 'bold'),
                bg='#f5f7fa',
                fg='#1a237e'
            )
            title.pack(pady=(30, 10))
            
            # Filter frame
            filter_frame = tk.Frame(self.content_frame, bg='#f5f7fa')
            filter_frame.pack(fill=tk.X, padx=25, pady=(10, 20))
            
            # Filter label
            filter_label = tk.Label(
                filter_frame,
                text="Filter by:",
                font=('Segoe UI', 11, 'bold'),
                bg='#f5f7fa',
                fg='#374151'
            )
            filter_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Store current filter state
            self.current_filter = {'type': 'all', 'date': None}
            self.stat_value_labels = []  # Store references to value labels for updating
            
            # Filter buttons
            filter_buttons_frame = tk.Frame(filter_frame, bg='#f5f7fa')
            filter_buttons_frame.pack(side=tk.LEFT, padx=5)
            
            # Date input frame (initially hidden)
            date_input_frame = tk.Frame(filter_frame, bg='#f5f7fa')
            date_input_frame.pack(side=tk.LEFT, padx=10)
            
            date_label = tk.Label(
                date_input_frame,
                text="Date:",
                font=('Segoe UI', 10),
                bg='#f5f7fa',
                fg='#6b7280'
            )
            date_label.pack(side=tk.LEFT, padx=(0, 5))
            
            from utils import get_current_date
            self.filter_date_var = tk.StringVar(value=get_current_date())
            date_entry = tk.Entry(
                date_input_frame,
                textvariable=self.filter_date_var,
                font=('Segoe UI', 10),
                width=12,
                relief=tk.SOLID,
                bd=1
            )
            date_entry.pack(side=tk.LEFT, padx=5)
            
            # Calendar button for date
            def open_calendar_for_date(entry_widget, var):
                """Open calendar for date entry"""
                calendar_window = tk.Toplevel(self.root)
                calendar_window.title("Select Date")
                calendar_window.geometry("300x280")
                calendar_window.configure(bg='#ffffff')
                calendar_window.transient(self.root)
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
                current_date_str = var.get()
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
                            current_selected = datetime.strptime(var.get(), '%Y-%m-%d')
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
                    var.set(date_str)
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, date_str)
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
            
            # Calendar button for date
            date_cal_btn = tk.Button(
                date_input_frame,
                text="📅",
                command=lambda: open_calendar_for_date(date_entry, self.filter_date_var),
                font=('Segoe UI', 12),
                bg='#3b82f6',
                fg='white',
                width=3,
                relief=tk.FLAT,
                cursor='hand2',
                activebackground='#2563eb'
            )
            date_cal_btn.pack(side=tk.LEFT, padx=2)
            
            # Month input frame (initially hidden)
            month_input_frame = tk.Frame(filter_frame, bg='#f5f7fa')
            month_input_frame.pack(side=tk.LEFT, padx=10)
            
            month_label = tk.Label(
                month_input_frame,
                text="Month (YYYY-MM):",
                font=('Segoe UI', 10),
                bg='#f5f7fa',
                fg='#6b7280'
            )
            month_label.pack(side=tk.LEFT, padx=(0, 5))
            
            from datetime import datetime
            current_month = datetime.now().strftime('%Y-%m')
            self.filter_month_var = tk.StringVar(value=current_month)
            month_entry = tk.Entry(
                month_input_frame,
                textvariable=self.filter_month_var,
                font=('Segoe UI', 10),
                width=12,
                relief=tk.SOLID,
                bd=1
            )
            month_entry.pack(side=tk.LEFT, padx=5)
            
            # Year input frame (initially hidden)
            year_input_frame = tk.Frame(filter_frame, bg='#f5f7fa')
            year_input_frame.pack(side=tk.LEFT, padx=10)
            
            year_label = tk.Label(
                year_input_frame,
                text="Year (YYYY):",
                font=('Segoe UI', 10),
                bg='#f5f7fa',
                fg='#6b7280'
            )
            year_label.pack(side=tk.LEFT, padx=(0, 5))
            
            current_year = datetime.now().strftime('%Y')
            self.filter_year_var = tk.StringVar(value=current_year)
            year_entry = tk.Entry(
                year_input_frame,
                textvariable=self.filter_year_var,
                font=('Segoe UI', 10),
                width=12,
                relief=tk.SOLID,
                bd=1
            )
            year_entry.pack(side=tk.LEFT, padx=5)
            
            # Date range input frame (initially hidden)
            date_range_frame = tk.Frame(filter_frame, bg='#f5f7fa')
            date_range_frame.pack(side=tk.LEFT, padx=10)
            
            from_label = tk.Label(
                date_range_frame,
                text="From:",
                font=('Segoe UI', 10),
                bg='#f5f7fa',
                fg='#6b7280'
            )
            from_label.pack(side=tk.LEFT, padx=(0, 5))
            
            self.filter_from_date_var = tk.StringVar(value=get_current_date())
            from_date_entry = tk.Entry(
                date_range_frame,
                textvariable=self.filter_from_date_var,
                font=('Segoe UI', 10),
                width=12,
                relief=tk.SOLID,
                bd=1
            )
            from_date_entry.pack(side=tk.LEFT, padx=2)
            
            from_cal_btn = tk.Button(
                date_range_frame,
                text="📅",
                command=lambda: open_calendar_for_date(from_date_entry, self.filter_from_date_var),
                font=('Segoe UI', 12),
                bg='#3b82f6',
                fg='white',
                width=3,
                relief=tk.FLAT,
                cursor='hand2',
                activebackground='#2563eb'
            )
            from_cal_btn.pack(side=tk.LEFT, padx=2)
            
            to_label = tk.Label(
                date_range_frame,
                text="To:",
                font=('Segoe UI', 10),
                bg='#f5f7fa',
                fg='#6b7280'
            )
            to_label.pack(side=tk.LEFT, padx=(5, 5))
            
            self.filter_to_date_var = tk.StringVar(value=get_current_date())
            to_date_entry = tk.Entry(
                date_range_frame,
                textvariable=self.filter_to_date_var,
                font=('Segoe UI', 10),
                width=12,
                relief=tk.SOLID,
                bd=1
            )
            to_date_entry.pack(side=tk.LEFT, padx=2)
            
            to_cal_btn = tk.Button(
                date_range_frame,
                text="📅",
                command=lambda: open_calendar_for_date(to_date_entry, self.filter_to_date_var),
                font=('Segoe UI', 12),
                bg='#3b82f6',
                fg='white',
                width=3,
                relief=tk.FLAT,
                cursor='hand2',
                activebackground='#2563eb'
            )
            to_cal_btn.pack(side=tk.LEFT, padx=2)
            
            # Initially hide date inputs
            date_input_frame.pack_forget()
            date_range_frame.pack_forget()
            month_input_frame.pack_forget()
            year_input_frame.pack_forget()
            
            # Create filter buttons list (will be populated)
            filter_btns = []
            
            def refresh_statistics():
                """Refresh statistics based on current filter"""
                try:
                    filter_type = self.current_filter['type']
                    filter_date = None
                    
                    if filter_type == 'daily':
                        filter_date = self.filter_date_var.get()
                        stats = self.db.get_daily_statistics(filter_date)
                    elif filter_type == 'monthly':
                        filter_date = self.filter_month_var.get()
                        stats = self.db.get_monthly_statistics(filter_date)
                    elif filter_type == 'yearly':
                        filter_date = self.filter_year_var.get()
                        stats = self.db.get_yearly_statistics(filter_date)
                    elif filter_type == 'datewise':
                        filter_date = self.filter_date_var.get()
                        stats = self.db.get_datewise_statistics(filter_date)
                    elif filter_type == 'daterange':
                        from_date = self.filter_from_date_var.get()
                        to_date = self.filter_to_date_var.get()
                        if not from_date or not to_date:
                            messagebox.showwarning("Warning", "Please select both 'From' and 'To' dates")
                            return
                        if from_date > to_date:
                            messagebox.showwarning("Warning", "'From' date cannot be after 'To' date")
                            return
                        stats = self.db.get_date_range_statistics(from_date, to_date)
                    else:  # 'all'
                        stats = self.db.get_statistics()
                    
                    # Update value labels
                    values = [
                        stats['total_patients'],
                        stats['total_doctors'],
                        stats['scheduled_appointments'],
                        stats['completed_appointments'],
                        f"${stats['total_revenue']:.2f}"
                    ]
                    
                    for i, label in enumerate(self.stat_value_labels):
                        label.config(text=str(values[i]))
                    
                except Exception as e:
                    log_error("Failed to refresh statistics", e)
                    messagebox.showerror("Error", f"Failed to refresh statistics: {str(e)}")
            
            # Create filter buttons
            all_btn = tk.Button(
                filter_buttons_frame,
                text="All",
                command=lambda: apply_filter('all'),
                font=('Segoe UI', 10, 'bold'),
                bg='#10b981',
                fg='white',
                padx=20,
                pady=8,
                cursor='hand2',
                relief=tk.FLAT,
                activebackground='#059669'
            )
            all_btn.pack(side=tk.LEFT, padx=3)
            filter_btns.append(all_btn)
            
            daily_btn = tk.Button(
                filter_buttons_frame,
                text="Daily",
                command=lambda: apply_filter('daily'),
                font=('Segoe UI', 10, 'bold'),
                bg='#6b7280',
                fg='white',
                padx=20,
                pady=8,
                cursor='hand2',
                relief=tk.FLAT,
                activebackground='#4b5563'
            )
            daily_btn.pack(side=tk.LEFT, padx=3)
            filter_btns.append(daily_btn)
            
            monthly_btn = tk.Button(
                filter_buttons_frame,
                text="Monthly",
                command=lambda: apply_filter('monthly'),
                font=('Segoe UI', 10, 'bold'),
                bg='#6b7280',
                fg='white',
                padx=20,
                pady=8,
                cursor='hand2',
                relief=tk.FLAT,
                activebackground='#4b5563'
            )
            monthly_btn.pack(side=tk.LEFT, padx=3)
            filter_btns.append(monthly_btn)
            
            yearly_btn = tk.Button(
                filter_buttons_frame,
                text="Yearly",
                command=lambda: apply_filter('yearly'),
                font=('Segoe UI', 10, 'bold'),
                bg='#6b7280',
                fg='white',
                padx=20,
                pady=8,
                cursor='hand2',
                relief=tk.FLAT,
                activebackground='#4b5563'
            )
            yearly_btn.pack(side=tk.LEFT, padx=3)
            filter_btns.append(yearly_btn)
            
            datewise_btn = tk.Button(
                filter_buttons_frame,
                text="Datewise",
                command=lambda: apply_filter('datewise'),
                font=('Segoe UI', 10, 'bold'),
                bg='#6b7280',
                fg='white',
                padx=20,
                pady=8,
                cursor='hand2',
                relief=tk.FLAT,
                activebackground='#4b5563'
            )
            datewise_btn.pack(side=tk.LEFT, padx=3)
            filter_btns.append(datewise_btn)
            
            date_range_btn = tk.Button(
                filter_buttons_frame,
                text="Date Range",
                command=lambda: apply_filter('daterange'),
                font=('Segoe UI', 10, 'bold'),
                bg='#6b7280',
                fg='white',
                padx=20,
                pady=8,
                cursor='hand2',
                relief=tk.FLAT,
                activebackground='#4b5563'
            )
            date_range_btn.pack(side=tk.LEFT, padx=3)
            filter_btns.append(date_range_btn)
            
            # Store button map for apply_filter function
            button_map = {
                'all': all_btn,
                'daily': daily_btn,
                'monthly': monthly_btn,
                'yearly': yearly_btn,
                'datewise': datewise_btn,
                'daterange': date_range_btn
            }
            
            # Update apply_filter to use button_map
            def apply_filter_updated(filter_type):
                """Apply filter and update statistics with button highlighting"""
                self.current_filter['type'] = filter_type
                
                # Show/hide appropriate input fields
                if filter_type == 'daily' or filter_type == 'datewise':
                    date_input_frame.pack(side=tk.LEFT, padx=10, before=filter_buttons_frame)
                    date_range_frame.pack_forget()
                    month_input_frame.pack_forget()
                    year_input_frame.pack_forget()
                elif filter_type == 'daterange':
                    date_range_frame.pack(side=tk.LEFT, padx=10, before=filter_buttons_frame)
                    date_input_frame.pack_forget()
                    month_input_frame.pack_forget()
                    year_input_frame.pack_forget()
                elif filter_type == 'monthly':
                    month_input_frame.pack(side=tk.LEFT, padx=10, before=filter_buttons_frame)
                    date_input_frame.pack_forget()
                    date_range_frame.pack_forget()
                    year_input_frame.pack_forget()
                elif filter_type == 'yearly':
                    year_input_frame.pack(side=tk.LEFT, padx=10, before=filter_buttons_frame)
                    date_input_frame.pack_forget()
                    date_range_frame.pack_forget()
                    month_input_frame.pack_forget()
                else:  # 'all'
                    date_input_frame.pack_forget()
                    date_range_frame.pack_forget()
                    month_input_frame.pack_forget()
                    year_input_frame.pack_forget()
                
                # Update button styles - reset all buttons
                for btn in filter_btns:
                    btn_text = btn['text'].replace('✓ ', '')
                    btn.config(bg='#6b7280', fg='white', text=btn_text)
                
                # Highlight selected button
                if filter_type in button_map:
                    selected_btn = button_map[filter_type]
                    selected_btn.config(bg='#10b981', fg='white')
                    selected_btn['text'] = '✓ ' + selected_btn['text'].replace('✓ ', '')
                
                # Refresh statistics
                refresh_statistics()
            
            # Update button commands to use the updated function
            all_btn.config(command=lambda: apply_filter_updated('all'))
            daily_btn.config(command=lambda: apply_filter_updated('daily'))
            monthly_btn.config(command=lambda: apply_filter_updated('monthly'))
            yearly_btn.config(command=lambda: apply_filter_updated('yearly'))
            datewise_btn.config(command=lambda: apply_filter_updated('datewise'))
            date_range_btn.config(command=lambda: apply_filter_updated('daterange'))
            
            # Apply button for date inputs
            apply_btn = tk.Button(
                filter_frame,
                text="Apply Filter",
                command=refresh_statistics,
                font=('Segoe UI', 10, 'bold'),
                bg='#3b82f6',
                fg='white',
                padx=15,
                pady=8,
                cursor='hand2',
                relief=tk.FLAT,
                activebackground='#2563eb'
            )
            apply_btn.pack(side=tk.LEFT, padx=(15, 0))
            
            # Statistics frame
            stats_frame = tk.Frame(self.content_frame, bg='#f5f7fa')
            stats_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
            
            try:
                stats = self.db.get_statistics()
            except:
                stats = {
                    'total_patients': 0,
                    'total_doctors': 0,
                    'scheduled_appointments': 0,
                    'completed_appointments': 0,
                    'total_revenue': 0
                }
            
            # Statistics cards
            stat_cards = [
                ("Total Patients", stats['total_patients'], '#3498db'),
                ("Total Doctors", stats['total_doctors'], '#2ecc71'),
                ("Scheduled Appointments", stats['scheduled_appointments'], '#f39c12'),
                ("Completed Appointments", stats['completed_appointments'], '#9b59b6'),
                ("Total Revenue", f"${stats['total_revenue']:.2f}", '#e74c3c')
            ]
            
            cards_frame = tk.Frame(stats_frame, bg='#f5f7fa')
            cards_frame.pack(fill=tk.BOTH, expand=True)
            
            # Modern color palette
            modern_colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']
            
            for i, (label, value, color) in enumerate(stat_cards):
                # Use modern colors
                modern_color = modern_colors[i % len(modern_colors)]
                card = tk.Frame(
                    cards_frame,
                    bg=modern_color,
                    relief=tk.FLAT,
                    bd=0
                )
                card.grid(row=i//3, column=i%3, padx=12, pady=12, sticky='nsew')
                cards_frame.grid_columnconfigure(i%3, weight=1)
                
                value_label = tk.Label(
                    card,
                    text=str(value),
                    font=('Segoe UI', 36, 'bold'),
                    bg=modern_color,
                    fg='white'
                )
                value_label.pack(pady=(25, 10))
                self.stat_value_labels.append(value_label)  # Store reference
                
                label_label = tk.Label(
                    card,
                    text=label,
                    font=('Segoe UI', 13),
                    bg=modern_color,
                    fg='white'
                )
                label_label.pack(pady=(0, 20))
            
            # Welcome message with modern card design
            welcome_frame = tk.Frame(self.content_frame, bg='white', relief=tk.FLAT, bd=0)
            welcome_frame.pack(fill=tk.X, padx=25, pady=25)
            
            welcome_text = """
Welcome to Hospital Management System!

This is an offline desktop application for managing hospital operations.
You can manage patients, doctors, appointments, prescriptions, and billing all in one place.

Features:
• Patient Registration and Management
• Doctor Management
• Appointment Scheduling
• Prescription Management
• Billing and Invoicing
• Reports and Analytics

All data is stored locally on your computer - no internet connection required.
            """
            
            welcome_label = tk.Label(
                welcome_frame,
                text=welcome_text,
                font=('Segoe UI', 11),
                bg='white',
                fg='#374151',
                justify=tk.LEFT,
                anchor='w'
            )
            welcome_label.pack(padx=30, pady=30)
            log_info("Dashboard loaded successfully")
        except Exception as e:
            log_error("Failed to load Dashboard", e)
            messagebox.showerror("Error", f"Failed to load Dashboard: {str(e)}")
    
    def show_patients(self):
        """Show patient management module"""
        try:
            log_info("Loading Patients module...")
            self.clear_content()
            self.root.update_idletasks()
            PatientModule(self.content_frame, self.db)
            # Update UI after module creation
            self.root.update_idletasks()
            self.root.update()
            log_info("Patients module loaded successfully")
        except Exception as e:
            log_error("Failed to load Patients module", e)
            messagebox.showerror("Error", f"Failed to load Patients module: {str(e)}")
    
    def show_doctors(self):
        """Show doctor management module"""
        try:
            log_info("Loading Doctors module...")
            self.clear_content()
            self.root.update_idletasks()
            DoctorModule(self.content_frame, self.db)
            self.root.update_idletasks()
            self.root.update()
            log_info("Doctors module loaded successfully")
        except Exception as e:
            log_error("Failed to load Doctors module", e)
            messagebox.showerror("Error", f"Failed to load Doctors module: {str(e)}")
    
    def show_appointments(self):
        """Show appointment management module"""
        try:
            log_info("Loading Appointments module...")
            self.clear_content()
            self.root.update_idletasks()
            AppointmentModule(self.content_frame, self.db)
            self.root.update_idletasks()
            self.root.update()
            log_info("Appointments module loaded successfully")
        except Exception as e:
            log_error("Failed to load Appointments module", e)
            messagebox.showerror("Error", f"Failed to load Appointments module: {str(e)}")
    
    def show_prescriptions(self):
        """Show prescription management module"""
        try:
            log_info("Loading Prescriptions module...")
            self.clear_content()
            self.root.update_idletasks()
            PrescriptionModule(self.content_frame, self.db)
            self.root.update_idletasks()
            self.root.update()
            log_info("Prescriptions module loaded successfully")
        except Exception as e:
            log_error("Failed to load Prescriptions module", e)
            messagebox.showerror("Error", f"Failed to load Prescriptions module: {str(e)}")
    
    def show_billing(self):
        """Show billing module"""
        try:
            log_info("Loading Billing module...")
            self.clear_content()
            self.root.update_idletasks()
            BillingModule(self.content_frame, self.db)
            self.root.update_idletasks()
            self.root.update()
            log_info("Billing module loaded successfully")
        except Exception as e:
            log_error("Failed to load Billing module", e)
            messagebox.showerror("Error", f"Failed to load Billing module: {str(e)}")
    
    def show_reports(self):
        """Show reports module"""
        try:
            log_info("Loading Reports module...")
            self.clear_content()
            self.root.update_idletasks()
            ReportsModule(self.content_frame, self.db)
            self.root.update_idletasks()
            self.root.update()
            log_info("Reports module loaded successfully")
        except Exception as e:
            log_error("Failed to load Reports module", e)
            messagebox.showerror("Error", f"Failed to load Reports module: {str(e)}")
    
    def on_closing(self):
        """Handle application closing"""
        log_info("Application closing...")
        self.db.close()
        log_info("Database connection closed")
        log_info("=" * 60)
        log_info("Hospital Management System Shutdown Complete")
        log_info("=" * 60)
        self.root.destroy()


def main():
    """Main entry point"""
    try:
        root = tk.Tk()
        app = HospitalManagementSystem(root)
        # Store app instance in root for easy access from modules
        root.app_instance = app
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        # Start mainloop immediately - window is already shown in __init__
        root.mainloop()
    except KeyboardInterrupt:
        log_info("Application interrupted by user")
    except Exception as e:
        log_error("Fatal error in main", e)
        import traceback
        traceback.print_exc()
        try:
            messagebox.showerror("Fatal Error", f"Application crashed: {str(e)}")
        except:
            print(f"Fatal Error: {str(e)}")


if __name__ == "__main__":
    main()

