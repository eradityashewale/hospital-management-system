"""
Hospital Management System - Main Application
Offline Desktop Application for Hospital Management
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from logger import log_button_click, log_navigation, log_error, log_info, log_debug, log_warning
from datetime import datetime, timedelta
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
    
    def __init__(self, root, authenticated_user=None, logout_callback=None):
        self.root = root
        self.authenticated_user = authenticated_user
        self.logout_callback = logout_callback
        self.root.title("MediFlow - Hospital Management System")
        self.root.geometry("1400x800")
        # Modern gradient-like background
        self.root.configure(bg='#f5f7fa')
        
        log_info("=" * 60)
        log_info("Hospital Management System Starting")
        if authenticated_user:
            log_info(f"User: {authenticated_user.get('username', 'Unknown')}")
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
        
        # Logo and product name container
        logo_title_container = tk.Frame(menu_frame, bg='#1a237e')
        logo_title_container.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Top row - Logo and Product name
        logo_title_frame = tk.Frame(logo_title_container, bg='#1a237e')
        logo_title_frame.pack(side=tk.TOP, anchor='w')
        
        # Logo icon (medical cross)
        logo_icon_label = tk.Label(
            logo_title_frame,
            text="╔═╗\n║╬║\n╚═╝",
            font=('Courier', 8, 'bold'),
            bg='#1a237e',
            fg='#60a5fa',
            justify=tk.LEFT
        )
        logo_icon_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Product name
        title_label = tk.Label(
            logo_title_frame,
            text="MediFlow",
            font=('Segoe UI', 18, 'bold'),
            bg='#1a237e',
            fg='white'
        )
        title_label.pack(side=tk.LEFT)
        
        # Bottom row - Company name
        company_label = tk.Label(
            logo_title_container,
            text="by Nexvora Solutions",
            font=('Segoe UI', 8, 'italic'),
            bg='#1a237e',
            fg='#93c5fd'
        )
        company_label.pack(side=tk.TOP, anchor='w', padx=(30, 0))
        
        # Navigation buttons - place in the middle area with proper spacing
        nav_frame = tk.Frame(menu_frame, bg='#1a237e')
        nav_frame.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        
        # User info and logout button frame
        user_frame = tk.Frame(menu_frame, bg='#1a237e')
        user_frame.pack(side=tk.RIGHT, padx=10)
        
        # User info label (will be updated with actual user info)
        self.user_info_label = tk.Label(
            user_frame,
            text="",
            font=('Segoe UI', 9),
            bg='#1a237e',
            fg='#e0e0e0'
        )
        self.user_info_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Logout button
        logout_btn = tk.Button(
            user_frame,
            text="🚪 Logout",
            font=('Segoe UI', 9, 'bold'),
            bg='#d32f2f',
            fg='white',
            activebackground='#c62828',
            activeforeground='white',
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=8,
            cursor='hand2',
            command=self.logout
        )
        logout_btn.pack(side=tk.RIGHT)
        
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
            
            # Modern button styling with hover effects - reduced padding to fit all buttons
            btn = tk.Button(
                nav_frame,
                text=text,
                command=make_handler(text),
                font=('Segoe UI', 10, 'bold'),
                bg='#3949ab',
                fg='white',
                activebackground='#5c6bc0',
                activeforeground='white',
                relief=tk.FLAT,
                bd=0,
                padx=12,
                pady=10,
                cursor='hand2',
                highlightthickness=0,
                state=tk.NORMAL,
                takefocus=0
            )
            btn.pack(side=tk.LEFT, padx=2)
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
        
        # Update user info label if user is authenticated
        if hasattr(self, 'authenticated_user') and self.authenticated_user:
            username = self.authenticated_user.get('username', 'User')
            full_name = self.authenticated_user.get('full_name', '')
            if full_name:
                self.user_info_label.config(text=f"👤 {full_name} ({username})")
            else:
                self.user_info_label.config(text=f"👤 {username}")
        
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
            
            # Create scrollable frame for dashboard
            # Create a canvas and scrollbar for scrolling
            canvas = tk.Canvas(self.content_frame, bg='#f5f7fa', highlightthickness=0)
            scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#f5f7fa')
            
            # Configure scrollable frame
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            # Create window in canvas for scrollable frame
            canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            
            # Configure canvas scrolling
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Update scroll region when canvas is resized
            def on_canvas_configure(event):
                canvas_width = event.width
                canvas.itemconfig(canvas_window, width=canvas_width)
                # Update scroll region
                canvas.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            canvas.bind('<Configure>', on_canvas_configure)
            
            # Bind mousewheel to canvas
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            
            # Filter frame
            filter_frame = tk.Frame(scrollable_frame, bg='#f5f7fa')
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
            
            # Month/Year picker for monthly filter - Grid-based Calendar Style
            def open_month_picker(entry_widget, var):
                """Open month and year picker with grid-based calendar design"""
                picker_window = tk.Toplevel(self.root)
                picker_window.title("Select Month")
                picker_window.geometry("320x280")
                picker_window.configure(bg='#ffffff')
                picker_window.transient(self.root)
                picker_window.grab_set()
                
                # Center the window
                picker_window.update_idletasks()
                x = (picker_window.winfo_screenwidth() // 2) - (320 // 2)
                y = (picker_window.winfo_screenheight() // 2) - (280 // 2)
                picker_window.geometry(f"320x280+{x}+{y}")
                
                # Get current month from entry or use current month
                current_month_str = var.get()
                try:
                    current_date = datetime.strptime(current_month_str + '-01', '%Y-%m-%d')
                    initial_year = current_date.year
                    initial_month = current_date.month
                except:
                    current_date = datetime.now()
                    initial_year = current_date.year
                    initial_month = current_date.month
                
                # Use mutable containers for selected values (for closure access)
                selected_state = {'year': initial_year, 'month': initial_month}
                
                # Year variable
                year_var = tk.IntVar(value=initial_year)
                
                # Month abbreviations
                month_abbr = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                
                # Main container with border
                main_container = tk.Frame(picker_window, bg='#ffffff', relief=tk.SOLID, bd=1)
                main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                main_container.config(highlightbackground='#3b82f6', highlightthickness=1)
                
                # Year navigation frame
                year_nav_frame = tk.Frame(main_container, bg='#ffffff')
                year_nav_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
                
                # Previous year button
                prev_year_btn = tk.Button(
                    year_nav_frame,
                    text="«",
                    font=('Segoe UI', 12, 'bold'),
                    bg='#ffffff',
                    fg='#374151',
                    relief=tk.FLAT,
                    bd=0,
                    cursor='hand2',
                    activebackground='#f3f4f6',
                    activeforeground='#1f2937',
                    width=3
                )
                prev_year_btn.pack(side=tk.LEFT)
                
                # Year label
                year_label = tk.Label(
                    year_nav_frame,
                    text=str(initial_year),
                    font=('Segoe UI', 14, 'bold'),
                    bg='#ffffff',
                    fg='#1f2937'
                )
                year_label.pack(side=tk.LEFT, expand=True)
                
                # Next year button
                next_year_btn = tk.Button(
                    year_nav_frame,
                    text="»",
                    font=('Segoe UI', 12, 'bold'),
                    bg='#ffffff',
                    fg='#374151',
                    relief=tk.FLAT,
                    bd=0,
                    cursor='hand2',
                    activebackground='#f3f4f6',
                    activeforeground='#1f2937',
                    width=3
                )
                next_year_btn.pack(side=tk.LEFT)
                
                # Month grid frame
                month_grid_frame = tk.Frame(main_container, bg='#ffffff')
                month_grid_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
                
                # Store month buttons for updating
                month_buttons = []
                
                def update_year_display():
                    """Update year label and month button highlights"""
                    current_year = year_var.get()
                    year_label.config(text=str(current_year))
                    # Update month button highlights
                    for i, btn in enumerate(month_buttons):
                        month_num = i + 1
                        # Highlight if this is the selected month for the current year
                        if month_num == selected_state['month'] and current_year == selected_state['year']:
                            btn.config(bg='#3b82f6', fg='white', relief=tk.SOLID, bd=1)
                        else:
                            btn.config(bg='#ffffff', fg='#374151', relief=tk.FLAT, bd=0)
                
                def prev_year():
                    """Go to previous year"""
                    year_var.set(year_var.get() - 1)
                    update_year_display()
                
                def next_year():
                    """Go to next year"""
                    year_var.set(year_var.get() + 1)
                    update_year_display()
                
                def select_month(month_index):
                    """Select a month"""
                    year = year_var.get()
                    month_str = f"{year}-{month_index:02d}"
                    var.set(month_str)
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, month_str)
                    picker_window.destroy()
                
                # Bind year navigation
                prev_year_btn.config(command=prev_year)
                next_year_btn.config(command=next_year)
                
                # Create month buttons in 4x3 grid
                for i, month_name in enumerate(month_abbr):
                    row = i // 4
                    col = i % 4
                    month_num = i + 1
                    
                    # Determine if this month should be highlighted
                    is_selected = (month_num == initial_month and year_var.get() == initial_year)
                    
                    month_btn = tk.Button(
                        month_grid_frame,
                        text=month_name,
                        font=('Segoe UI', 10),
                        bg='#3b82f6' if is_selected else '#ffffff',
                        fg='white' if is_selected else '#374151',
                        relief=tk.SOLID if is_selected else tk.FLAT,
                        bd=1 if is_selected else 0,
                        cursor='hand2',
                        activebackground='#2563eb' if not is_selected else '#3b82f6',
                        activeforeground='white',
                        padx=15,
                        pady=10,
                        command=lambda m=month_num: select_month(m)
                    )
                    month_btn.grid(row=row, column=col, padx=3, pady=3, sticky='nsew')
                    month_buttons.append(month_btn)
                
                # Configure grid weights for even spacing
                for i in range(4):
                    month_grid_frame.grid_columnconfigure(i, weight=1)
                for i in range(3):
                    month_grid_frame.grid_rowconfigure(i, weight=1)
            
            # Year picker for yearly filter - Grid-based Calendar Style
            def open_year_picker(entry_widget, var):
                """Open year picker with grid-based calendar design"""
                picker_window = tk.Toplevel(self.root)
                picker_window.title("Select Year")
                picker_window.geometry("320x280")
                picker_window.configure(bg='#ffffff')
                picker_window.transient(self.root)
                picker_window.grab_set()
                
                # Center the window
                picker_window.update_idletasks()
                x = (picker_window.winfo_screenwidth() // 2) - (320 // 2)
                y = (picker_window.winfo_screenheight() // 2) - (280 // 2)
                picker_window.geometry(f"320x280+{x}+{y}")
                
                # Get current year from entry or use current year
                current_year_str = var.get()
                try:
                    initial_year = int(current_year_str)
                except:
                    initial_year = datetime.now().year
                
                # Calculate decade range (e.g., 2010-2019)
                # Find the start of the decade containing the selected year
                decade_start = (initial_year // 10) * 10
                # Display years from decade_start-1 to decade_start+10 (12 years total)
                # This gives us a range like 2009-2020 for decade 2010-2019
                
                # Use mutable containers (for closure access)
                decade_state = {'start': decade_start}
                selected_state = {'year': initial_year}
                
                # Main container with border
                main_container = tk.Frame(picker_window, bg='#ffffff', relief=tk.SOLID, bd=1)
                main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                main_container.config(highlightbackground='#3b82f6', highlightthickness=1)
                
                # Decade navigation frame
                decade_nav_frame = tk.Frame(main_container, bg='#ffffff')
                decade_nav_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
                
                # Previous decade button
                prev_decade_btn = tk.Button(
                    decade_nav_frame,
                    text="<",
                    font=('Segoe UI', 12, 'bold'),
                    bg='#ffffff',
                    fg='#374151',
                    relief=tk.FLAT,
                    bd=0,
                    cursor='hand2',
                    activebackground='#f3f4f6',
                    activeforeground='#1f2937',
                    width=3
                )
                prev_decade_btn.pack(side=tk.LEFT)
                
                # Decade range label (e.g., "2010-2019")
                def get_decade_range():
                    """Get the decade range string"""
                    start = decade_state['start']
                    return f"{start}-{start+9}"
                
                decade_label = tk.Label(
                    decade_nav_frame,
                    text=get_decade_range(),
                    font=('Segoe UI', 12, 'bold'),
                    bg='#ffffff',
                    fg='#1f2937'
                )
                decade_label.pack(side=tk.LEFT, expand=True)
                
                # Next decade button
                next_decade_btn = tk.Button(
                    decade_nav_frame,
                    text=">",
                    font=('Segoe UI', 12, 'bold'),
                    bg='#ffffff',
                    fg='#374151',
                    relief=tk.FLAT,
                    bd=0,
                    cursor='hand2',
                    activebackground='#f3f4f6',
                    activeforeground='#1f2937',
                    width=3
                )
                next_decade_btn.pack(side=tk.LEFT)
                
                # Year grid frame
                year_grid_frame = tk.Frame(main_container, bg='#ffffff')
                year_grid_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
                
                # Store year buttons for updating
                year_buttons = []
                
                def get_years_for_decade():
                    """Get list of years to display (12 years: decade_start-1 to decade_start+10)"""
                    start = decade_state['start']
                    return list(range(start - 1, start + 11))
                
                def update_decade_display():
                    """Update decade label and recreate year buttons"""
                    decade_label.config(text=get_decade_range())
                    # Clear existing buttons
                    for btn in year_buttons:
                        btn.destroy()
                    year_buttons.clear()
                    
                    # Recreate year buttons with new decade
                    years = get_years_for_decade()
                    for i, year_value in enumerate(years):
                        row = i // 4
                        col = i % 4
                        
                        # Determine if this year should be highlighted
                        is_selected = (year_value == selected_state['year'])
                        
                        year_btn = tk.Button(
                            year_grid_frame,
                            text=str(year_value),
                            font=('Segoe UI', 10),
                            bg='#3b82f6' if is_selected else '#ffffff',
                            fg='white' if is_selected else '#374151',
                            relief=tk.SOLID if is_selected else tk.FLAT,
                            bd=1 if is_selected else 0,
                            cursor='hand2',
                            activebackground='#2563eb' if not is_selected else '#3b82f6',
                            activeforeground='white',
                            padx=15,
                            pady=10,
                            command=lambda y=year_value: select_year(y)
                        )
                        year_btn.grid(row=row, column=col, padx=3, pady=3, sticky='nsew')
                        year_buttons.append(year_btn)
                
                def prev_decade():
                    """Go to previous decade"""
                    decade_state['start'] -= 10
                    update_decade_display()
                
                def next_decade():
                    """Go to next decade"""
                    decade_state['start'] += 10
                    update_decade_display()
                
                def select_year(year_value):
                    """Select a year"""
                    year_str = str(year_value)
                    var.set(year_str)
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, year_str)
                    picker_window.destroy()
                
                # Bind decade navigation
                prev_decade_btn.config(command=prev_decade)
                next_decade_btn.config(command=next_decade)
                
                # Create year buttons in 4x3 grid
                years = get_years_for_decade()
                for i, year_value in enumerate(years):
                    row = i // 4
                    col = i % 4
                    
                    # Determine if this year should be highlighted
                    is_selected = (year_value == initial_year)
                    
                    year_btn = tk.Button(
                        year_grid_frame,
                        text=str(year_value),
                        font=('Segoe UI', 10),
                        bg='#3b82f6' if is_selected else '#ffffff',
                        fg='white' if is_selected else '#374151',
                        relief=tk.SOLID if is_selected else tk.FLAT,
                        bd=1 if is_selected else 0,
                        cursor='hand2',
                        activebackground='#2563eb' if not is_selected else '#3b82f6',
                        activeforeground='white',
                        padx=15,
                        pady=10,
                        command=lambda y=year_value: select_year(y)
                    )
                    year_btn.grid(row=row, column=col, padx=3, pady=3, sticky='nsew')
                    year_buttons.append(year_btn)
                
                # Configure grid weights for even spacing
                for i in range(4):
                    year_grid_frame.grid_columnconfigure(i, weight=1)
                for i in range(3):
                    year_grid_frame.grid_rowconfigure(i, weight=1)
            
            # Calendar button for month picker
            month_cal_btn = tk.Button(
                month_input_frame,
                text="📅",
                command=lambda: open_month_picker(month_entry, self.filter_month_var),
                font=('Segoe UI', 12),
                bg='#3b82f6',
                fg='white',
                width=3,
                relief=tk.FLAT,
                cursor='hand2',
                activebackground='#2563eb'
            )
            month_cal_btn.pack(side=tk.LEFT, padx=2)
            
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
            
            # Calendar button for year picker
            year_cal_btn = tk.Button(
                year_input_frame,
                text="📅",
                command=lambda: open_year_picker(year_entry, self.filter_year_var),
                font=('Segoe UI', 12),
                bg='#3b82f6',
                fg='white',
                width=3,
                relief=tk.FLAT,
                cursor='hand2',
                activebackground='#2563eb'
            )
            year_cal_btn.pack(side=tk.LEFT, padx=2)
            
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
            
            # Define apply_filter function before creating buttons
            def apply_filter(filter_type):
                """Apply filter - basic version (will be enhanced after buttons are created)"""
                self.current_filter['type'] = filter_type
                
                # Show/hide appropriate input fields
                if filter_type == 'daily':
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
                
                # Button highlighting will be added after button_map is created
            
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
                    
                    # Update value labels (5 cards now)
                    values = [
                        stats['total_patients'],
                        stats['total_doctors'],
                        stats['scheduled_appointments'],
                        stats['completed_appointments'],
                        f"${stats['total_revenue']:.2f}"
                    ]
                    
                    for i, label in enumerate(self.stat_value_labels):
                        if i < len(values):
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
                'daterange': date_range_btn
            }
            
            # Update apply_filter to use button_map
            def apply_filter_updated(filter_type):
                """Apply filter and update statistics with button highlighting"""
                self.current_filter['type'] = filter_type
                
                # Show/hide appropriate input fields
                if filter_type == 'daily':
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
            stats_frame = tk.Frame(scrollable_frame, bg='#f5f7fa')
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
            
            # Modern KPI Cards with icons
            stat_cards = [
                ("👥", "Total Patients", stats['total_patients'], "+12%", '#3b82f6'),
                ("👨‍⚕️", "Active Doctors", stats['total_doctors'], "", '#8b5cf6'),
                ("📅", "Today's Appointments", stats['scheduled_appointments'], "", '#ec4899'),
                ("✅", "Completed Appointments", stats['completed_appointments'], "", '#f59e0b'),
                ("💰", "Total Revenue", f"${stats['total_revenue']:.2f}", "", '#10b981')
            ]
            
            cards_frame = tk.Frame(stats_frame, bg='#f5f7fa')
            cards_frame.pack(fill=tk.X, pady=(0, 20))
            
            for i, (icon, label, value, trend, color) in enumerate(stat_cards):
                card = tk.Frame(
                    cards_frame,
                    bg=color,
                    relief=tk.FLAT,
                    bd=0
                )
                # Arrange all 5 cards in a single row
                card.grid(row=0, column=i, padx=12, pady=12, sticky='nsew')
                cards_frame.grid_columnconfigure(i, weight=1)
                
                # Icon and label frame
                top_frame = tk.Frame(card, bg=color)
                top_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
                
                icon_label = tk.Label(
                    top_frame,
                    text=icon,
                    font=('Segoe UI', 24),
                    bg=color,
                    fg='white'
                )
                icon_label.pack(side=tk.LEFT, padx=(0, 10))
                
                label_frame = tk.Frame(top_frame, bg=color)
                label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                label_text = tk.Label(
                    label_frame,
                    text=label,
                    font=('Segoe UI', 11),
                    bg=color,
                    fg='white',
                    anchor='w'
                )
                label_text.pack(anchor='w')
                
                if trend:
                    trend_label = tk.Label(
                        label_frame,
                        text=f"↑ {trend}",
                        font=('Segoe UI', 9),
                        bg=color,
                        fg='white',
                        anchor='w'
                    )
                    trend_label.pack(anchor='w')
                
                # Value
                value_label = tk.Label(
                    card,
                    text=str(value),
                    font=('Segoe UI', 28, 'bold'),
                    bg=color,
                    fg='white'
                )
                value_label.pack(pady=(0, 20))
                self.stat_value_labels.append(value_label)  # Store reference
            
            # Company Branding Section
            branding_frame = tk.Frame(stats_frame, bg='#ffffff', relief=tk.FLAT, bd=1, highlightbackground='#e5e7eb', highlightthickness=1)
            branding_frame.pack(fill=tk.X, pady=(0, 20))
            
            branding_inner = tk.Frame(branding_frame, bg='#ffffff')
            branding_inner.pack(fill=tk.X, padx=25, pady=20)
            
            # Left side - Logo and Product Info
            logo_info_frame = tk.Frame(branding_inner, bg='#ffffff')
            logo_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Logo representation
            logo_frame = tk.Frame(logo_info_frame, bg='#1e3a8a', relief=tk.FLAT)
            logo_frame.pack(side=tk.LEFT, padx=(0, 20))
            
            logo_icon = tk.Label(
                logo_frame,
                text="╔═══╗\n║ ╬ ║\n╚═══╝",
                font=('Courier', 12, 'bold'),
                bg='#1e3a8a',
                fg='#60a5fa',
                padx=15,
                pady=10
            )
            logo_icon.pack()
            
            # Product and Company Info
            product_info = tk.Frame(logo_info_frame, bg='#ffffff')
            product_info.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            product_name_label = tk.Label(
                product_info,
                text="MediFlow",
                font=('Segoe UI', 22, 'bold'),
                bg='#ffffff',
                fg='#1e3a8a'
            )
            product_name_label.pack(anchor='w', pady=(0, 5))
            
            tagline_label = tk.Label(
                product_info,
                text="Streamlining Healthcare Management",
                font=('Segoe UI', 12),
                bg='#ffffff',
                fg='#6b7280'
            )
            tagline_label.pack(anchor='w', pady=(0, 8))
            
            company_label = tk.Label(
                product_info,
                text="Powered by Nexvora Solutions",
                font=('Segoe UI', 10, 'italic'),
                bg='#ffffff',
                fg='#6366f1'
            )
            company_label.pack(anchor='w')
            
            # Right side - Marketing Features
            features_frame = tk.Frame(branding_inner, bg='#ffffff')
            features_frame.pack(side=tk.RIGHT, padx=(20, 0))
            
            features_title = tk.Label(
                features_frame,
                text="Key Features",
                font=('Segoe UI', 12, 'bold'),
                bg='#ffffff',
                fg='#1e3a8a'
            )
            features_title.pack(anchor='e', pady=(0, 8))
            
            features_list = [
                "✓ Comprehensive Patient Management",
                "✓ Efficient Appointment Scheduling",
                "✓ Digital Prescription System",
                "✓ Automated Billing & Reports"
            ]
            
            for feature in features_list:
                feature_label = tk.Label(
                    features_frame,
                    text=feature,
                    font=('Segoe UI', 9),
                    bg='#ffffff',
                    fg='#374151',
                    anchor='e'
                )
                feature_label.pack(anchor='e', pady=2)
            
            # Main content area with three columns
            main_content = tk.Frame(scrollable_frame, bg='#f5f7fa')
            main_content.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 25))
            
            # Left column (charts)
            left_column = tk.Frame(main_content, bg='#f5f7fa', width=400)
            left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
            
            # Middle column (status chart and activities)
            middle_column = tk.Frame(main_content, bg='#f5f7fa', width=300)
            middle_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
            
            # Right column (quick actions and today's appointments)
            right_column = tk.Frame(main_content, bg='#f5f7fa', width=300)
            right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
            
            # Appointments Overview Chart (Left Column)
            appointments_chart_frame = tk.Frame(left_column, bg='white', relief=tk.FLAT, bd=1)
            appointments_chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            
            chart_header = tk.Frame(appointments_chart_frame, bg='white')
            chart_header.pack(fill=tk.X, padx=20, pady=(15, 10))
            
            tk.Label(
                chart_header,
                text="Appointments Overview",
                font=('Segoe UI', 14, 'bold'),
                bg='white',
                fg='#1f2937'
            ).pack(side=tk.LEFT)
            
            # Toggle buttons
            toggle_frame = tk.Frame(chart_header, bg='white')
            toggle_frame.pack(side=tk.RIGHT)
            
            daily_toggle = tk.Button(
                toggle_frame,
                text="Daily",
                font=('Segoe UI', 9, 'bold'),
                bg='#3b82f6',
                fg='white',
                padx=12,
                pady=4,
                relief=tk.FLAT,
                cursor='hand2'
            )
            daily_toggle.pack(side=tk.LEFT, padx=2)
            
            monthly_toggle = tk.Button(
                toggle_frame,
                text="Monthly",
                font=('Segoe UI', 9),
                bg='#e5e7eb',
                fg='#6b7280',
                padx=12,
                pady=4,
                relief=tk.FLAT,
                cursor='hand2'
            )
            monthly_toggle.pack(side=tk.LEFT, padx=2)
            
            # Chart canvas for appointments overview - larger for better visibility
            chart_canvas = tk.Canvas(appointments_chart_frame, bg='white', height=280, highlightthickness=0)
            chart_canvas.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 25))
            
            # Store chart mode
            self.appointments_chart_mode = 'daily'
            
            def draw_appointments_chart(mode='daily'):
                """Draw appointments chart based on mode"""
                chart_canvas.delete("all")
                
                # Get appointments data
                all_appointments = self.db.get_all_appointments()
                
                if not all_appointments:
                    canvas_width = chart_canvas.winfo_width() or 500
                    canvas_height = chart_canvas.winfo_height() or 280
                    chart_canvas.create_text(canvas_width/2, canvas_height/2, text="No appointment data available", 
                                           font=('Segoe UI', 11), fill='#9ca3af', justify=tk.CENTER)
                    return
                
                # Prepare data based on mode
                if mode == 'daily':
                    # Last 7 days
                    dates = []
                    for i in range(6, -1, -1):
                        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                        dates.append(date)
                    
                    scheduled_data = []
                    completed_data = []
                    cancelled_data = []
                    
                    for date in dates:
                        day_appts = [a for a in all_appointments if a.get('appointment_date') == date]
                        scheduled_data.append(sum(1 for a in day_appts if a.get('status') == 'Scheduled'))
                        completed_data.append(sum(1 for a in day_appts if a.get('status') == 'Completed'))
                        cancelled_data.append(sum(1 for a in day_appts if a.get('status') in ['Cancelled', 'No Show']))
                    
                    labels = [datetime.strptime(d, '%Y-%m-%d').strftime('%m/%d') for d in dates]
                else:  # monthly
                    # Last 6 months
                    months = []
                    for i in range(5, -1, -1):
                        month_date = datetime.now() - timedelta(days=30*i)
                        month_str = month_date.strftime('%Y-%m')
                        months.append(month_str)
                    
                    scheduled_data = []
                    completed_data = []
                    cancelled_data = []
                    
                    for month in months:
                        month_appts = [a for a in all_appointments if a.get('appointment_date', '')[:7] == month]
                        scheduled_data.append(sum(1 for a in month_appts if a.get('status') == 'Scheduled'))
                        completed_data.append(sum(1 for a in month_appts if a.get('status') == 'Completed'))
                        cancelled_data.append(sum(1 for a in month_appts if a.get('status') in ['Cancelled', 'No Show']))
                    
                    labels = [datetime.strptime(m + '-01', '%Y-%m-%d').strftime('%b') for m in months]
                
                # Calculate max value for scaling
                max_val = max(max(scheduled_data) if scheduled_data else 0,
                            max(completed_data) if completed_data else 0,
                            max(cancelled_data) if cancelled_data else 0, 1)
                
                # Get canvas dimensions
                chart_canvas.update_idletasks()
                chart_width = chart_canvas.winfo_width() or 500
                chart_height = chart_canvas.winfo_height() or 280
                
                # Chart dimensions with better margins
                margin_left = 60
                margin_bottom = 50
                margin_top = 20
                margin_right = 30
                
                plot_width = chart_width - margin_left - margin_right
                plot_height = chart_height - margin_top - margin_bottom
                
                # Draw axes
                chart_canvas.create_line(margin_left, margin_top, margin_left, chart_height - margin_bottom, fill='#d1d5db', width=2)
                chart_canvas.create_line(margin_left, chart_height - margin_bottom, chart_width - margin_right, chart_height - margin_bottom, fill='#d1d5db', width=2)
                
                # Draw grid lines and labels
                num_points = len(labels)
                if num_points > 0:
                    # Better spacing - more space between bar groups
                    group_spacing = plot_width / (num_points + 1)  # Space between groups
                    bar_group_width = group_spacing * 0.7  # Width of the 3-bar group
                    bar_width = bar_group_width / 3.5  # Individual bar width
                    bar_gap = bar_width * 0.15  # Small gap between bars
                    
                    for i, label in enumerate(labels):
                        # Center of bar group
                        x_center = margin_left + (i + 1) * group_spacing
                        
                        # X positions for each bar
                        x_scheduled = x_center - bar_group_width/2 + bar_width/2
                        x_completed = x_center
                        x_cancelled = x_center + bar_group_width/2 - bar_width/2
                        
                        # Draw label below bars
                        chart_canvas.create_text(x_center, chart_height - margin_bottom + 20, text=label, 
                                                font=('Segoe UI', 9, 'bold'), fill='#374151', anchor='n')
                        
                        # Draw bars for each status with better spacing
                        if scheduled_data[i] > 0:
                            bar_height = (scheduled_data[i] / max_val) * plot_height
                            chart_canvas.create_rectangle(
                                x_scheduled - bar_width/2, chart_height - margin_bottom,
                                x_scheduled + bar_width/2, chart_height - margin_bottom - bar_height,
                                fill='#3b82f6', outline='', width=0
                            )
                        
                        if completed_data[i] > 0:
                            bar_height = (completed_data[i] / max_val) * plot_height
                            chart_canvas.create_rectangle(
                                x_completed - bar_width/2, chart_height - margin_bottom,
                                x_completed + bar_width/2, chart_height - margin_bottom - bar_height,
                                fill='#10b981', outline='', width=0
                            )
                        
                        if cancelled_data[i] > 0:
                            bar_height = (cancelled_data[i] / max_val) * plot_height
                            chart_canvas.create_rectangle(
                                x_cancelled - bar_width/2, chart_height - margin_bottom,
                                x_cancelled + bar_width/2, chart_height - margin_bottom - bar_height,
                                fill='#ec4899', outline='', width=0
                            )
                    
                    # Y-axis labels with grid lines
                    num_grid_lines = 5
                    for i in range(num_grid_lines):
                        y_val = max_val * (i / (num_grid_lines - 1))
                        y_pos = chart_height - margin_bottom - (plot_height * i / (num_grid_lines - 1))
                        
                        # Grid line
                        chart_canvas.create_line(margin_left, y_pos, chart_width - margin_right, y_pos, 
                                               fill='#e5e7eb', width=1, dash=(2, 2))
                        
                        # Y-axis label
                        chart_canvas.create_text(margin_left - 10, y_pos, text=str(int(y_val)), 
                                                font=('Segoe UI', 9), fill='#6b7280', anchor='e')
            
            # Draw initial chart after a short delay to ensure canvas is sized
            def draw_initial_chart():
                chart_canvas.update_idletasks()
                draw_appointments_chart('daily')
            
            self.root.after(100, draw_initial_chart)
            
            # Toggle button handlers
            def toggle_daily():
                self.appointments_chart_mode = 'daily'
                daily_toggle.config(bg='#3b82f6', fg='white', font=('Segoe UI', 9, 'bold'))
                monthly_toggle.config(bg='#e5e7eb', fg='#6b7280', font=('Segoe UI', 9))
                chart_canvas.update_idletasks()
                draw_appointments_chart('daily')
            
            def toggle_monthly():
                self.appointments_chart_mode = 'monthly'
                monthly_toggle.config(bg='#3b82f6', fg='white', font=('Segoe UI', 9, 'bold'))
                daily_toggle.config(bg='#e5e7eb', fg='#6b7280', font=('Segoe UI', 9))
                chart_canvas.update_idletasks()
                draw_appointments_chart('monthly')
            
            daily_toggle.config(command=toggle_daily)
            monthly_toggle.config(command=toggle_monthly)
            
            # Redraw on canvas resize
            def on_canvas_configure(event):
                if event.width > 1 and event.height > 1:
                    draw_appointments_chart(self.appointments_chart_mode)
            
            chart_canvas.bind('<Configure>', on_canvas_configure)
            
            # Legend with better spacing
            legend_frame = tk.Frame(appointments_chart_frame, bg='white')
            legend_frame.pack(fill=tk.X, padx=25, pady=(0, 20))
            
            legend_items = [("Scheduled", "#3b82f6"), ("Completed", "#10b981"), ("Cancelled", "#ec4899")]
            for i, (label, color) in enumerate(legend_items):
                legend_item = tk.Frame(legend_frame, bg='white')
                legend_item.pack(side=tk.LEFT, padx=15)
                tk.Label(legend_item, text="●", font=('Segoe UI', 14), bg='white', fg=color).pack(side=tk.LEFT, padx=(0, 8))
                tk.Label(legend_item, text=label, font=('Segoe UI', 10, 'bold'), bg='white', fg='#374151').pack(side=tk.LEFT)
            
            # Revenue Insights Chart
            revenue_chart_frame = tk.Frame(left_column, bg='white', relief=tk.FLAT, bd=1)
            revenue_chart_frame.pack(fill=tk.BOTH, expand=True)
            
            revenue_header = tk.Frame(revenue_chart_frame, bg='white')
            revenue_header.pack(fill=tk.X, padx=20, pady=(15, 10))
            
            tk.Label(
                revenue_header,
                text="Revenue Insights",
                font=('Segoe UI', 14, 'bold'),
                bg='white',
                fg='#1f2937'
            ).pack(side=tk.LEFT)
            
            tk.Label(
                revenue_header,
                text="87% $100k >",
                font=('Segoe UI', 10),
                bg='white',
                fg='#6b7280'
            ).pack(side=tk.RIGHT)
            
            revenue_canvas = tk.Canvas(revenue_chart_frame, bg='white', height=200, highlightthickness=0)
            revenue_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
            
            revenue_canvas.create_text(200, 100, text="📊 Bar chart visualization\n(Monthly revenue)", 
                                      font=('Segoe UI', 11), fill='#9ca3af', justify=tk.CENTER)
            
            # Appointment Status Donut Chart (Middle Column)
            status_chart_frame = tk.Frame(middle_column, bg='white', relief=tk.FLAT, bd=1)
            status_chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            
            tk.Label(
                status_chart_frame,
                text="Appointment Status",
                font=('Segoe UI', 14, 'bold'),
                bg='white',
                fg='#1f2937'
            ).pack(pady=(15, 10))
            
            status_canvas = tk.Canvas(status_chart_frame, bg='white', height=250, highlightthickness=0)
            status_canvas.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 15))
            
            # Get real appointment status data
            all_appointments = self.db.get_all_appointments()
            total_appointments = len(all_appointments) if all_appointments else 0
            
            scheduled_count = sum(1 for a in all_appointments if a.get('status') == 'Scheduled') if all_appointments else 0
            completed_count = sum(1 for a in all_appointments if a.get('status') == 'Completed') if all_appointments else 0
            cancelled_count = sum(1 for a in all_appointments if a.get('status') in ['Cancelled', 'No Show']) if all_appointments else 0
            
            # Calculate percentages
            if total_appointments > 0:
                scheduled_pct = (scheduled_count / total_appointments) * 100
                completed_pct = (completed_count / total_appointments) * 100
                cancelled_pct = (cancelled_count / total_appointments) * 100
            else:
                scheduled_pct = completed_pct = cancelled_pct = 0
            
            def draw_donut_chart():
                """Draw donut chart with proper sizing"""
                status_canvas.delete("all")
                
                # Get canvas size for proper centering
                status_canvas.update_idletasks()
                canvas_width = status_canvas.winfo_width() or 300
                canvas_height = status_canvas.winfo_height() or 250
                
                center_x = canvas_width / 2
                center_y = canvas_height / 2 - 5  # Slightly above center
                radius = min(canvas_width, canvas_height) / 4.2  # Responsive size
                thickness = radius * 0.45  # Proportional thickness
            
                if total_appointments > 0:
                    # Draw donut chart segments
                    start_angle = -90  # Start at top
                    
                    # Scheduled (blue)
                    if scheduled_pct > 0:
                        extent = (scheduled_pct / 100) * 360
                        status_canvas.create_arc(
                            center_x - radius, center_y - radius,
                            center_x + radius, center_y + radius,
                            start=start_angle, extent=extent,
                            outline='#3b82f6', width=thickness, style='arc'
                        )
                        start_angle += extent
                    
                    # Completed (purple)
                    if completed_pct > 0:
                        extent = (completed_pct / 100) * 360
                        status_canvas.create_arc(
                            center_x - radius, center_y - radius,
                            center_x + radius, center_y + radius,
                            start=start_angle, extent=extent,
                            outline='#8b5cf6', width=thickness, style='arc'
                        )
                        start_angle += extent
                    
                    # Cancelled (pink)
                    if cancelled_pct > 0:
                        extent = (cancelled_pct / 100) * 360
                        status_canvas.create_arc(
                            center_x - radius, center_y - radius,
                            center_x + radius, center_y + radius,
                            start=start_angle, extent=extent,
                            outline='#ec4899', width=thickness, style='arc'
                        )
                    
                    # Center text with largest percentage
                    max_pct = max(scheduled_pct, completed_pct, cancelled_pct)
                    status_canvas.create_text(center_x, center_y, text=f"{max_pct:.1f}%", 
                                            font=('Segoe UI', 18, 'bold'), fill='#1f2937')
                else:
                    # No data
                    status_canvas.create_text(center_x, center_y, text="No Data", 
                                            font=('Segoe UI', 12), fill='#9ca3af')
            
            # Draw initial chart
            self.root.after(100, draw_donut_chart)
            
            # Redraw on canvas resize
            def on_status_canvas_configure(event):
                if event.width > 1 and event.height > 1:
                    draw_donut_chart()
            
            status_canvas.bind('<Configure>', on_status_canvas_configure)
            
            # Status legend with real data - better spacing
            status_legend = tk.Frame(status_chart_frame, bg='white')
            status_legend.pack(fill=tk.X, padx=25, pady=(0, 20))
            
            status_items = [
                ("Scheduled", "#3b82f6", f"{scheduled_pct:.1f}%", scheduled_count),
                ("Completed", "#8b5cf6", f"{completed_pct:.1f}%", completed_count),
                ("Cancelled", "#ec4899", f"{cancelled_pct:.1f}%", cancelled_count)
            ]
            for label, color, percent, count in status_items:
                item_frame = tk.Frame(status_legend, bg='white')
                item_frame.pack(fill=tk.X, pady=8, padx=10)
                tk.Label(item_frame, text="●", font=('Segoe UI', 14), bg='white', fg=color).pack(side=tk.LEFT, padx=(0, 12))
                tk.Label(item_frame, text=label, font=('Segoe UI', 11), bg='white', fg='#374151').pack(side=tk.LEFT)
                tk.Label(item_frame, text=f"{percent} ({count})", font=('Segoe UI', 11, 'bold'), bg='white', fg='#6b7280').pack(side=tk.RIGHT)
            
            # Recent Activities (Middle Column)
            activities_frame = tk.Frame(middle_column, bg='white', relief=tk.FLAT, bd=1)
            activities_frame.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(
                activities_frame,
                text="Recent Activities",
                font=('Segoe UI', 14, 'bold'),
                bg='white',
                fg='#1f2937'
            ).pack(pady=(15, 10))
            
            activities_list = tk.Frame(activities_frame, bg='white')
            activities_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
            
            # Get recent activities
            try:
                recent_activities = self.db.get_recent_activities(5)
                for activity in recent_activities:
                    activity_type = activity.get('type', '')
                    name = activity.get('name', 'Unknown')
                    action = activity.get('action', '')
                    
                    activity_text = f"{action.capitalize()} {name}"
                    time_text = "5m ago"  # Simplified
                    
                    activity_item = tk.Frame(activities_list, bg='white')
                    activity_item.pack(fill=tk.X, pady=8)
                    
                    tk.Label(
                        activity_item,
                        text=activity_text,
                        font=('Segoe UI', 10),
                        bg='white',
                        fg='#374151'
                    ).pack(anchor='w')
                    
                    tk.Label(
                        activity_item,
                        text=time_text,
                        font=('Segoe UI', 9),
                        bg='white',
                        fg='#9ca3af'
                    ).pack(anchor='w')
            except:
                tk.Label(activities_list, text="No recent activities", font=('Segoe UI', 10), 
                        bg='white', fg='#9ca3af').pack(pady=10)
            
            # Quick Actions (Right Column)
            quick_actions_frame = tk.Frame(right_column, bg='white', relief=tk.FLAT, bd=1)
            quick_actions_frame.pack(fill=tk.X, pady=(0, 15))
            
            tk.Label(
                quick_actions_frame,
                text="Quick Actions",
                font=('Segoe UI', 14, 'bold'),
                bg='white',
                fg='#1f2937'
            ).pack(pady=(15, 10))
            
            actions_list = tk.Frame(quick_actions_frame, bg='white')
            actions_list.pack(fill=tk.X, padx=15, pady=(0, 15))
            
            action_buttons = [
                ("➕ Add Patient", '#10b981', self.show_patients),
                ("📅 Book Appointment", '#3b82f6', self.show_appointments),
                ("👨‍⚕️ Add Doctor", '#8b5cf6', self.show_doctors),
                ("💰 Generate Invoice", '#06b6d4', self.show_billing)
            ]
            
            for text, color, command in action_buttons:
                btn = tk.Button(
                    actions_list,
                    text=text,
                    font=('Segoe UI', 11, 'bold'),
                    bg=color,
                    fg='white',
                    padx=15,
                    pady=12,
                    relief=tk.FLAT,
                    cursor='hand2',
                    command=command,
                    anchor='w',
                    width=20
                )
                btn.pack(fill=tk.X, pady=5)
            
            # Today's Appointments (Right Column)
            today_appts_frame = tk.Frame(right_column, bg='white', relief=tk.FLAT, bd=1)
            today_appts_frame.pack(fill=tk.BOTH, expand=True)
            
            header_frame = tk.Frame(today_appts_frame, bg='white')
            header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
            
            tk.Label(
                header_frame,
                text="Today's Appointments",
                font=('Segoe UI', 14, 'bold'),
                bg='white',
                fg='#1f2937'
            ).pack(side=tk.LEFT)
            
            tk.Label(
                header_frame,
                text="UPCOMING 3 HOURS",
                font=('Segoe UI', 9, 'bold'),
                bg='white',
                fg='#6b7280'
            ).pack(side=tk.RIGHT)
            
            appointments_list = tk.Frame(today_appts_frame, bg='white')
            appointments_list.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
            
            # Get today's appointments
            try:
                from utils import get_current_date
                today_appts = self.db.get_todays_appointments(get_current_date())
                for apt in today_appts[:5]:  # Show max 5
                    apt_time = apt.get('appointment_time', '')
                    patient_name = apt.get('patient_name', 'Unknown')
                    doctor_name = apt.get('doctor_name', '')
                    specialization = apt.get('specialization', '')
                    
                    apt_item = tk.Frame(appointments_list, bg='white')
                    apt_item.pack(fill=tk.X, pady=8)
                    
                    time_label = tk.Label(
                        apt_item,
                        text=apt_time,
                        font=('Segoe UI', 10, 'bold'),
                        bg='white',
                        fg='#1f2937'
                    )
                    time_label.pack(anchor='w')
                    
                    name_label = tk.Label(
                        apt_item,
                        text=f"{patient_name} - {doctor_name}",
                        font=('Segoe UI', 10),
                        bg='white',
                        fg='#374151'
                    )
                    name_label.pack(anchor='w')
                    
                    if specialization:
                        spec_label = tk.Label(
                            apt_item,
                            text=specialization,
                            font=('Segoe UI', 9),
                            bg='white',
                            fg='#6b7280'
                        )
                        spec_label.pack(anchor='w')
            except Exception as e:
                tk.Label(appointments_list, text="No appointments today", font=('Segoe UI', 10), 
                        bg='white', fg='#9ca3af').pack(pady=10)
            
            # Update scroll region after all content is loaded
            self.root.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            
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
    
    def logout(self):
        """Handle user logout"""
        from tkinter import messagebox
        
        # Confirm logout
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            log_info("User logging out...")
            self.db.close()
            log_info("Database connection closed")
            log_info("=" * 60)
            log_info("User logged out")
            log_info("=" * 60)
            
            # Destroy main window
            self.root.destroy()
            
            # Call logout callback if provided (to show login window again)
            if self.logout_callback:
                self.logout_callback()
    
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
        while True:  # Loop to allow re-login after logout
            # Show login window first
            from login_window import LoginWindow
            
            login_root = tk.Tk()
            authenticated_user = None
            login_successful = False
            
            def on_login_success(user):
                """Callback when login is successful"""
                nonlocal authenticated_user, login_successful
                authenticated_user = user
                login_successful = True
                login_root.quit()
            
            # Create and show login window
            login_app = LoginWindow(login_root, on_login_success)
            # Ensure window is visible
            login_root.deiconify()
            login_root.lift()
            login_root.focus_force()
            login_root.mainloop()
            login_root.destroy()
            
            # Check if user was authenticated
            if not authenticated_user or not login_successful:
                log_info("Login cancelled or failed - exiting application")
                break  # Exit the loop and close application
            
            log_info(f"User authenticated: {authenticated_user.get('username', 'Unknown')}")
            
            # Create main application window
            root = tk.Tk()
            
            # Track if logout was called
            logout_called = [False]  # Use list to allow modification in nested function
            
            # Define logout callback to return to login
            def on_logout():
                """Handle logout - destroy main window and return to login loop"""
                logout_called[0] = True
                root.destroy()
            
            app = HospitalManagementSystem(root, authenticated_user, on_logout)
            # Store app instance and authenticated user in root for easy access from modules
            root.app_instance = app
            root.authenticated_user = authenticated_user
            root.protocol("WM_DELETE_WINDOW", app.on_closing)
            # Start mainloop immediately - window is already shown in __init__
            root.mainloop()
            
            # If we reach here, the main window was closed
            # If logout was called, continue the loop to show login again
            # Otherwise, break to exit application
            if not logout_called[0]:
                break  # Window was closed normally, exit application
            
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

