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
        
        # Action buttons - Doctor-friendly popup-based actions (BEFORE list so they're visible)
        action_frame = tk.Frame(self.parent, bg='#f5f7fa')
        action_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Button labels for doctors
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
        
        tk.Button(
            action_frame,
            text="✏️ Edit Prescription",
            command=self.edit_prescription,
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
            command=self.delete_prescription,
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
        
        # Single-click to open prescription in editable mode
        self.tree.bind('<Button-1>', lambda e: self.on_prescription_click(e))
        # Double-click also opens in editable mode
        self.tree.bind('<Double-1>', self.edit_prescription)
    
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
    
    def show_prescription_selection_popup(self, title, action_callback):
        """Show popup to select a prescription - doctor-friendly"""
        popup = tk.Toplevel(self.parent)
        popup.title(title)
        popup.geometry("900x600")
        popup.configure(bg='#f5f7fa')
        popup.transient(self.parent)
        popup.grab_set()
        
        # Center the window
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (900 // 2)
        y = (popup.winfo_screenheight() // 2) - (600 // 2)
        popup.geometry(f"900x600+{x}+{y}")
        
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
            text="Search by Patient Name or Date:",
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
        
        # Prescription list
        list_frame = tk.Frame(popup, bg='#f5f7fa', padx=20, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Patient ID', 'Patient Name', 'Doctor', 'Date', 'Diagnosis')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            if col == 'ID':
                tree.column(col, width=150)
            elif col == 'Patient ID':
                tree.column(col, width=120)
            elif col == 'Patient Name':
                tree.column(col, width=180)
            elif col == 'Doctor':
                tree.column(col, width=200)
            elif col == 'Date':
                tree.column(col, width=120)
            else:
                tree.column(col, width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def load_prescriptions():
            """Load prescriptions based on search"""
            tree.delete(*tree.get_children())
            search_text = search_var.get().strip()
            
            try:
                if search_text:
                    # Try to search by patient name first
                    prescriptions = self.db.get_prescriptions_by_patient_name(search_text)
                    # If no results, try by date
                    if not prescriptions:
                        prescriptions = self.db.get_prescriptions_by_date(search_text)
                else:
                    prescriptions = self.db.get_all_prescriptions()
                
                for pres in prescriptions:
                    doctor_display = pres.get('doctor_name', pres.get('doctor_id', 'Unknown'))
                    patient_display = pres.get('patient_name', pres.get('patient_id', 'Unknown'))
                    diagnosis = pres.get('diagnosis', '')
                    if len(diagnosis) > 50:
                        diagnosis = diagnosis[:47] + '...'
                    
                    tree.insert('', tk.END, values=(
                        pres['prescription_id'],
                        pres['patient_id'],
                        patient_display,
                        doctor_display,
                        pres['prescription_date'],
                        diagnosis
                    ))
            except Exception as e:
                print(f"Error loading prescriptions: {e}")
        
        search_var.trace('w', lambda *args: load_prescriptions())
        load_prescriptions()  # Initial load
        
        # Button frame
        button_frame = tk.Frame(popup, bg='#f5f7fa', padx=20, pady=15)
        button_frame.pack(fill=tk.X)
        
        def on_select():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a prescription")
                return
            
            item = tree.item(selection[0])
            prescription_id = item['values'][0]
            popup.destroy()
            action_callback(prescription_id)
        
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
    
    def add_prescription(self):
        """Open add prescription form in popup window"""
        self.show_prescription_form_popup()
    
    def on_prescription_click(self, event):
        """Handle single-click on prescription to open in editable mode"""
        # Identify the item that was clicked
        item = self.tree.identify_row(event.y)
        if item:
            # Get prescription ID from the first column
            values = self.tree.item(item, 'values')
            if values and len(values) > 0:
                prescription_id = values[0]
                if prescription_id:
                    # Open in editable mode
                    self.show_prescription_form_popup(prescription_id=prescription_id, view_only=False)
    
    def get_selected_prescription_id(self):
        """Get selected prescription ID from main tree"""
        selection = self.tree.selection()
        if not selection:
            return None
        item = self.tree.item(selection[0])
        # Prescription ID is in the first column (index 0)
        return item['values'][0] if item['values'] else None
    
    def edit_prescription(self, event=None):
        """Edit selected prescription - opens in EDIT mode"""
        prescription_id = self.get_selected_prescription_id()
        if not prescription_id:
            # If no selection, show selection popup
            self.show_prescription_selection_popup(
                "Select Prescription to Edit",
                lambda pid: self.show_prescription_form_popup(prescription_id=pid, view_only=False)
            )
            return
        
        # Directly edit the selected prescription
        prescription = self.db.get_prescription_by_id(prescription_id)
        if not prescription:
            messagebox.showerror("Error", "Prescription not found")
            return
        
        # Explicitly pass view_only=False to ensure fields are editable
        self.show_prescription_form_popup(prescription_id=prescription_id, view_only=False)
    
    def view_prescription(self, event=None):
        """View selected prescription details"""
        prescription_id = self.get_selected_prescription_id()
        if not prescription_id:
            # If no selection, show selection popup
            self.show_prescription_selection_popup(
                "Select Prescription to View",
                self.view_prescription_details
            )
            return
        
        # Directly view the selected prescription
        self.view_prescription_details(prescription_id)
    
    def delete_prescription(self, event=None):
        """Delete selected prescription"""
        prescription_id = self.get_selected_prescription_id()
        if not prescription_id:
            # If no selection, show selection popup
            self.show_prescription_selection_popup(
                "Select Prescription to Delete",
                self.delete_prescription_by_id
            )
            return
        
        # Directly delete the selected prescription
        self.delete_prescription_by_id(prescription_id)
    
    def delete_prescription_by_id(self, prescription_id):
        """Delete prescription by ID"""
        prescription_data = self.db.get_prescription_by_id(prescription_id)
        if not prescription_data:
            messagebox.showerror("Error", "Prescription not found")
            return
        
        # Get patient and doctor details for confirmation
        patient = self.db.get_patient_by_id(prescription_data.get('patient_id'))
        doctor = self.db.get_doctor_by_id(prescription_data.get('doctor_id'))
        
        patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}" if patient else prescription_data.get('patient_id', 'Unknown')
        doctor_name = f"Dr. {doctor.get('first_name', '')} {doctor.get('last_name', '')}" if doctor else prescription_data.get('doctor_id', 'Unknown')
        date = prescription_data.get('prescription_date', '')
        
        confirm_msg = f"Are you sure you want to DELETE this prescription?\n\n"
        confirm_msg += f"Prescription ID: {prescription_id}\n"
        confirm_msg += f"Patient: {patient_name}\n"
        confirm_msg += f"Doctor: {doctor_name}\n"
        confirm_msg += f"Date: {date}\n\n"
        confirm_msg += "This action cannot be undone!"
        
        if messagebox.askyesno("Confirm Delete", confirm_msg, icon='warning'):
            try:
                # Check if delete_prescription method exists
                if hasattr(self.db, 'delete_prescription'):
                    if self.db.delete_prescription(prescription_id):
                        messagebox.showinfo("Success", "Prescription deleted successfully")
                        self.apply_filters()  # Refresh the list
                    else:
                        messagebox.showerror("Error", "Failed to delete prescription")
                else:
                    messagebox.showerror("Error", "Delete functionality not available in database")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete prescription: {str(e)}")
    
    def view_prescription_details(self, prescription_id):
        """View prescription details in a popup"""
        prescription_data = self.db.get_prescription_by_id(prescription_id)
        if not prescription_data:
            messagebox.showerror("Error", "Prescription not found")
            return
        
        items = self.db.get_prescription_items(prescription_id)
        
        # Create popup window
        popup = tk.Toplevel(self.parent)
        popup.title(f"Prescription Details - {prescription_id}")
        popup.geometry("800x700")
        popup.configure(bg='#f5f7fa')
        popup.transient(self.parent)
        popup.grab_set()
        
        # Center the window
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (800 // 2)
        y = (popup.winfo_screenheight() // 2) - (700 // 2)
        popup.geometry(f"800x700+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(popup, bg='#1e40af', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text=f"Prescription Details - {prescription_id}",
            font=('Segoe UI', 14, 'bold'),
            bg='#1e40af',
            fg='white'
        ).pack(pady=18)
        
        # Scrollable content
        canvas = tk.Canvas(popup, bg='#f5f7fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f5f7fa')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=15)
        scrollbar.pack(side="right", fill="y", pady=15)
        
        # Content frame
        content_frame = tk.Frame(scrollable_frame, bg='#ffffff', relief=tk.RAISED, bd=2)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Patient and Doctor info
        info_frame = tk.LabelFrame(
            content_frame,
            text="Patient & Doctor Information",
            font=('Segoe UI', 11, 'bold'),
            bg='#ffffff',
            fg='#1a237e',
            padx=15,
            pady=10
        )
        info_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Get patient and doctor details
        patient = self.db.get_patient_by_id(prescription_data.get('patient_id'))
        doctor = self.db.get_doctor_by_id(prescription_data.get('doctor_id'))
        
        info_text = f"Patient: {patient.get('first_name', '')} {patient.get('last_name', '')} ({prescription_data.get('patient_id')})\n"
        info_text += f"Doctor: Dr. {doctor.get('first_name', '')} {doctor.get('last_name', '')} ({prescription_data.get('doctor_id')})\n"
        info_text += f"Date: {prescription_data.get('prescription_date', '')}\n"
        if prescription_data.get('appointment_id'):
            info_text += f"Appointment ID: {prescription_data.get('appointment_id')}\n"
        
        tk.Label(
            info_frame,
            text=info_text,
            font=('Segoe UI', 10),
            bg='#ffffff',
            fg='#374151',
            justify=tk.LEFT,
            anchor='w'
        ).pack(fill=tk.X, padx=5, pady=5)
        
        # Diagnosis
        if prescription_data.get('diagnosis'):
            diagnosis_frame = tk.LabelFrame(
                content_frame,
                text="Diagnosis",
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#1a237e',
                padx=15,
                pady=10
            )
            diagnosis_frame.pack(fill=tk.X, padx=15, pady=10)
            
            diagnosis_label = tk.Label(
                diagnosis_frame,
                text=prescription_data.get('diagnosis', ''),
                font=('Segoe UI', 10),
                bg='#ffffff',
                fg='#374151',
                wraplength=700,
                justify=tk.LEFT,
                anchor='w'
            )
            diagnosis_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Medicines
        if items:
            medicines_frame = tk.LabelFrame(
                content_frame,
                text="Prescribed Medicines",
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#1a237e',
                padx=15,
                pady=10
            )
            medicines_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
            
            # Treeview for medicines
            med_columns = ('Medicine', 'Type', 'Dosage', 'Frequency', 'Duration', 'Instructions')
            med_tree = ttk.Treeview(medicines_frame, columns=med_columns, show='headings', height=min(len(items), 10))
            
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
            
            for item in items:
                med_tree.insert('', tk.END, values=(
                    item.get('medicine_name', ''),
                    item.get('medicine_type', ''),
                    item.get('dosage', ''),
                    item.get('frequency', ''),
                    item.get('duration', ''),
                    item.get('instructions', '')
                ))
            
            med_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Notes
        if prescription_data.get('notes'):
            notes_frame = tk.LabelFrame(
                content_frame,
                text="Doctor's Notes",
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#1a237e',
                padx=15,
                pady=10
            )
            notes_frame.pack(fill=tk.X, padx=15, pady=10)
            
            notes_label = tk.Label(
                notes_frame,
                text=prescription_data.get('notes', ''),
                font=('Segoe UI', 10),
                bg='#ffffff',
                fg='#374151',
                wraplength=700,
                justify=tk.LEFT,
                anchor='w'
            )
            notes_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Close button
        close_btn = tk.Button(
            popup,
            text="Close",
            command=popup.destroy,
            font=('Segoe UI', 10, 'bold'),
            bg='#6b7280',
            fg='white',
            padx=40,
            pady=10,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#4b5563'
        )
        close_btn.pack(pady=15)
    
    def show_prescription_form_popup(self, prescription_id=None, view_only=False):
        """Show prescription form in popup window - doctor-friendly"""
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
        
        # Create popup window
        popup = tk.Toplevel(self.parent)
        # Set title based on mode
        if view_only:
            popup.title("View Prescription Details")
        elif is_editing:
            popup.title("Edit Prescription - Editable")
        else:
            popup.title("New Prescription")
        
        # Get screen dimensions and set window to fullscreen
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        
        # Set window geometry to full screen
        popup.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Try to maximize window (works on Windows)
        try:
            popup.state('zoomed')  # Windows maximized state
        except:
            try:
                # Alternative for Linux
                popup.attributes('-zoomed', True)
            except:
                # Fallback: use full screen dimensions
                popup.geometry(f"{screen_width}x{screen_height}+0+0")
        
        popup.configure(bg='#f5f7fa')
        popup.transient(self.parent)
        popup.grab_set()
        
        # Use popup as parent for all widgets
        form_parent = popup
        
        # Create scrollable container with better background
        canvas = tk.Canvas(form_parent, bg='#f5f7fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f5f7fa')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling handler
        def on_mousewheel(event):
            # Windows uses delta, Linux uses num
            # Scroll by 3 units for smoother scrolling
            if event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-3, "units")
            elif event.num == 5 or event.delta < 0:
                canvas.yview_scroll(3, "units")
        
        # Bind mouse wheel events to canvas
        canvas.bind("<MouseWheel>", on_mousewheel)
        canvas.bind("<Button-4>", on_mousewheel)  # Linux
        canvas.bind("<Button-5>", on_mousewheel)  # Linux
        
        # Also bind to scrollable_frame
        scrollable_frame.bind("<MouseWheel>", on_mousewheel)
        scrollable_frame.bind("<Button-4>", on_mousewheel)  # Linux
        scrollable_frame.bind("<Button-5>", on_mousewheel)  # Linux
        
        # Bind to popup window so scrolling works anywhere in the form
        # This ensures scrolling works even when mouse is over child widgets
        def on_popup_mousewheel(event):
            # Only scroll if the event originated from within the popup
            on_mousewheel(event)
        
        popup.bind("<MouseWheel>", on_popup_mousewheel)
        popup.bind("<Button-4>", on_popup_mousewheel)  # Linux
        popup.bind("<Button-5>", on_popup_mousewheel)  # Linux
        
        # Use bind_all when popup has focus to catch all mousewheel events
        def on_popup_focus_in(event):
            popup.bind_all("<MouseWheel>", on_mousewheel)
            popup.bind_all("<Button-4>", on_mousewheel)  # Linux
            popup.bind_all("<Button-5>", on_mousewheel)  # Linux
        
        def on_popup_focus_out(event):
            popup.unbind_all("<MouseWheel>")
            popup.unbind_all("<Button-4>")
            popup.unbind_all("<Button-5>")
        
        popup.bind("<FocusIn>", on_popup_focus_in)
        popup.bind("<FocusOut>", on_popup_focus_out)
        
        # Set focus to popup initially
        popup.focus_set()
        
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
        
        # Mode indicator and title
        title_frame = tk.Frame(header_frame, bg='#1e40af')
        title_frame.pack(side=tk.LEFT, padx=25, pady=18)
        
        # Add mode indicator
        if view_only:
            mode_text = "📖 VIEW MODE (Read Only)"
            mode_color = '#ef4444'
        elif is_editing:
            mode_text = "✏️ EDIT MODE (Editable)"
            mode_color = '#10b981'
        else:
            mode_text = "➕ NEW PRESCRIPTION"
            mode_color = '#3b82f6'
        
        mode_label = tk.Label(
            title_frame,
            text=mode_text,
            font=('Segoe UI', 11, 'bold'),
            bg='#1e40af',
            fg=mode_color
        )
        mode_label.pack()
        
        title_text = f"Prescription ID: {prescription_id}"
        title_label = tk.Label(
            title_frame,
            text=title_text,
            font=('Segoe UI', 12, 'bold'),
            bg='#1e40af',
            fg='white'
        )
        title_label.pack()
        
        def back_to_list():
            """Close popup and return to prescription list"""
            popup.destroy()
            self.apply_filters()  # Refresh the list
        
        back_btn = tk.Button(
            header_frame,
            text="✕ Close",
            command=back_to_list,
            font=('Segoe UI', 10, 'bold'),
            bg='#6b7280',
            fg='white',
            padx=18,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#4b5563',
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
        
        # Status indicator frame (shows completion status)
        status_frame = tk.Frame(form_frame, bg='#ffffff', pady=5)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        status_label = tk.Label(
            status_frame,
            text="⚪ Required fields not completed",
            font=('Segoe UI', 9, 'bold'),
            bg='#ffffff',
            fg='#ef4444'
        )
        status_label.pack(side=tk.LEFT)
        
        def update_status():
            """Update status indicator"""
            patient_status = "✓" if selected_patient_id['value'] else "✗"
            doctor_status = "✓" if selected_doctor_id['value'] else "✗"
            med_status = "✓" if medicines else "✗"
            
            if selected_patient_id['value'] and selected_doctor_id['value'] and medicines:
                status_label.config(text="✅ All required fields completed", fg='#10b981')
            else:
                status_text = f"⚪ Patient: {patient_status} | Doctor: {doctor_status} | Medicines: {med_status}"
                status_label.config(text=status_text, fg='#f59e0b')
        
        # Patient selection with popup button
        patient_label_frame = tk.Frame(form_frame, bg='#ffffff')
        patient_label_frame.pack(fill=tk.X, pady=(0, 8))
        
        patient_title_frame = tk.Frame(patient_label_frame, bg='#ffffff')
        patient_title_frame.pack(fill=tk.X)
        
        tk.Label(patient_title_frame, text="Patient *", font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#374151').pack(side=tk.LEFT, anchor='w')
        
        # Show recent patients if editing same patient
        recent_patients_frame = tk.Frame(patient_label_frame, bg='#ffffff')
        recent_patients_frame.pack(fill=tk.X, pady=(5, 0))
        
        patient_frame = tk.Frame(form_frame, bg='#ffffff')
        patient_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Set entry state based on view_only
        entry_state = 'readonly' if view_only else 'readonly'  # Always readonly for display
        patient_var = tk.StringVar(value="Click to select patient..." if not view_only else "No patient selected")
        patient_display = tk.Entry(
            patient_frame,
            textvariable=patient_var,
            font=('Segoe UI', 10),
            state='readonly',
            relief=tk.SOLID,
            bd=1,
            readonlybackground='#f9fafb',
            fg='#6b7280'
        )
        patient_display.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 5))
        
        selected_patient_id = {'value': None}  # Use dict to allow modification in nested function
        
        def open_patient_selector():
            """Open patient selection popup"""
            patient_popup = tk.Toplevel(form_parent)
            patient_popup.title("Select Patient")
            patient_popup.geometry("800x600")
            patient_popup.configure(bg='#f5f7fa')
            patient_popup.transient(form_parent)
            patient_popup.grab_set()
            
            # Center the window
            patient_popup.update_idletasks()
            x = (patient_popup.winfo_screenwidth() // 2) - (800 // 2)
            y = (patient_popup.winfo_screenheight() // 2) - (600 // 2)
            patient_popup.geometry(f"800x600+{x}+{y}")
            
            # Header
            header_frame = tk.Frame(patient_popup, bg='#1e40af', height=60)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            tk.Label(
                header_frame,
                text="Select Patient",
                font=('Segoe UI', 14, 'bold'),
                bg='#1e40af',
                fg='white'
            ).pack(pady=18)
            
            # Search frame
            search_frame = tk.Frame(patient_popup, bg='#f5f7fa', padx=20, pady=15)
            search_frame.pack(fill=tk.X)
            
            tk.Label(
                search_frame,
                text="Search:",
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
            
            # Patient list
            list_frame = tk.Frame(patient_popup, bg='#f5f7fa', padx=20, pady=10)
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            columns = ('Patient ID', 'First Name', 'Last Name', 'Age', 'Gender', 'Phone')
            tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                if col == 'Patient ID':
                    tree.column(col, width=150)
                elif col in ['First Name', 'Last Name']:
                    tree.column(col, width=150)
                else:
                    tree.column(col, width=100)
            
            scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            def load_patients():
                """Load patients based on search"""
                tree.delete(*tree.get_children())
                search_text = search_var.get().strip().lower()
                
                try:
                    all_patients = self.db.get_all_patients()
                    for patient in all_patients:
                        if (not search_text or 
                            search_text in patient.get('patient_id', '').lower() or
                            search_text in patient.get('first_name', '').lower() or
                            search_text in patient.get('last_name', '').lower()):
                            tree.insert('', tk.END, values=(
                                patient.get('patient_id', ''),
                                patient.get('first_name', ''),
                                patient.get('last_name', ''),
                                patient.get('age', ''),
                                patient.get('gender', ''),
                                patient.get('phone', '')
                            ))
                except Exception as e:
                    print(f"Error loading patients: {e}")
            
            search_var.trace('w', lambda *args: load_patients())
            load_patients()  # Initial load
            
            # Button frame
            button_frame = tk.Frame(patient_popup, bg='#f5f7fa', padx=20, pady=15)
            button_frame.pack(fill=tk.X)
            
            def on_select():
                selection = tree.selection()
                if not selection:
                    messagebox.showwarning("Warning", "Please select a patient")
                    return
                
                item = tree.item(selection[0])
                patient_id = item['values'][0]
                patient_name = f"{item['values'][1]} {item['values'][2]}"
                display_text = f"{patient_id} - {patient_name}"
                
                selected_patient_id['value'] = patient_id
                patient_var.set(display_text)
                patient_display.config(fg='#1f2937')  # Change color to indicate selection
                patient_popup.destroy()
            
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
                command=patient_popup.destroy,
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
            
            search_entry.bind('<Return>', lambda e: on_select())
            patient_popup.bind('<Return>', lambda e: on_select())
        
        patient_btn = tk.Button(
            patient_frame,
            text="🔍 Select Patient",
            command=open_patient_selector if not view_only else lambda: None,
            font=('Segoe UI', 10, 'bold'),
            bg='#3b82f6',
            fg='white',
            padx=15,
            pady=8,
            cursor='hand2' if not view_only else 'arrow',
            relief=tk.FLAT,
            activebackground='#2563eb',
            state='normal' if not view_only else 'disabled'
        )
        patient_btn.pack(side=tk.LEFT)
        
        # Doctor selection with popup button
        doctor_label_frame = tk.Frame(form_frame, bg='#ffffff')
        doctor_label_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(doctor_label_frame, text="Doctor *", font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        
        doctor_frame = tk.Frame(form_frame, bg='#ffffff')
        doctor_frame.pack(fill=tk.X, pady=(0, 15))
        
        doctor_var = tk.StringVar(value="Click to select doctor..." if not view_only else "No doctor selected")
        doctor_display = tk.Entry(
            doctor_frame,
            textvariable=doctor_var,
            font=('Segoe UI', 10),
            state='readonly',
            relief=tk.SOLID,
            bd=1,
            readonlybackground='#f9fafb',
            fg='#6b7280'
        )
        doctor_display.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 5))
        
        selected_doctor_id = {'value': None}  # Use dict to allow modification in nested function
        
        def open_doctor_selector():
            """Open doctor selection popup"""
            doctor_popup = tk.Toplevel(form_parent)
            doctor_popup.title("Select Doctor")
            doctor_popup.geometry("900x600")
            doctor_popup.configure(bg='#f5f7fa')
            doctor_popup.transient(form_parent)
            doctor_popup.grab_set()
            
            # Center the window
            doctor_popup.update_idletasks()
            x = (doctor_popup.winfo_screenwidth() // 2) - (900 // 2)
            y = (doctor_popup.winfo_screenheight() // 2) - (600 // 2)
            doctor_popup.geometry(f"900x600+{x}+{y}")
            
            # Header
            header_frame = tk.Frame(doctor_popup, bg='#1e40af', height=60)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            tk.Label(
                header_frame,
                text="Select Doctor",
                font=('Segoe UI', 14, 'bold'),
                bg='#1e40af',
                fg='white'
            ).pack(pady=18)
            
            # Search frame
            search_frame = tk.Frame(doctor_popup, bg='#f5f7fa', padx=20, pady=15)
            search_frame.pack(fill=tk.X)
            
            tk.Label(
                search_frame,
                text="Search:",
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
            
            # Doctor list
            list_frame = tk.Frame(doctor_popup, bg='#f5f7fa', padx=20, pady=10)
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            columns = ('Doctor ID', 'First Name', 'Last Name', 'Specialization', 'Phone', 'Email')
            tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                if col == 'Doctor ID':
                    tree.column(col, width=150)
                elif col in ['First Name', 'Last Name']:
                    tree.column(col, width=150)
                elif col == 'Specialization':
                    tree.column(col, width=180)
                else:
                    tree.column(col, width=150)
            
            scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            def load_doctors():
                """Load doctors based on search"""
                tree.delete(*tree.get_children())
                search_text = search_var.get().strip().lower()
                
                try:
                    all_doctors = self.db.get_all_doctors()
                    for doctor in all_doctors:
                        if (not search_text or 
                            search_text in doctor.get('doctor_id', '').lower() or
                            search_text in doctor.get('first_name', '').lower() or
                            search_text in doctor.get('last_name', '').lower() or
                            search_text in doctor.get('specialization', '').lower()):
                            tree.insert('', tk.END, values=(
                                doctor.get('doctor_id', ''),
                                doctor.get('first_name', ''),
                                doctor.get('last_name', ''),
                                doctor.get('specialization', ''),
                                doctor.get('phone', ''),
                                doctor.get('email', '')
                            ))
                except Exception as e:
                    print(f"Error loading doctors: {e}")
            
            search_var.trace('w', lambda *args: load_doctors())
            load_doctors()  # Initial load
            
            # Button frame
            button_frame = tk.Frame(doctor_popup, bg='#f5f7fa', padx=20, pady=15)
            button_frame.pack(fill=tk.X)
            
            def on_select():
                selection = tree.selection()
                if not selection:
                    messagebox.showwarning("Warning", "Please select a doctor")
                    return
                
                item = tree.item(selection[0])
                doctor_id = item['values'][0]
                doctor_name = f"Dr. {item['values'][1]} {item['values'][2]}"
                specialization = item['values'][3]
                display_text = f"{doctor_id} - {doctor_name} ({specialization})"
                
                selected_doctor_id['value'] = doctor_id
                doctor_var.set(display_text)
                doctor_display.config(fg='#1f2937')  # Change color to indicate selection
                doctor_popup.destroy()
                update_status()  # Update status indicator
            
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
                command=doctor_popup.destroy,
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
            
            search_entry.bind('<Return>', lambda e: on_select())
            doctor_popup.bind('<Return>', lambda e: on_select())
        
        doctor_btn = tk.Button(
            doctor_frame,
            text="🔍 Select Doctor",
            command=open_doctor_selector if not view_only else lambda: None,
            font=('Segoe UI', 10, 'bold'),
            bg='#3b82f6',
            fg='white',
            padx=15,
            pady=8,
            cursor='hand2' if not view_only else 'arrow',
            relief=tk.FLAT,
            activebackground='#2563eb',
            state='normal' if not view_only else 'disabled'
        )
        doctor_btn.pack(side=tk.LEFT)
        
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
        
        # Set entry state based on view_only
        entry_state = 'readonly' if view_only else 'normal'
        date_entry = tk.Entry(date_input_frame, font=('Segoe UI', 10), relief=tk.SOLID, bd=1, state=entry_state)
        date_entry.insert(0, get_current_date())
        date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 5))
        
        def open_calendar():
            """Open calendar date picker"""
            calendar_window = tk.Toplevel(form_parent)
            calendar_window.title("Select Date")
            calendar_window.geometry("300x280")
            calendar_window.configure(bg='#ffffff')
            calendar_window.transient(form_parent)
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
            command=open_calendar if not view_only else lambda: None,
            font=('Segoe UI', 12),
            bg='#3b82f6',
            fg='white',
            width=3,
            relief=tk.FLAT,
            cursor='hand2' if not view_only else 'arrow',
            activebackground='#2563eb',
            state='normal' if not view_only else 'disabled'
        )
        calendar_btn.pack(side=tk.LEFT)
        
        # Diagnosis with templates
        diagnosis_label_frame = tk.Frame(form_frame, bg='#ffffff')
        diagnosis_label_frame.pack(fill=tk.X, pady=(0, 8))
        
        diagnosis_title_frame = tk.Frame(diagnosis_label_frame, bg='#ffffff')
        diagnosis_title_frame.pack(fill=tk.X)
        
        tk.Label(diagnosis_title_frame, text="Diagnosis", font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#374151').pack(side=tk.LEFT, anchor='w')
        
        # Common diagnosis templates
        common_diagnoses = [
            "Acute Upper Respiratory Tract Infection",
            "Hypertension",
            "Type 2 Diabetes Mellitus",
            "Acute Gastroenteritis",
            "Urinary Tract Infection",
            "Acute Bronchitis",
            "Migraine",
            "Dermatitis",
            "Arthritis",
            "Anxiety Disorder"
        ]
        
        def insert_diagnosis_template(diag):
            """Insert diagnosis template"""
            current = diagnosis_text.get('1.0', tk.END).strip()
            if current:
                diagnosis_text.insert('1.0', f"{diag}\n")
            else:
                diagnosis_text.insert('1.0', diag)
            diagnosis_text.focus_set()
        
        template_frame = tk.Frame(diagnosis_label_frame, bg='#f0f9ff', relief=tk.SUNKEN, bd=1)
        template_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Label(
            template_frame,
            text="Quick templates:",
            font=('Segoe UI', 8),
            bg='#f0f9ff',
            fg='#6b7280'
        ).pack(side=tk.LEFT, padx=5, pady=3)
        
        for diag in common_diagnoses[:6]:  # Show first 6
            btn = tk.Button(
                template_frame,
                text=diag[:25] + "..." if len(diag) > 25 else diag,
                command=lambda d=diag: insert_diagnosis_template(d),
                font=('Segoe UI', 7),
                bg='#dbeafe',
                fg='#1e40af',
                padx=8,
                pady=2,
                relief=tk.FLAT,
                cursor='hand2',
                activebackground='#bfdbfe'
            )
            btn.pack(side=tk.LEFT, padx=2, pady=3)
        
        diagnosis_text = tk.Text(form_frame, font=('Segoe UI', 10), height=4, wrap=tk.WORD, relief=tk.SOLID, bd=1, padx=5, pady=5, state='normal' if not view_only else 'disabled')
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
        notes_text = tk.Text(notes_frame, font=('Segoe UI', 10), height=12, wrap=tk.WORD, relief=tk.SOLID, bd=1, padx=5, pady=5, state='normal' if not view_only else 'disabled')
        notes_text.pack(fill=tk.BOTH, expand=True)
        
        # Populate form fields if editing
        if is_editing and prescription_data:
            # Set patient
            patient_id_to_find = prescription_data.get('patient_id')
            if patient_id_to_find:
                patient = self.db.get_patient_by_id(patient_id_to_find)
                if patient:
                    display_text = f"{patient_id_to_find} - {patient.get('first_name', '')} {patient.get('last_name', '')}"
                    patient_var.set(display_text)
                    selected_patient_id['value'] = patient_id_to_find
                    patient_display.config(fg='#1f2937')
            
            # Set doctor
            doctor_id_to_find = prescription_data.get('doctor_id')
            if doctor_id_to_find:
                doctor = self.db.get_doctor_by_id(doctor_id_to_find)
                if doctor:
                    display_text = f"{doctor_id_to_find} - Dr. {doctor.get('first_name', '')} {doctor.get('last_name', '')} ({doctor.get('specialization', '')})"
                    doctor_var.set(display_text)
                    selected_doctor_id['value'] = doctor_id_to_find
                    doctor_display.config(fg='#1f2937')
            
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
            # Update status indicator
            update_status()
        
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
            bd=1,
            state=entry_state
        )
        med_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=4)
        
        def open_medicine_selector():
            """Open full window medicine selector"""
            medicine_window = tk.Toplevel(form_parent)
            medicine_window.title("Select Medicine")
            medicine_window.geometry("1200x700")
            medicine_window.configure(bg='#f0f0f0')
            medicine_window.transient(form_parent)
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
            command=open_medicine_selector if not view_only else lambda: None,
            font=('Segoe UI', 9, 'bold'),
            bg='#6366f1',
            fg='white',
            padx=12,
            pady=4,
            cursor='hand2' if not view_only else 'arrow',
            relief=tk.FLAT,
            activebackground='#4f46e5',
            activeforeground='white',
            state='normal' if not view_only else 'disabled'
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
        
        # Common prescription presets
        presets_frame = tk.Frame(add_med_frame, bg='#ffffff')
        presets_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            presets_frame,
            text="💊 Quick Presets:",
            font=('Segoe UI', 8, 'bold'),
            bg='#ffffff',
            fg='#6b7280'
        ).pack(side=tk.LEFT, padx=(0, 5), pady=3)
        
        common_presets = [
            ("Paracetamol", "500mg", "BD", "5 days", "After meals"),
            ("Ibuprofen", "400mg", "TDS", "3 days", "With food"),
            ("Amoxicillin", "500mg", "TDS", "7 days", "After meals"),
            ("Azithromycin", "500mg", "OD", "3 days", "1 hour before food"),
            ("Omeprazole", "20mg", "OD", "14 days", "Before breakfast"),
            ("Cetirizine", "10mg", "OD", "5 days", "At bedtime")
        ]
        
        def apply_preset(med, dose, freq, dur, inst):
            """Apply preset values"""
            med_name_var.set(med)
            dosage_var.set(dose)
            frequency_var.set(freq)
            duration_var.set(dur)
            instructions_var.set(inst)
        
        for med, dose, freq, dur, inst in common_presets:
            btn = tk.Button(
                presets_frame,
                text=f"{med} ({dose})",
                command=lambda m=med, d=dose, f=freq, dur=dur, i=inst: apply_preset(m, d, f, dur, i),
                font=('Segoe UI', 7),
                bg='#ecfdf5',
                fg='#065f46',
                padx=6,
                pady=2,
                relief=tk.FLAT,
                cursor='hand2',
                activebackground='#d1fae5'
            )
            btn.pack(side=tk.LEFT, padx=2, pady=3)
        
        # Set combo state based on view_only
        combo_state = 'readonly' if view_only else 'normal'
        
        dosage_var = tk.StringVar()
        dosage_combo = ttk.Combobox(
            details_frame, 
            textvariable=dosage_var, 
            values=dosage_options, 
            font=('Segoe UI', 9), 
            width=20, 
            state=combo_state
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
        # Set combo state based on view_only
        combo_state = 'readonly' if view_only else 'normal'
        frequency_combo = ttk.Combobox(
            details_frame, 
            textvariable=frequency_var, 
            values=frequency_options, 
            font=('Segoe UI', 9), 
            width=20, 
            state=combo_state
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
            state=combo_state
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
        
        instructions_var = tk.StringVar()
        instructions_entry = tk.Entry(
            details_frame,
            textvariable=instructions_var,
            font=('Segoe UI', 9), 
            width=20,
            relief=tk.SOLID,
            bd=1,
            state=entry_state
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
            
            # Update status indicator
            update_status()
            
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
            command=add_medicine if not view_only else lambda: None,
            font=('Segoe UI', 10, 'bold'),
            bg='#3b82f6',
            fg='white',
            padx=25,
            pady=10,
            cursor='hand2' if not view_only else 'arrow',
            relief=tk.FLAT,
            activebackground='#2563eb',
            activeforeground='white',
            state='normal' if not view_only else 'disabled'
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
        
        # Keyboard shortcuts help
        shortcuts_frame = tk.Frame(main_frame, bg='#f0f9ff', relief=tk.SUNKEN, bd=1)
        shortcuts_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        shortcuts_text = "⌨️ Keyboard Shortcuts: F1=Select Patient | F2=Select Doctor | F3=Add Medicine | Ctrl+S=Save | Ctrl+P=Print | Esc=Close"
        shortcuts_label = tk.Label(
            shortcuts_frame,
            text=shortcuts_text,
            font=('Segoe UI', 8),
            bg='#f0f9ff',
            fg='#1e40af',
            anchor='w',
            justify=tk.LEFT
        )
        shortcuts_label.pack(padx=10, pady=5)
        
        # Bind keyboard shortcuts
        def on_f1(event=None):
            open_patient_selector()
        
        def on_f2(event=None):
            open_doctor_selector()
        
        def on_f3(event=None):
            med_name_entry.focus_set()
        
        def on_ctrl_s(event=None):
            save_prescription()
        
        def on_ctrl_p(event=None):
            print_prescription()
        
        form_parent.bind('<F1>', on_f1)
        form_parent.bind('<F2>', on_f2)
        form_parent.bind('<F3>', on_f3)
        form_parent.bind('<Control-s>', on_ctrl_s)
        form_parent.bind('<Control-p>', on_ctrl_p)
        form_parent.bind('<Escape>', lambda e: back_to_list())
        
        # Save and Cancel buttons at bottom - improved styling
        button_frame = tk.Frame(main_frame, bg='#f8f9fa', relief=tk.RAISED, bd=1)
        button_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        inner_button_frame = tk.Frame(button_frame, bg='#f8f9fa')
        inner_button_frame.pack(padx=20, pady=15)
        
        def save_prescription():
            # Get selected patient ID
            patient_id = selected_patient_id['value']
            if not patient_id:
                messagebox.showerror("Validation Error", "Please select a patient using the 'Select Patient' button.")
                patient_btn.focus_set()
                return
            
            # Get selected doctor ID
            doctor_id = selected_doctor_id['value']
            if not doctor_id:
                messagebox.showerror("Validation Error", "Please select a doctor using the 'Select Doctor' button.")
                doctor_btn.focus_set()
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
                else:
                    messagebox.showerror("Error", "Failed to update prescription")
            else:
                # Create new prescription
                data['prescription_id'] = prescription_id
                if self.db.add_prescription(data, medicines):
                    messagebox.showinfo("Success", "Prescription created successfully")
                    back_to_list()
                else:
                    messagebox.showerror("Error", "Failed to create prescription")
        
        def print_prescription():
            """Generate and print professional prescription PDF"""
            # Get selected patient ID
            patient_id = selected_patient_id['value']
            if not patient_id:
                messagebox.showwarning("Warning", "Please select a patient to print prescription")
                return
            
            # Get selected doctor ID
            doctor_id = selected_doctor_id['value']
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
        
        # Only show save button if not in view_only mode
        if not view_only:
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
        
        # Print button - always show (can print even in view mode)
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
        form_parent.after(100, lambda: patient_btn.focus_set())
        
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

