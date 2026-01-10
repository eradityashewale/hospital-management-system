"""
Billing Management Module
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import tempfile
import os
import subprocess
import platform

# Backend imports
from backend.database import Database

# Utils imports
from utils.helpers import generate_id, get_current_date


class BillingModule:
    """Billing management interface"""
    
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
            text="Billing Management",
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
        tk.Label(filter_frame, text="Status:", font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#374151').pack(side=tk.LEFT, padx=(15, 5))
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=["All", "Pending", "Paid"],
            font=('Segoe UI', 10),
            width=12,
            state='readonly'
        )
        status_combo.pack(side=tk.LEFT, padx=5)
        # Auto-filter when status changes
        self.status_var.trace('w', lambda *args: self.apply_filters())
        
        # Add bill button with modern styling
        add_btn = tk.Button(
            top_frame,
            text="+ New Bill",
            command=self.add_bill,
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
        
        # Action buttons with modern styling (BEFORE list so they're visible)
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
            command=self.view_bill,
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
            text="✏️ Edit Bill",
            command=self.edit_bill,
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
            command=self.delete_bill,
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
        
        # List frame (AFTER action buttons)
        list_frame = tk.Frame(self.parent, bg='#f5f7fa')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)
        
        # Treeview
        columns = ('Bill ID', 'Patient', 'Date', 'Total Amount', 'Status')
        
        # Configure style FIRST before creating treeview
        style = ttk.Style()
        # Try to use a theme that supports custom styling
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
        
        # Configure column widths based on content - wider sizes for readability
        column_widths = {
            'Bill ID': 180,
            'Patient': 200,
            'Date': 150,
            'Total Amount': 150,
            'Status': 120
        }
        
        # Minimum widths to ensure content is readable
        min_widths = {
            'Bill ID': 150,
            'Patient': 150,
            'Date': 120,
            'Total Amount': 130,
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
        
        self.tree.bind('<Double-1>', self.view_bill)
        
        tk.Button(
            action_frame,
            text="🖨️ Print",
            command=self.print_bill,
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
            text="Mark Paid",
            command=self.mark_paid,
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
    
    def refresh_list(self):
        """Refresh bill list (shows all bills)"""
        # Reset filters
        self.patient_name_var.set("")
        self.date_var.set("")
        self.status_var.set("All")
        
        # apply_filters will be called automatically via trace
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
        
        try:
            if has_patient and has_date and has_status:
                # All three filters
                bills = self.db.get_bills_by_patient_name_date_and_status(patient_name, date, status)
            elif has_patient and has_date:
                # Patient name and date
                bills = self.db.get_bills_by_patient_name_and_date(patient_name, date)
            elif has_patient and has_status:
                # Patient name and status
                bills = self.db.get_bills_by_patient_name_and_status(patient_name, status)
            elif has_patient:
                # Patient name only
                bills = self.db.get_bills_by_patient_name(patient_name)
            elif has_date and has_status:
                # Date and status
                bills = self.db.get_bills_by_date_and_status(date, status)
            elif has_date:
                # Date only
                bills = self.db.get_bills_by_date(date)
            elif has_status:
                # Status only
                bills = self.db.get_bills_by_status(status)
            else:
                # No filters - show all
                bills = self.db.get_all_bills()
            
            for bill in bills:
                self.tree.insert('', tk.END, values=(
                    bill['bill_id'],
                    bill.get('patient_name', ''),
                    bill['bill_date'],
                    f"${bill['total_amount']:.2f}",
                    bill['payment_status']
                ))
        except Exception as e:
            # Log error but don't crash
            print(f"Error applying filters: {e}")
    
    def get_selected_bill_id(self):
        """Get selected bill ID"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a bill")
            return None
        item = self.tree.item(selection[0])
        return item['values'][0]
    
    def add_bill(self):
        """Open add bill dialog"""
        self.bill_dialog()
    
    def view_bill(self, event=None):
        """View selected bill details in read-only mode"""
        bill_id = self.get_selected_bill_id()
        if not bill_id:
            return
        
        bill = self.db.get_bill_by_id(bill_id)
        if not bill:
            messagebox.showerror("Error", "Bill not found")
            return
        
        # Open bill dialog in view-only mode
        self.bill_dialog(bill_id=bill_id, bill_data=bill, view_only=True)
    
    def print_bill(self):
        """Print bill - exactly like prescription printing"""
        bill_id = self.get_selected_bill_id()
        if not bill_id:
            return
        
        # Get bill details
        bill = self.db.get_bill_by_id(bill_id)
        if not bill:
            messagebox.showerror("Error", "Bill not found")
            return
        
        # Get patient details
        patient = self.db.get_patient_by_id(bill['patient_id'])
        if not patient:
            messagebox.showerror("Error", "Patient not found")
            return
        
        patient_name = bill.get('patient_name', '')
        if not patient_name:
            patient_name = f"{patient['first_name']} {patient['last_name']}"
        
        # Get doctor information from appointment if linked
        doctor = None
        if bill.get('appointment_id'):
            appointment = self.db.get_appointment_by_id(bill['appointment_id'])
            if appointment and appointment.get('doctor_id'):
                doctor = self.db.get_doctor_by_id(appointment['doctor_id'])
        
        # If no doctor from appointment, get first available doctor (for header)
        if not doctor:
            all_doctors = self.db.get_all_doctors()
            if all_doctors:
                doctor = all_doctors[0]  # Use first doctor as default
        
        # Try to generate PDF using reportlab (exactly like prescriptions)
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
            from datetime import datetime
            import os
            import platform
            import subprocess
            
            # Ask user where to save PDF (same as prescription)
            bill_date_str = bill['bill_date'].replace('-', '')
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"Bill_{bill_id}_{bill_date_str}.pdf"
            )
            
            if not filename:
                return  # User cancelled
            
            # Debug: Print that we're generating PDF
            print(f"Generating PDF for bill {bill_id} to {filename}")
            
            # Create PDF document (same margins as prescription)
            doc = SimpleDocTemplate(filename, pagesize=A4,
                                  rightMargin=15*mm, leftMargin=15*mm,
                                  topMargin=15*mm, bottomMargin=15*mm)
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Define styles (same as prescription)
            styles = getSampleStyleSheet()
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
            
            # Header - Doctor info on left, BILL/INVOICE on right (exactly like prescription)
            doctor_name = "Dr. Hospital"
            doctor_qual = "MBBS"
            doctor_spec = "General"
            doctor_phone = "N/A"
            doctor_email = "N/A"
            
            if doctor:
                doctor_name = f"Dr. {doctor.get('first_name', '')} {doctor.get('last_name', '')}".strip()
                if not doctor_name or doctor_name == "Dr.":
                    doctor_name = "Dr. Hospital"
                doctor_qual = doctor.get('qualification', '') or 'MBBS'
                doctor_spec = doctor.get('specialization', '') or 'General'
                doctor_phone = doctor.get('phone', 'N/A')
                doctor_email = doctor.get('email', 'N/A')
            
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
            
            patient_name_upper = patient_name.upper()
            
            # Format date for display
            try:
                date_obj = datetime.strptime(bill['bill_date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d.%m.%Y')
            except:
                formatted_date = bill['bill_date']
            
            # Header table (exactly like prescription)
            header_data = [
                [
                    Paragraph(f"<b>{doctor_name}</b><br/>"
                             f"{doctor_qual}<br/>"
                             f"Specialization: {doctor_spec}<br/>"
                             f"Mobile: {doctor_phone}<br/>"
                             f"Email: {doctor_email}", 
                             normal_style),
                    Paragraph(f"<b>BILL / INVOICE</b><br/>"
                             f"Date: {formatted_date}<br/>"
                             f"Bill ID: {bill_id}", 
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
            
            # Patient Information (exactly like prescription)
            patient_info_data = [
                ['Name:', patient_name_upper],
                ['Age/Gender:', f"{patient_age}/{patient_gender}" if patient_age else patient_gender],
                ['Patient ID:', bill['patient_id']],
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
            
            # Charges section (exactly like PRESCRIBED MEDICINES in prescription)
            elements.append(Paragraph("<b>CHARGES</b>", heading_style))
            
            charges_data = [['R', 'Description', 'Amount']]
            row_num = 1
            if bill.get('consultation_fee', 0) > 0:
                charges_data.append([
                    str(row_num),
                    'Consultation Fee',
                    f"${bill.get('consultation_fee', 0):,.2f}"
                ])
                row_num += 1
            if bill.get('medicine_cost', 0) > 0:
                charges_data.append([
                    str(row_num),
                    'Medicine Cost',
                    f"${bill.get('medicine_cost', 0):,.2f}"
                ])
                row_num += 1
            if bill.get('other_charges', 0) > 0:
                charges_data.append([
                    str(row_num),
                    'Other Charges',
                    f"${bill.get('other_charges', 0):,.2f}"
                ])
                row_num += 1
            
            # Always show at least one row
            if row_num == 1:
                charges_data.append([
                    '1',
                    'Consultation Fee',
                    f"${bill.get('consultation_fee', 0):,.2f}"
                ])
            
            # Table with same styling as medicines table in prescription
            # Column widths: R (8mm), Description (120mm), Amount (52mm) = 180mm total
            charges_table = Table(charges_data, colWidths=[8*mm, 120*mm, 52*mm])
            charges_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ]))
            elements.append(charges_table)
            elements.append(Spacer(1, 8*mm))
            
            # Total Amount (displayed after table)
            total_para = Paragraph(f"<b>Total Amount: ${bill['total_amount']:,.2f}</b>", normal_style)
            elements.append(total_para)
            elements.append(Spacer(1, 8*mm))
            
            # Payment Information (like Doctor's Notes in prescription)
            payment_info_text = f"Payment Status: {bill.get('payment_status', 'Pending')}<br/>"
            payment_info_text += f"Payment Method: {bill.get('payment_method', 'N/A')}"
            elements.append(Paragraph("<b>PAYMENT INFORMATION</b>", heading_style))
            elements.append(Paragraph(payment_info_text, normal_style))
            elements.append(Spacer(1, 8*mm))
            
            # Notes if available (like Doctor's Notes in prescription)
            if bill.get('notes'):
                elements.append(Paragraph("<b>NOTES</b>", heading_style))
                elements.append(Paragraph(bill['notes'].replace('\n', '<br/>'), normal_style))
                elements.append(Spacer(1, 8*mm))
            
            # Footer (exactly like prescription)
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
            messagebox.showinfo("Success", f"Bill saved successfully!\n\n{filename}")
            
            # Ask if user wants to open the PDF (same as prescription)
            if messagebox.askyesno("Open PDF", "Do you want to open the PDF now?"):
                system = platform.system()
                if system == "Windows":
                    os.startfile(filename)
                elif system == "Darwin":  # macOS
                    subprocess.run(['open', filename])
                else:  # Linux
                    subprocess.run(['xdg-open', filename])
            
        except ImportError as e:
            # Fallback to text printing if reportlab not available
            messagebox.showwarning("PDF Library Not Found", 
                "reportlab library is not installed.\n\n"
                "Please install it using: pip install reportlab\n\n"
                "Falling back to text format...")
            import traceback
            print(f"ImportError: {e}")
            print(traceback.format_exc())
            self._generate_text_bill(bill, patient, bill_id)
        except Exception as e:
            # Show detailed error for debugging
            import traceback
            error_details = traceback.format_exc()
            error_msg = f"Failed to generate PDF:\n\n{str(e)}\n\nWould you like to see the text version instead?"
            print(f"PDF Generation Error: {e}")
            print(error_details)
            
            # Ask user if they want text version or to retry
            response = messagebox.askyesno("PDF Generation Error", 
                f"{error_msg}\n\nClick 'Yes' to view text version, 'No' to cancel.")
            if response:
                self._generate_text_bill(bill, patient, bill_id)
            # If No, just return without showing text
    
    def _generate_text_bill(self, bill, patient, bill_id):
        """Fallback text bill generator"""
        patient_name = bill.get('patient_name', '')
        if not patient_name:
            patient_name = f"{patient['first_name']} {patient['last_name']}"
        
        print_text = f"""
================================================================
                    BILL / INVOICE
================================================================

Bill ID: {bill_id}
Date: {bill['bill_date']}

----------------------------------------------------------------
PATIENT INFORMATION
----------------------------------------------------------------
  Name: {patient_name}
  Patient ID: {bill['patient_id']}
  Phone: {patient.get('phone', 'N/A')}
  Email: {patient.get('email', 'N/A')}

----------------------------------------------------------------
CHARGES
----------------------------------------------------------------
  Consultation Fee:      ${bill.get('consultation_fee', 0):>15,.2f}
  Medicine Cost:         ${bill.get('medicine_cost', 0):>15,.2f}
  Other Charges:         ${bill.get('other_charges', 0):>15,.2f}
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TOTAL AMOUNT:          ${bill['total_amount']:>15,.2f}

----------------------------------------------------------------
PAYMENT INFORMATION
----------------------------------------------------------------
  Payment Status: {bill.get('payment_status', 'Pending')}
  Payment Method: {bill.get('payment_method', 'N/A')}
"""
        
        if bill.get('notes'):
            print_text += f"""
----------------------------------------------------------------
NOTES
----------------------------------------------------------------
{bill['notes']}
"""
        
        print_text += "\n"
        
        # Show print dialog
        self._show_print_dialog(print_text, f"Bill - {bill_id}")
    
    def show_bill_selection_popup(self, title, action_callback):
        """Show popup to select a bill"""
        popup = tk.Toplevel(self.parent)
        popup.title(title)
        popup.geometry("1100x650")
        popup.configure(bg='#f5f7fa')
        popup.transient(self.parent)
        popup.grab_set()
        
        # Center the window
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (1100 // 2)
        y = (popup.winfo_screenheight() // 2) - (650 // 2)
        popup.geometry(f"1100x650+{x}+{y}")
        
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
            text="Search by Bill ID, Patient Name, or Date:",
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
        
        # Bill list
        list_frame = tk.Frame(popup, bg='#f5f7fa', padx=20, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('Bill ID', 'Patient ID', 'Patient Name', 'Date', 'Total Amount', 'Status', 'Payment Method')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            if col == 'Bill ID':
                tree.column(col, width=150)
            elif col in ['Patient ID', 'Patient Name']:
                tree.column(col, width=150)
            elif col == 'Date':
                tree.column(col, width=120)
            elif col == 'Total Amount':
                tree.column(col, width=120)
            elif col == 'Status':
                tree.column(col, width=100)
            else:
                tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def load_bills():
            """Load bills based on search"""
            tree.delete(*tree.get_children())
            search_text = search_var.get().strip().lower()
            
            try:
                all_bills = self.db.get_all_bills()
                for bill in all_bills:
                    bill_id = bill.get('bill_id', '')
                    patient_id = bill.get('patient_id', '')
                    patient_name = bill.get('patient_name', patient_id)
                    date = bill.get('bill_date', '')
                    total = bill.get('total_amount', 0)
                    status = bill.get('payment_status', 'Pending')
                    payment_method = bill.get('payment_method', 'Cash')
                    
                    if (not search_text or 
                        search_text in bill_id.lower() or
                        search_text in patient_id.lower() or
                        search_text in patient_name.lower() or
                        search_text in date.lower() or
                        search_text in status.lower()):
                        tree.insert('', tk.END, values=(
                            bill_id,
                            patient_id,
                            patient_name,
                            date,
                            f"₹{total:.2f}" if total else "₹0.00",
                            status,
                            payment_method
                        ))
            except Exception as e:
                print(f"Error loading bills: {e}")
        
        search_var.trace('w', lambda *args: load_bills())
        load_bills()  # Initial load
        
        # Button frame
        button_frame = tk.Frame(popup, bg='#f5f7fa', padx=20, pady=15)
        button_frame.pack(fill=tk.X)
        
        def on_select():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a bill")
                return
            
            item = tree.item(selection[0])
            bill_id = item['values'][0]
            popup.destroy()
            action_callback(bill_id)
        
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
    
    def edit_bill(self):
        """Edit selected bill - opens in EDIT mode"""
        bill_id = self.get_selected_bill_id()
        if not bill_id:
            # If no selection, show selection popup
            self.show_bill_selection_popup(
                "Select Bill to Edit",
                lambda bid: self.edit_bill_by_id(bid)
            )
            return
        
        # Directly edit the selected bill
        self.edit_bill_by_id(bill_id)
    
    def edit_bill_by_id(self, bill_id):
        """Edit bill by ID - explicitly opens in EDIT mode"""
        bill = self.db.get_bill_by_id(bill_id)
        if not bill:
            messagebox.showerror("Error", "Bill not found")
            return
        
        # Explicitly pass view_only=False to ensure fields are editable
        self.bill_dialog(bill_id=bill_id, bill_data=bill, view_only=False)
    
    def delete_bill(self):
        """Delete selected bill"""
        bill_id = self.get_selected_bill_id()
        if not bill_id:
            # If no selection, show selection popup
            self.show_bill_selection_popup(
                "Select Bill to Delete",
                lambda bid: self.delete_bill_by_id(bid)
            )
            return
        
        # Directly delete the selected bill
        self.delete_bill_by_id(bill_id)
    
    def delete_bill_by_id(self, bill_id):
        """Delete bill by ID"""
        bill = self.db.get_bill_by_id(bill_id)
        if not bill:
            messagebox.showerror("Error", "Bill not found")
            return
        
        # Show confirmation with bill details
        patient_name = bill.get('patient_name', bill.get('patient_id', 'Unknown'))
        total = bill.get('total_amount', 0)
        date = bill.get('bill_date', '')
        
        confirm_msg = f"Are you sure you want to DELETE this bill?\n\n"
        confirm_msg += f"Bill ID: {bill_id}\n"
        confirm_msg += f"Patient: {patient_name}\n"
        confirm_msg += f"Date: {date}\n"
        confirm_msg += f"Total Amount: ₹{total:.2f}\n\n"
        confirm_msg += "This action cannot be undone!"
        
        if messagebox.askyesno("Confirm Delete", confirm_msg, icon='warning'):
            try:
                if self.db.delete_bill(bill_id):
                    messagebox.showinfo("Success", f"Bill {bill_id} deleted successfully")
                    self.refresh_list()
                else:
                    messagebox.showerror("Error", "Failed to delete bill")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete bill: {str(e)}")
    
    def mark_paid(self):
        """Mark bill as paid"""
        bill_id = self.get_selected_bill_id()
        if not bill_id:
            return
        
        bill = self.db.get_bill_by_id(bill_id)
        if not bill:
            messagebox.showerror("Error", "Bill not found")
            return
        
        # Update payment status
        bill['payment_status'] = 'Paid'
        if not bill.get('payment_method'):
            bill['payment_method'] = 'Cash'  # Default payment method
        
        if self.db.update_bill(bill_id, bill):
            messagebox.showinfo("Success", f"Bill {bill_id} marked as paid")
            self.refresh_list()
        else:
            messagebox.showerror("Error", "Failed to update bill")
    
    def bill_dialog(self, bill_id=None, bill_data=None, view_only=False):
        """Bill form dialog - for adding new or editing existing bill"""
        is_edit = bill_id is not None
        dialog = tk.Toplevel(self.parent)
        # Set title based on mode
        if view_only:
            dialog.title("View Bill Details")
        elif is_edit:
            dialog.title("Edit Bill - Editable")
        else:
            dialog.title("New Bill")
        dialog.geometry("500x600")  # Increased height to ensure buttons are visible
        dialog.configure(bg='#f5f7fa')
        dialog.transient(self.parent)
        
        # Get root window for focus management
        root = self.parent.winfo_toplevel()
        
        # Make dialog modal but ensure input works
        dialog.lift()  # Bring dialog to front first
        dialog.focus_force()  # Force focus on dialog
        # Use grab_set_global=False to allow other windows to work
        try:
            dialog.grab_set_global(False)
        except:
            dialog.grab_set()  # Fallback for older tkinter versions
        
        main_frame = tk.Frame(dialog, bg='#f5f7fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Add mode indicator
        if view_only:
            mode_label = tk.Label(main_frame, text="📖 VIEW MODE (Read Only)", 
                                 font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#ef4444')
            mode_label.pack(pady=5)
        elif is_edit:
            mode_label = tk.Label(main_frame, text="✏️ EDIT MODE (Editable)", 
                                 font=('Segoe UI', 11, 'bold'), bg='#f5f7fa', fg='#10b981')
            mode_label.pack(pady=5)
        
        if not is_edit:
            bill_id = generate_id('BILL')
        tk.Label(main_frame, text=f"Bill ID: {bill_id}", font=('Segoe UI', 13, 'bold'), bg='#f5f7fa', fg='#1a237e').pack(pady=8)
        
        # Form fields - don't expand to fill all space
        form_frame = tk.Frame(main_frame, bg='#f0f0f0')
        form_frame.pack(fill=tk.X, expand=False, pady=10)
        
        # Patient selection with searchable dropdown
        tk.Label(form_frame, text="Patient ID *:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        
        # Get all patients for dropdown
        all_patients = self.db.get_all_patients()
        patient_options = []
        patient_id_map = {}  # Map display string to patient_id
        
        for p in all_patients:
            display_text = f"{p['patient_id']} - {p['first_name']} {p['last_name']}"
            patient_options.append(display_text)
            patient_id_map[display_text] = p['patient_id']
        
        patient_var = tk.StringVar()
        if is_edit and bill_data:
            # Set current patient in edit mode
            current_patient_id = bill_data.get('patient_id', '')
            for p in all_patients:
                if p['patient_id'] == current_patient_id:
                    display_text = f"{p['patient_id']} - {p['first_name']} {p['last_name']}"
                    patient_var.set(display_text)
                    break
        
        # Set state based on view_only
        combo_state = 'readonly' if view_only else 'normal'
        entry_state = 'readonly' if view_only else 'normal'
        patient_combo = ttk.Combobox(
            form_frame, 
            textvariable=patient_var,
            values=patient_options,
            font=('Arial', 10),
            width=37,
            state=combo_state
        )
        patient_combo.pack(fill=tk.X, pady=5)
        
        # Make patient combo auto-focus on mouse enter
        def on_patient_enter(event):
            patient_combo.focus_set()
        patient_combo.bind('<Enter>', on_patient_enter)
        
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
        
        tk.Label(form_frame, text="Date:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        date_entry = tk.Entry(form_frame, font=('Arial', 10), width=40, state=entry_state)
        if is_edit and bill_data:
            date_entry.insert(0, bill_data.get('bill_date', get_current_date()))
        else:
            date_entry.insert(0, get_current_date())
        date_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Consultation Fee:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        consultation_entry = tk.Entry(form_frame, font=('Arial', 10), width=40, state=entry_state)
        if is_edit and bill_data:
            consultation_entry.insert(0, str(bill_data.get('consultation_fee', 0)))
        else:
            consultation_entry.insert(0, "0")
        consultation_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Medicine Cost:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        medicine_entry = tk.Entry(form_frame, font=('Arial', 10), width=40, state=entry_state)
        if is_edit and bill_data:
            medicine_entry.insert(0, str(bill_data.get('medicine_cost', 0)))
        else:
            medicine_entry.insert(0, "0")
        medicine_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Other Charges:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        other_entry = tk.Entry(form_frame, font=('Arial', 10), width=40, state=entry_state)
        if is_edit and bill_data:
            other_entry.insert(0, str(bill_data.get('other_charges', 0)))
        else:
            other_entry.insert(0, "0")
        other_entry.pack(fill=tk.X, pady=5)
        
        # Total display
        if is_edit and bill_data:
            initial_total = bill_data.get('total_amount', 0)
            total_label = tk.Label(form_frame, text=f"Total: ${initial_total:.2f}", font=('Arial', 14, 'bold'), bg='#f0f0f0', fg='#27ae60')
        else:
            total_label = tk.Label(form_frame, text="Total: $0.00", font=('Arial', 14, 'bold'), bg='#f0f0f0', fg='#27ae60')
        total_label.pack(pady=10)
        
        def calculate_total():
            try:
                consultation = float(consultation_entry.get() or 0)
                medicine = float(medicine_entry.get() or 0)
                other = float(other_entry.get() or 0)
                total = consultation + medicine + other
                total_label.config(text=f"Total: ${total:.2f}")
            except:
                total_label.config(text="Total: $0.00")
        
        consultation_entry.bind('<KeyRelease>', lambda e: calculate_total())
        medicine_entry.bind('<KeyRelease>', lambda e: calculate_total())
        other_entry.bind('<KeyRelease>', lambda e: calculate_total())
        
        tk.Label(form_frame, text="Payment Status:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        status_var = tk.StringVar()
        if view_only:
            # For view mode, use a label instead of combobox
            current_status = bill_data.get('payment_status', 'Pending') if is_edit and bill_data else 'Pending'
            status_label = tk.Label(form_frame, text=current_status, font=('Arial', 10), bg='#f9fafb', fg='#374151', relief=tk.SOLID, bd=1, anchor='w', padx=5, pady=5)
            status_label.pack(fill=tk.X, pady=5)
            status_combo = None
        else:
            status_combo = ttk.Combobox(form_frame, textvariable=status_var, values=['Pending', 'Paid', 'Partial'], width=37, state=combo_state)
            if is_edit and bill_data:
                status_var.set(bill_data.get('payment_status', 'Pending'))
            else:
                status_var.set('Pending')
            status_combo.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Payment Method:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        payment_var = tk.StringVar()
        if view_only:
            # For view mode, use a label instead of combobox
            current_payment = bill_data.get('payment_method', '') if is_edit and bill_data else ''
            payment_label = tk.Label(form_frame, text=current_payment or 'Not specified', font=('Arial', 10), bg='#f9fafb', fg='#374151', relief=tk.SOLID, bd=1, anchor='w', padx=5, pady=5)
            payment_label.pack(fill=tk.X, pady=5)
            payment_combo = None
        else:
            payment_combo = ttk.Combobox(form_frame, textvariable=payment_var, values=['Cash', 'Card', 'Online', 'Insurance'], width=37, state=combo_state)
            if is_edit and bill_data:
                payment_var.set(bill_data.get('payment_method', ''))
            payment_combo.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Notes:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        notes_text = tk.Text(form_frame, font=('Arial', 10), width=37, height=3, state='normal' if not view_only else 'disabled')
        if is_edit and bill_data:
            notes_text.insert('1.0', bill_data.get('notes', ''))
            if view_only:
                notes_text.config(state='disabled')
        notes_text.pack(fill=tk.X, pady=5)
        
        def save_bill():
            # Extract patient_id from combobox selection
            selected_patient = patient_var.get()
            if not selected_patient:
                messagebox.showerror("Error", "Patient ID is required")
                return
            
            # Get patient_id from the selection (format: "PATIENT_ID - FirstName LastName")
            patient_id = None
            if selected_patient in patient_id_map:
                patient_id = patient_id_map[selected_patient]
            else:
                # If user typed directly, try to extract ID (take first part before " - ")
                parts = selected_patient.split(' - ')
                if parts:
                    patient_id = parts[0].strip()
            
            if not patient_id:
                messagebox.showerror("Error", "Please select a valid patient")
                return
            
            try:
                consultation = float(consultation_entry.get() or 0)
                medicine = float(medicine_entry.get() or 0)
                other = float(other_entry.get() or 0)
                total = consultation + medicine + other
            except:
                messagebox.showerror("Error", "Invalid amount values")
                return
            
            data = {
                'patient_id': patient_id,
                'bill_date': date_entry.get() or get_current_date(),
                'consultation_fee': consultation,
                'medicine_cost': medicine,
                'other_charges': other,
                'total_amount': total,
                'payment_status': status_var.get() or 'Pending',
                'payment_method': payment_var.get() or '',
                'notes': notes_text.get('1.0', tk.END).strip()
            }
            
            if is_edit:
                # Update existing bill
                if self.db.update_bill(bill_id, data):
                    # Release grab BEFORE destroying dialog
                    try:
                        dialog.grab_release()
                    except Exception as e:
                        pass
                    
                    # Destroy dialog first
                    dialog.destroy()
                    
                    # Process all pending events immediately
                    root.update_idletasks()
                    root.update()
                    root.update_idletasks()
                    
                    # Return focus to main window immediately
                    root.focus_force()
                    root.update_idletasks()
                    root.update()
                    root.update_idletasks()
                    
                    # Show message after dialog is closed
                    root.after(150, lambda: messagebox.showinfo("Success", "Bill updated successfully"))
                    # Refresh list asynchronously
                    root.after(250, self.refresh_list)
                else:
                    messagebox.showerror("Error", "Failed to update bill")
            else:
                # Add new bill
                data['bill_id'] = bill_id
                if self.db.add_bill(data):
                    # Release grab BEFORE destroying dialog
                    try:
                        dialog.grab_release()
                    except Exception as e:
                        pass
                    
                    # Destroy dialog first
                    dialog.destroy()
                    
                    # Process all pending events immediately - CRITICAL for immediate button response
                    root.update_idletasks()
                    root.update()
                    root.update_idletasks()
                    
                    # Return focus to main window immediately
                    root.focus_force()
                    root.update_idletasks()
                    root.update()
                    
                    # Ensure all events are processed and UI is ready
                    root.update_idletasks()
                    
                    # Final update to ensure buttons are immediately responsive
                    root.update()
                    root.update_idletasks()
                    
                    # Show message after dialog is closed (non-blocking) - delayed to not interfere
                    root.after(150, lambda: messagebox.showinfo("Success", "Bill created successfully"))
                    # Refresh list asynchronously
                    root.after(250, self.refresh_list)
                else:
                    messagebox.showerror("Error", "Failed to create bill")
        
        def close_dialog():
            # Release grab BEFORE destroying
            try:
                dialog.grab_release()
            except Exception as e:
                pass
            
            # Destroy dialog
            dialog.destroy()
            
            # Process all pending events immediately - CRITICAL for immediate button response
            root.update_idletasks()
            root.update()
            root.update_idletasks()
            
            # Return focus to main window immediately
            root.focus_force()
            root.update_idletasks()
            root.update()
            
            # Ensure all events are processed and UI is ready
            root.update_idletasks()
        
        # Only show save button if not in view_only mode
        if not view_only:
            # Button frame - pack first to ensure it's at the bottom
            button_frame = tk.Frame(dialog, bg='#f5f7fa', relief=tk.FLAT, bd=0)
            button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)
            
            # Inner frame for button spacing
            inner_button_frame = tk.Frame(button_frame, bg='#f5f7fa')
            inner_button_frame.pack(fill=tk.X, padx=25, pady=20)
            
            tk.Button(
                inner_button_frame,
                text="Save",
                command=save_bill,
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
            
            tk.Button(
                inner_button_frame,
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
            # For view_only mode, just show close button
            close_btn = tk.Button(
                main_frame,
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
            )
            close_btn.pack(pady=20)
        
        # Ensure everything is properly laid out
        dialog.update_idletasks()
        # Make sure dialog is not resizable below minimum size needed for buttons
        dialog.resizable(True, True)
        dialog.minsize(500, 600)
        
        # Ensure dialog releases grab when closed via window close button
        def on_close():
            try:
                dialog.grab_release()
            except:
                pass
            dialog.destroy()
            
            # Process all pending events immediately - CRITICAL for immediate button response
            root.update_idletasks()
            root.update()
            root.update_idletasks()
            
            # Return focus to main window immediately
            root.focus_force()
            root.update_idletasks()
            root.update()
            
            # Ensure all events are processed and UI is ready
            root.update_idletasks()
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
        # Bind Escape key to close dialog
        def on_escape(event):
            close_dialog()
            return "break"
        dialog.bind('<Escape>', on_escape)
    
    def _show_print_dialog(self, text, title="Print"):
        """Show print dialog with formatted text"""
        print_dialog = tk.Toplevel(self.parent)
        print_dialog.title(title)
        print_dialog.geometry("700x600")
        print_dialog.configure(bg='#f0f0f0')
        print_dialog.transient(self.parent)
        
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
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
                temp_file.write(text)
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
                    subprocess.run(['lp', temp_file.name], check=True)
                    messagebox.showinfo("Print", "Document sent to default printer!")
                
                # Clean up after a delay
                def cleanup():
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                print_dialog.after(5000, cleanup)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to print: {str(e)}\n\nYou can save the document and print it manually.")
        
        def save_as_pdf():
            """Save document as PDF"""
            try:
                # Generate default filename from title
                default_filename = title.replace(" - ", "_").replace(" ", "_") + ".pdf"
                
                # Try using reportlab if available
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                    from reportlab.lib.styles import getSampleStyleSheet
                    from reportlab.lib.units import inch
                    
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".pdf",
                        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                        title="Save Bill as PDF",
                        initialfile=default_filename
                    )
                    
                    if filename:
                        doc = SimpleDocTemplate(filename, pagesize=letter)
                        styles = getSampleStyleSheet()
                        story = []
                        
                        # Add content line by line
                        for line in text.split('\n'):
                            if line.strip():
                                # Handle special characters
                                line = line.replace('╔', '=').replace('╗', '=')
                                line = line.replace('║', '|').replace('╚', '=')
                                line = line.replace('╝', '=').replace('━', '-')
                                line = line.replace('═', '=')
                                
                                if 'BILL' in line.upper() or 'INVOICE' in line.upper() or '━━━' in line:
                                    story.append(Paragraph(line, styles['Heading1']))
                                else:
                                    story.append(Paragraph(line, styles['Normal']))
                                story.append(Spacer(1, 0.1*inch))
                        
                        doc.build(story)
                        messagebox.showinfo("Success", f"Bill saved as PDF:\n{filename}")
                    return
                except ImportError:
                    # reportlab not available - install it or use alternative
                    messagebox.showwarning(
                        "PDF Library Not Found",
                        "The 'reportlab' library is required to save as PDF.\n\n"
                        "Please install it using: pip install reportlab\n\n"
                        "Alternatively, you can save as text file and convert it manually."
                    )
                    
                    # Fallback: Save as text file
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".txt",
                        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                        title="Save Bill",
                        initialfile=default_filename.replace(".pdf", ".txt")
                    )
                    
                    if filename:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(text)
                        messagebox.showinfo("Success", 
                            f"Bill saved as text file:\n{filename}\n\n"
                            f"Note: Install reportlab (pip install reportlab) to save as PDF directly.")
                        
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")
        
        tk.Button(
            button_frame,
            text="🖨️ Print",
            command=print_text,
            font=('Arial', 11, 'bold'),
            bg='#e67e22',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="📄 Save as PDF",
            command=save_as_pdf,
            font=('Arial', 11, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        def close_dialog():
            print_dialog.destroy()
        
        tk.Button(
            button_frame,
            text="Close",
            command=close_dialog,
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
