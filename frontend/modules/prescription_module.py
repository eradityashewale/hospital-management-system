"""
Prescription Management Module
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime

# Backend imports
from backend.database import Database

# Frontend theme
from frontend.theme import (
    BG_BASE, BG_CARD, BG_DEEP, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_BLUE, BORDER_DEFAULT, TABLE_HEADER_BG, BTN_SUCCESS_BG, BTN_SUCCESS_HOVER,
    BTN_PRIMARY_BG, BTN_PRIMARY_HOVER, BTN_DANGER_BG, BTN_DANGER_HOVER,
    BTN_SECONDARY_BG, BTN_SECONDARY_HOVER, WARNING, FONT_UI,
    get_theme,
)

# Utils imports
from utils.helpers import generate_id, get_current_date


class AnimationHelper:
    """Helper class for smooth Framer-like animations in Tkinter"""
    
    @staticmethod
    def fade_in_window(window, duration=300, steps=30):
        """Fade in a window smoothly"""
        try:
            # Start with transparent (alpha = 0.0)
            window.attributes('-alpha', 0.0)
            window.update()
            
            step = 1.0 / steps
            delay = duration // steps
            current_alpha = 0.0
            
            def animate():
                nonlocal current_alpha
                current_alpha += step
                if current_alpha >= 1.0:
                    window.attributes('-alpha', 1.0)
                else:
                    window.attributes('-alpha', current_alpha)
                    window.after(delay, animate)
            
            animate()
        except:
            # Fallback if alpha not supported
            window.attributes('-alpha', 1.0)
    
    @staticmethod
    def slide_in_widget(widget, direction='left', distance=50, duration=400, steps=40):
        """Slide in a widget from a direction"""
        original_x = widget.winfo_x()
        original_y = widget.winfo_y()
        
        # Hide widget initially
        widget.place_forget()
        widget.update()
        
        # Calculate start position
        if direction == 'left':
            start_x = original_x - distance
            start_y = original_y
        elif direction == 'right':
            start_x = original_x + distance
            start_y = original_y
        elif direction == 'top':
            start_x = original_x
            start_y = original_y - distance
        elif direction == 'bottom':
            start_x = original_x
            start_y = original_y + distance
        else:
            start_x = original_x
            start_y = original_y
        
        # Place at start position
        widget.place(x=start_x, y=start_y)
        widget.update()
        
        # Animate
        step_x = (original_x - start_x) / steps
        step_y = (original_y - start_y) / steps
        delay = duration // steps
        current_step = 0
        
        def animate():
            nonlocal current_step
            current_step += 1
            new_x = start_x + (step_x * current_step)
            new_y = start_y + (step_y * current_step)
            
            if current_step >= steps:
                widget.place(x=original_x, y=original_y)
            else:
                widget.place(x=new_x, y=new_y)
                widget.after(delay, animate)
        
        animate()
    
    @staticmethod
    def fade_in_widget(widget, duration=300, steps=30):
        """Fade in a widget by changing its background color"""
        try:
            original_bg = widget.cget('bg')
            # Get RGB values
            if original_bg.startswith('#'):
                r = int(original_bg[1:3], 16)
                g = int(original_bg[3:5], 16)
                b = int(original_bg[5:7], 16)
            else:
                # Default to white if can't parse
                r, g, b = 255, 255, 255
            
            # Start with lighter version
            start_r, start_g, start_b = 255, 255, 255
            step_r = (r - start_r) / steps
            step_g = (g - start_g) / steps
            step_b = (b - start_b) / steps
            delay = duration // steps
            current_step = 0
            
            def animate():
                nonlocal current_step
                current_step += 1
                new_r = int(start_r + (step_r * current_step))
                new_g = int(start_g + (step_g * current_step))
                new_b = int(start_b + (step_b * current_step))
                
                # Clamp values
                new_r = max(0, min(255, new_r))
                new_g = max(0, min(255, new_g))
                new_b = max(0, min(255, new_b))
                
                new_color = f"#{new_r:02x}{new_g:02x}{new_b:02x}"
                widget.config(bg=new_color)
                
                if current_step < steps:
                    widget.after(delay, animate)
            
            widget.config(bg=f"#{start_r:02x}{start_g:02x}{start_b:02x}")
            animate()
        except:
            pass
    
    @staticmethod
    def scale_button(button, scale_factor=1.05, duration=150):
        """Scale a button on hover with smooth animation"""
        original_font = button.cget('font')
        original_padx = button.cget('padx') if hasattr(button, 'cget') else 0
        original_pady = button.cget('pady') if hasattr(button, 'cget') else 0
        
        # Parse font
        try:
            font_parts = original_font.split()
            font_size = int(font_parts[-1]) if font_parts[-1].isdigit() else 10
            new_size = int(font_size * scale_factor)
            new_font = ' '.join(font_parts[:-1] + [str(new_size)])
        except:
            new_font = original_font
        
        new_padx = int(original_padx * scale_factor) if isinstance(original_padx, (int, float)) else original_padx
        new_pady = int(original_pady * scale_factor) if isinstance(original_pady, (int, float)) else original_pady
        
        steps = 10
        delay = duration // steps
        current_step = 0
        
        def animate():
            nonlocal current_step
            current_step += 1
            progress = current_step / steps
            
            # Interpolate
            current_size = font_size + (new_size - font_size) * progress
            current_padx = original_padx + (new_padx - original_padx) * progress
            current_pady = original_pady + (new_pady - original_pady) * progress
            
            try:
                button.config(font=' '.join(font_parts[:-1] + [str(int(current_size))]))
                if isinstance(current_padx, (int, float)):
                    button.config(padx=int(current_padx))
                if isinstance(current_pady, (int, float)):
                    button.config(pady=int(current_pady))
            except:
                pass
            
            if current_step < steps:
                button.after(delay, animate)
        
        animate()
    
    @staticmethod
    def pulse_widget(widget, color1, color2, duration=1000, steps=20):
        """Pulse a widget's color between two colors"""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"
        
        try:
            rgb1 = hex_to_rgb(color1)
            rgb2 = hex_to_rgb(color2)
            
            delay = duration // steps
            current_step = 0
            forward = True
            
            def animate():
                nonlocal current_step, forward
                if forward:
                    current_step += 1
                    if current_step >= steps:
                        forward = False
                else:
                    current_step -= 1
                    if current_step <= 0:
                        forward = True
                
                # Interpolate
                progress = current_step / steps
                r = rgb1[0] + (rgb2[0] - rgb1[0]) * progress
                g = rgb1[1] + (rgb2[1] - rgb1[1]) * progress
                b = rgb1[2] + (rgb2[2] - rgb1[2]) * progress
                
                new_color = rgb_to_hex((r, g, b))
                widget.config(bg=new_color)
                
                widget.after(delay, animate)
            
            animate()
        except:
            pass
    
    @staticmethod
    def animate_color_transition(widget, start_color, end_color, duration=300, steps=30):
        """Smoothly transition a widget's color"""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"
        
        try:
            rgb1 = hex_to_rgb(start_color)
            rgb2 = hex_to_rgb(end_color)
            
            delay = duration // steps
            current_step = 0
            
            def animate():
                nonlocal current_step
                current_step += 1
                progress = current_step / steps
                
                r = rgb1[0] + (rgb2[0] - rgb1[0]) * progress
                g = rgb1[1] + (rgb2[1] - rgb1[1]) * progress
                b = rgb1[2] + (rgb2[2] - rgb1[2]) * progress
                
                new_color = rgb_to_hex((r, g, b))
                widget.config(bg=new_color)
                
                if current_step < steps:
                    widget.after(delay, animate)
            
            animate()
        except:
            widget.config(bg=end_color)


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
        t = get_theme()
        # Header with modern styling (theme-aware)
        header = tk.Label(
            self.parent,
            text="Prescription Management",
            font=(FONT_UI, 24, 'bold'),
            bg=t["BG_DEEP"],
            fg=t["TEXT_PRIMARY"]
        )
        header.pack(pady=20)
        
        # Selection indicator frame - shows selected prescription
        self.selection_indicator_frame = tk.Frame(self.parent, bg=t["BG_BASE"], relief=tk.FLAT, bd=0)
        self.selection_indicator_frame.pack(fill=tk.X, padx=25, pady=(0, 10))
        self.selection_indicator_frame.pack_forget()  # Initially hidden
        
        self.selection_label = tk.Label(
            self.selection_indicator_frame,
            text="",
            font=(FONT_UI, 11, 'bold'),
            bg=t["BG_BASE"],
            fg=t["ACCENT_BLUE"],
            padx=15,
            pady=10
        )
        self.selection_label.pack(side=tk.LEFT, padx=10)
        
        # Top frame
        top_frame = tk.Frame(self.parent, bg=t["BG_DEEP"])
        top_frame.pack(fill=tk.X, padx=25, pady=15)
        
        # Filter frame
        filter_frame = tk.Frame(top_frame, bg=t["BG_DEEP"])
        filter_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Search by patient name
        tk.Label(filter_frame, text="Search by Patient Name:", font=(FONT_UI, 11, 'bold'), bg=t["BG_DEEP"], fg=t["TEXT_SECONDARY"]).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.apply_filters())
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var, font=(FONT_UI, 10), width=20, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground=t["BORDER_DEFAULT"], highlightcolor=t["ACCENT_BLUE"], bg=t["BG_CARD"], fg=t["TEXT_PRIMARY"], insertbackground=t["TEXT_PRIMARY"])
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Date filter with calendar button
        tk.Label(filter_frame, text="Filter by Date:", font=(FONT_UI, 11, 'bold'), bg=t["BG_DEEP"], fg=t["TEXT_SECONDARY"]).pack(side=tk.LEFT, padx=(15, 5))
        date_filter_frame = tk.Frame(filter_frame, bg=t["BG_DEEP"])
        date_filter_frame.pack(side=tk.LEFT, padx=5)
        self.date_var = tk.StringVar(value="")
        date_entry = tk.Entry(date_filter_frame, textvariable=self.date_var, font=(FONT_UI, 10), width=15, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground=t["BORDER_DEFAULT"], highlightcolor=t["ACCENT_BLUE"], bg=t["BG_CARD"], fg=t["TEXT_PRIMARY"], insertbackground=t["TEXT_PRIMARY"])
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
                font=(FONT_UI, 12, 'bold'),
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
                        font=(FONT_UI, 9, 'bold'),
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
                        font=(FONT_UI, 9),
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
                font=(FONT_UI, 10, 'bold'),
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
                font=(FONT_UI, 11, 'bold'),
                bg='#ffffff',
                fg='#1a237e'
            )
            month_label.pack(side=tk.LEFT, expand=True)
            
            next_btn = tk.Button(
                nav_frame,
                text="▶",
                command=next_month,
                font=(FONT_UI, 10, 'bold'),
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
                font=(FONT_UI, 9),
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
                font=(FONT_UI, 9),
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
            font=(FONT_UI, 12),
            bg=ACCENT_BLUE,
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
            font=(FONT_UI, 11, 'bold'),
            bg=BTN_SUCCESS_BG,
            fg='white',
            padx=25,
            pady=10,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground=BTN_SUCCESS_HOVER,
            activeforeground='white'
        )
        add_btn.pack(side=tk.RIGHT, padx=10)
        
        # Action buttons - Doctor-friendly popup-based actions (BEFORE list so they're visible)
        action_frame = tk.Frame(self.parent, bg=t["BG_DEEP"])
        action_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Button labels for doctors
        tk.Label(
            action_frame,
            text="Quick Actions:",
            font=(FONT_UI, 11, 'bold'),
            bg=t["BG_DEEP"],
            fg=t["TEXT_SECONDARY"]
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Button(
            action_frame,
            text="View Details",
            command=self.view_prescription,
            font=(FONT_UI, 10, 'bold'),
            bg=BTN_PRIMARY_BG,
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground=BTN_PRIMARY_HOVER,
            activeforeground='white'
        ).pack(side=tk.LEFT, padx=6)
        
        tk.Button(
            action_frame,
            text="✏️ Edit Prescription",
            command=self.edit_prescription,
            font=(FONT_UI, 10, 'bold'),
            bg=WARNING,
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
            font=(FONT_UI, 10, 'bold'),
            bg=BTN_DANGER_BG,
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground=BTN_DANGER_HOVER,
            activeforeground='white'
        ).pack(side=tk.LEFT, padx=6)
        
        # List frame (AFTER action buttons)
        list_frame = tk.Frame(self.parent, bg=t["BG_DEEP"])
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
                       font=(FONT_UI, 10), 
                       rowheight=30, 
                       background=t["BG_CARD"], 
                       foreground=t["TEXT_PRIMARY"],
                       fieldbackground=t["BG_CARD"])
        style.configure("Treeview.Heading", 
                       font=(FONT_UI, 11, 'bold'), 
                       background=t["TABLE_HEADER_BG"], 
                       foreground=t["TEXT_PRIMARY"],
                       relief='flat')
        style.map("Treeview.Heading", 
                 background=[('active', t["ACCENT_BLUE"]), ('pressed', t["ACCENT_BLUE"])])
        style.map("Treeview",
                 background=[('selected', t["ACCENT_BLUE"])],
                 foreground=[('selected', 'white')])
        
        # Create treeview AFTER style is configured
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Style scrollbars to match theme
        style.configure("Vertical.TScrollbar", 
                       background=t["TEXT_MUTED"],
                       troughcolor=t["BG_BASE"],
                       borderwidth=0,
                       arrowcolor=t["ACCENT_BLUE"],
                       darkcolor=t["TEXT_MUTED"],
                       lightcolor=t["TEXT_MUTED"])
        style.map("Vertical.TScrollbar",
                 background=[('active', t["TEXT_SECONDARY"])],
                 arrowcolor=[('active', t["ACCENT_BLUE"])])
        
        style.configure("Horizontal.TScrollbar",
                       background=t["TEXT_MUTED"],
                       troughcolor=t["BG_BASE"],
                       borderwidth=1,
                       arrowcolor=t["ACCENT_BLUE"],
                       darkcolor=t["TEXT_MUTED"],
                       lightcolor=t["TEXT_MUTED"],
                       relief=tk.FLAT)
        style.map("Horizontal.TScrollbar",
                 background=[('active', t["TEXT_SECONDARY"]), ('pressed', t["BORDER_DEFAULT"])],
                 arrowcolor=[('active', t["ACCENT_BLUE"])])
        
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
            self.tree.column(col, width=width, minwidth=minwidth, stretch=True, anchor='center')
        
        # Add both vertical and horizontal scrollbars with theme styling
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview, style="Vertical.TScrollbar")
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview, style="Horizontal.TScrollbar")
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Use pack layout - pack horizontal scrollbar first at bottom, then treeview and vertical scrollbar
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Pack treeview and vertical scrollbar side by side
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to view prescription details
        self.tree.bind('<Double-1>', self.view_prescription)
        
        # Bind selection event to update indicator
        def on_selection_change(event=None):
            """Update selection indicator when prescription is selected"""
            selection = self.tree.selection()
            if selection:
                item = self.tree.item(selection[0])
                values = item['values']
                if values:
                    prescription_id = values[0]
                    patient_name = values[2] if len(values) > 2 else 'Unknown'
                    doctor_name = values[3] if len(values) > 3 else 'Unknown'
                    date = values[4] if len(values) > 4 else ''
                    
                    indicator_text = f"📋 Selected: {prescription_id} | Patient: {patient_name} | Doctor: {doctor_name}"
                    if date:
                        indicator_text += f" | Date: {date}"
                    
                    self.selection_label.config(text=indicator_text)
                    # Show indicator frame
                    if not self.selection_indicator_frame.winfo_viewable():
                        self.selection_indicator_frame.pack(fill=tk.X, padx=25, pady=(0, 10))
            else:
                self.selection_indicator_frame.pack_forget()
        
        self.tree.bind('<<TreeviewSelect>>', on_selection_change)
    
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
            font=(FONT_UI, 14, 'bold'),
            bg='#1e40af',
            fg='white'
        ).pack(pady=18)
        
        # Search frame
        search_frame = tk.Frame(popup, bg='#f5f7fa', padx=20, pady=15)
        search_frame.pack(fill=tk.X)
        
        tk.Label(
            search_frame,
            text="Search by Patient Name or Date:",
            font=(FONT_UI, 10, 'bold'),
            bg='#f5f7fa',
            fg='#374151'
        ).pack(side=tk.LEFT, padx=5)
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=search_var,
            font=(FONT_UI, 10),
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
                tree.column(col, width=150, anchor='center')
            elif col == 'Patient ID':
                tree.column(col, width=120, anchor='center')
            elif col == 'Patient Name':
                tree.column(col, width=180, anchor='center')
            elif col == 'Doctor':
                tree.column(col, width=200, anchor='center')
            elif col == 'Date':
                tree.column(col, width=120, anchor='center')
            else:
                tree.column(col, width=200, anchor='center')
        
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
            font=(FONT_UI, 10, 'bold'),
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
            font=(FONT_UI, 10),
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
        popup.configure(bg='#f5f7fa')
        popup.transient(self.parent)
        popup.grab_set()
        
        # Header
        header_frame = tk.Frame(popup, bg='#1e40af', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text=f"Prescription Details - {prescription_id}",
            font=(FONT_UI, 14, 'bold'),
            bg='#1e40af',
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=25, pady=18)
        
        # Edit button
        def open_edit():
            popup.destroy()
            self.show_prescription_form_popup(prescription_id=prescription_id, view_only=False)
        
        edit_btn = tk.Button(
            header_frame,
            text="✏️ Edit",
            command=open_edit,
            font=(FONT_UI, 10, 'bold'),
            bg='#10b981',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#059669',
            activeforeground='white'
        )
        edit_btn.pack(side=tk.RIGHT, padx=(0, 10), pady=12)
        
        # Print button
        def print_prescription():
            """Print/Export prescription as PDF"""
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.units import mm
                from reportlab.lib import colors
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.enums import TA_LEFT, TA_CENTER
                from tkinter import filedialog
                from datetime import datetime
                import os
                import platform
                import subprocess
                
                # Get patient and doctor details
                patient = self.db.get_patient_by_id(prescription_data.get('patient_id'))
                doctor = self.db.get_doctor_by_id(prescription_data.get('doctor_id'))
                
                if not patient or not doctor:
                    messagebox.showerror("Error", "Could not retrieve patient or doctor information")
                    return
                
                # Ask user where to save PDF
                prescription_date = prescription_data.get('prescription_date', '')
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
                
                elements = []
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
                    fontSize=10,
                    textColor=colors.HexColor('#1a237e'),
                    spaceAfter=2,
                    spaceBefore=4,
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
                
                # Header
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
                
                # Format date
                try:
                    date_obj = datetime.strptime(prescription_date, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%d.%m.%Y')
                except:
                    formatted_date = prescription_date
                
                # Header table
                header_data = [[
                    Paragraph(f"<b>{doctor_name}</b><br/>"
                             f"{doctor_qual}<br/>"
                             f"Specialization: {doctor_spec}<br/>"
                             f"Mobile: {doctor.get('phone', 'N/A')}<br/>"
                             f"Email: {doctor.get('email', 'N/A')}", normal_style),
                    Paragraph(f"<b>PRESCRIPTION</b><br/>"
                             f"Date: {formatted_date}<br/>"
                             f"Prescription ID: {prescription_id}", normal_style)
                ]]
                
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
                elements.append(Spacer(1, 4*mm))
                
                # Patient Information (compact single line)
                age_gender = f"{patient_age}/{patient_gender}" if patient_age else patient_gender
                extra = []
                if patient.get('phone'):
                    extra.append(patient.get('phone'))
                if patient.get('address'):
                    addr = str(patient.get('address') or '')
                    extra.append(addr[:40] + ('...' if len(addr) > 40 else ''))
                pt_text = f"<b>Patient:</b> {patient_name}  |  {age_gender}  |  ID: {prescription_data.get('patient_id')}"
                if extra:
                    pt_text += f"  |  {' | '.join(extra)}"
                compact_style = ParagraphStyle('Compact', parent=styles['Normal'], fontSize=9, spaceAfter=2, spaceBefore=0)
                elements.append(Paragraph(pt_text, compact_style))
                elements.append(Spacer(1, 3*mm))
                
                # Vital Signs
                weight = prescription_data.get('weight', '')
                spo2 = prescription_data.get('spo2', '')
                hr = prescription_data.get('hr', '')
                rr = prescription_data.get('rr', '')
                bp = prescription_data.get('bp', '')
                height = prescription_data.get('height', '')
                ideal_body_weight = prescription_data.get('ideal_body_weight', '')
                follow_up_date = prescription_data.get('follow_up_date', '')
                
                if weight or spo2 or hr or rr or bp or height or ideal_body_weight or follow_up_date:
                    v_parts = []
                    if weight:
                        v_parts.append(f"Wt:{weight}kg")
                    if height:
                        v_parts.append(f"Ht:{height}m")
                    if bp:
                        v_parts.append(f"BP:{bp}")
                    if hr:
                        v_parts.append(f"HR:{hr}")
                    if spo2:
                        v_parts.append(f"SPO2:{spo2}%")
                    if rr:
                        v_parts.append(f"RR:{rr}")
                    if ideal_body_weight:
                        v_parts.append(f"IBW:{ideal_body_weight}kg")
                    if follow_up_date:
                        v_parts.append(f"FUP:{follow_up_date}")
                    if v_parts:
                        vitals_para = Paragraph(f"<b>Vitals:</b> {' | '.join(v_parts)}", compact_style)
                        elements.append(vitals_para)
                        elements.append(Spacer(1, 3*mm))
                
                # Diagnosis
                diagnosis = prescription_data.get('diagnosis', '')
                icd_codes = prescription_data.get('icd_codes', '')
                if diagnosis or icd_codes:
                    elements.append(Paragraph("<b>DIAGNOSIS</b>", heading_style))
                    if diagnosis:
                        elements.append(Paragraph(diagnosis.replace('\n', '<br/>'), normal_style))
                    if icd_codes:
                        elements.append(Paragraph(f"<b>ICD Codes:</b> {icd_codes}", normal_style))
                    elements.append(Spacer(1, 3*mm))
                
                # Medicines
                if items:
                    elements.append(Paragraph("<b>PRESCRIBED MEDICINES</b>", heading_style))
                    med_data = [['R', 'Medicine Name', 'Type', 'Dosage', 'Frequency', 'Duration', 'Instructions']]
                    for idx, item in enumerate(items, 1):
                        med_data.append([
                            str(idx),
                            item.get('medicine_name', ''),
                            item.get('medicine_type', ''),
                            item.get('dosage', ''),
                            item.get('frequency', ''),
                            item.get('duration', ''),
                            item.get('instructions', '')
                        ])
                    
                    med_table = Table(med_data, colWidths=[8*mm, 40*mm, 20*mm, 22*mm, 25*mm, 22*mm, 43*mm])
                    med_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                        ('ALIGN', (6, 1), (6, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
                    ]))
                    elements.append(med_table)
                    elements.append(Spacer(1, 4*mm))
                
                # Notes
                notes = prescription_data.get('notes', '')
                if notes:
                    elements.append(Paragraph("<b>DOCTOR'S NOTES</b>", heading_style))
                    elements.append(Paragraph(notes.replace('\n', '<br/>'), normal_style))
                    elements.append(Spacer(1, 8*mm))
                
                # Footer
                footer_data = [['Signature: _________________________', f'Date: {formatted_date}']]
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
                messagebox.showinfo("Success", f"Prescription PDF saved successfully!\n\n{filename}")
                
                # Ask if user wants to open the PDF
                if messagebox.askyesno("Open PDF", "Do you want to open the PDF now?"):
                    system = platform.system()
                    if system == "Windows":
                        os.startfile(filename)
                    elif system == "Darwin":  # macOS
                        subprocess.run(['open', filename])
                    else:  # Linux
                        subprocess.run(['xdg-open', filename])
                        
            except ImportError:
                messagebox.showerror("Error", 
                    "reportlab library is not installed.\n\n"
                    "Please install it using: pip install reportlab")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")
        
        print_btn = tk.Button(
            header_frame,
            text="🖨️ Print",
            command=print_prescription,
            font=(FONT_UI, 10, 'bold'),
            bg='#6366f1',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#4f46e5',
            activeforeground='white'
        )
        print_btn.pack(side=tk.RIGHT, padx=(0, 10), pady=12)
        
        # Main container frame
        main_container = tk.Frame(popup, bg='#f5f7fa')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Scrollable content
        canvas = tk.Canvas(main_container, bg='#f5f7fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f5f7fa')
        
        def update_scrollregion(event=None):
            canvas.update_idletasks()
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=bbox)
                # Hide scrollbar if content fits within canvas
                content_height = bbox[3] - bbox[1]
                canvas_height = canvas.winfo_height()
                if content_height <= canvas_height and canvas_height > 0:
                    scrollbar.pack_forget()
                else:
                    if not scrollbar.winfo_viewable():
                        scrollbar.pack(side="right", fill="y")
        
        scrollable_frame.bind("<Configure>", update_scrollregion)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def on_canvas_configure(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar initially (will be hidden if not needed)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Content frame
        content_frame = tk.Frame(scrollable_frame, bg='#ffffff', relief=tk.RAISED, bd=2)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Patient and Doctor info
        info_frame = tk.LabelFrame(
            content_frame,
            text="Patient & Doctor Information",
            font=(FONT_UI, 11, 'bold'),
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
            font=(FONT_UI, 10),
            bg='#ffffff',
            fg='#374151',
            justify=tk.LEFT,
            anchor='w'
        ).pack(fill=tk.X, padx=5, pady=5)
        
        # Vital Signs & Measurements
        has_vitals = any([
            prescription_data.get('weight'),
            prescription_data.get('spo2'),
            prescription_data.get('hr'),
            prescription_data.get('rr'),
            prescription_data.get('bp'),
            prescription_data.get('height'),
            prescription_data.get('ideal_body_weight'),
            prescription_data.get('follow_up_date')
        ])
        
        if has_vitals:
            vitals_frame = tk.LabelFrame(
                content_frame,
                text="📊 Vital Signs & Measurements",
                font=(FONT_UI, 11, 'bold'),
                bg='#ffffff',
                fg='#1a237e',
                padx=15,
                pady=10
            )
            vitals_frame.pack(fill=tk.X, padx=15, pady=10)
            
            # Create a grid layout for vital signs
            vitals_grid = tk.Frame(vitals_frame, bg='#ffffff')
            vitals_grid.pack(fill=tk.X, padx=5, pady=5)
            
            # Configure grid columns for equal spacing
            vitals_grid.grid_columnconfigure(0, weight=1, uniform='vitals')
            vitals_grid.grid_columnconfigure(1, weight=1, uniform='vitals')
            vitals_grid.grid_columnconfigure(2, weight=1, uniform='vitals')
            vitals_grid.grid_columnconfigure(3, weight=1, uniform='vitals')
            
            # Helper function to create vital sign display
            def create_vital_display(parent, row, col, label_text, value):
                """Helper function to create a vital sign display"""
                if not value:
                    return
                frame = tk.Frame(parent, bg='#ffffff')
                frame.grid(row=row, column=col, padx=10, pady=5, sticky='ew')
                tk.Label(
                    frame,
                    text=label_text,
                    font=(FONT_UI, 9, 'bold'),
                    bg='#ffffff',
                    fg='#6b7280'
                ).pack(anchor='w')
                tk.Label(
                    frame,
                    text=str(value),
                    font=(FONT_UI, 10),
                    bg='#ffffff',
                    fg='#374151'
                ).pack(anchor='w', pady=(2, 0))
            
            # Get vital signs values
            weight = prescription_data.get('weight', '')
            spo2 = prescription_data.get('spo2', '')
            hr = prescription_data.get('hr', '')
            rr = prescription_data.get('rr', '')
            bp = prescription_data.get('bp', '')
            height = prescription_data.get('height', '')
            ibw = prescription_data.get('ideal_body_weight', '')
            followup = prescription_data.get('follow_up_date', '')
            
            # Row 1: Weight, SPO2, HR, RR
            row = 0
            if weight or spo2 or hr or rr:
                if weight:
                    create_vital_display(vitals_grid, row, 0, "Weight (Kgs)", weight)
                if spo2:
                    create_vital_display(vitals_grid, row, 1, "SPO2 (%)", spo2)
                if hr:
                    create_vital_display(vitals_grid, row, 2, "HR (/min)", hr)
                if rr:
                    create_vital_display(vitals_grid, row, 3, "RR (/min)", rr)
                row += 1
            
            # Row 2: BP, Height, Ideal Body Weight, Follow-up Date
            if bp or height or ibw or followup:
                if bp:
                    create_vital_display(vitals_grid, row, 0, "BP (mmHg)", bp)
                if height:
                    create_vital_display(vitals_grid, row, 1, "Height (Mtrs)", height)
                if ibw:
                    create_vital_display(vitals_grid, row, 2, "Ideal Body Weight (Kgs)", ibw)
                if followup:
                    create_vital_display(vitals_grid, row, 3, "Follow-up Date", followup)
        
        # Diagnosis
        if prescription_data.get('diagnosis'):
            diagnosis_frame = tk.LabelFrame(
                content_frame,
                text="Diagnosis",
                font=(FONT_UI, 11, 'bold'),
                bg='#ffffff',
                fg='#1a237e',
                padx=15,
                pady=10
            )
            diagnosis_frame.pack(fill=tk.X, padx=15, pady=10)
            
            diagnosis_label = tk.Label(
                diagnosis_frame,
                text=prescription_data.get('diagnosis', ''),
                font=(FONT_UI, 10),
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
                font=(FONT_UI, 11, 'bold'),
                bg='#ffffff',
                fg='#1a237e',
                padx=15,
                pady=10
            )
            medicines_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
            
            # Treeview for medicines - show all items
            med_columns = ('Medicine', 'Type', 'Dosage', 'Frequency', 'Duration', 'Instructions')
            med_tree = ttk.Treeview(medicines_frame, columns=med_columns, show='headings', height=len(items) if items else 1)
            
            for col in med_columns:
                med_tree.heading(col, text=col)
                if col == 'Medicine':
                    med_tree.column(col, width=200, anchor='center')
                elif col == 'Type':
                    med_tree.column(col, width=90, anchor='center')
                elif col == 'Instructions':
                    med_tree.column(col, width=200, anchor='center')
                else:
                    med_tree.column(col, width=120, anchor='center')
            
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
                font=(FONT_UI, 11, 'bold'),
                bg='#ffffff',
                fg='#1a237e',
                padx=15,
                pady=10
            )
            notes_frame.pack(fill=tk.X, padx=15, pady=10)
            
            notes_label = tk.Label(
                notes_frame,
                text=prescription_data.get('notes', ''),
                font=(FONT_UI, 10),
                bg='#ffffff',
                fg='#374151',
                wraplength=700,
                justify=tk.LEFT,
                anchor='w'
            )
            notes_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Update scroll region and window size after all content is added
        popup.update_idletasks()
        update_scrollregion()
        
        # Calculate optimal window size (max 90% of screen, min 800x600)
        content_height = scrollable_frame.winfo_reqheight() + 120  # Add header and padding
        content_width = max(800, scrollable_frame.winfo_reqwidth() + 60)  # Add padding
        
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        
        max_width = int(screen_width * 0.9)
        max_height = int(screen_height * 0.9)
        
        window_width = min(content_width, max_width)
        window_height = min(content_height, max_height)
        
        # Center the window
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        popup.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Final update to ensure scrollbar visibility is correct
        popup.update_idletasks()
        update_scrollregion()
    
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
        else:
            existing_items = []
        
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
        
        # Apply fade-in animation to the popup window
        popup.update_idletasks()
        AnimationHelper.fade_in_window(popup, duration=250)
        
        # Use popup as parent for all widgets
        form_parent = popup
        
        # Create scrollable container with better background
        canvas = tk.Canvas(form_parent, bg='#f5f7fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f5f7fa')
        
        def update_scroll_region(event=None):
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", update_scroll_region)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def on_canvas_configure(event):
            """Update canvas window width when canvas is resized"""
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        
        # Mouse wheel scrolling - works from anywhere in the window
        def on_mousewheel(event):
            """Handle mouse wheel scrolling"""
            # Windows uses delta, Linux/Mac uses num
            if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
                canvas.yview_scroll(-1, "units")
            elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
                canvas.yview_scroll(1, "units")
            return "break"
        
        # Bind mouse wheel to canvas
        canvas.bind("<MouseWheel>", on_mousewheel)
        canvas.bind("<Button-4>", on_mousewheel)  # Linux scroll up
        canvas.bind("<Button-5>", on_mousewheel)  # Linux scroll down
        
        # Also bind to the popup window so scrolling works from anywhere
        popup.bind("<MouseWheel>", lambda e: on_mousewheel(e) if canvas.winfo_exists() else None)
        popup.bind("<Button-4>", lambda e: on_mousewheel(e) if canvas.winfo_exists() else None)
        popup.bind("<Button-5>", lambda e: on_mousewheel(e) if canvas.winfo_exists() else None)
        
        # Bind to scrollable frame and all child widgets for universal scrolling
        def bind_mousewheel_to_widget(widget):
            """Recursively bind mouse wheel to widget and its children"""
            widget.bind("<MouseWheel>", on_mousewheel)
            widget.bind("<Button-4>", on_mousewheel)
            widget.bind("<Button-5>", on_mousewheel)
            for child in widget.winfo_children():
                try:
                    bind_mousewheel_to_widget(child)
                except:
                    pass
        
        # Bind mouse wheel to scrollable frame after it's created
        def bind_all_widgets():
            bind_mousewheel_to_widget(scrollable_frame)
        
        popup.after(100, bind_all_widgets)
        
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
        
        # Animate header appearance
        popup.after(50, lambda: AnimationHelper.fade_in_widget(header_frame, duration=300))
        
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
            font=(FONT_UI, 11, 'bold'),
            bg='#1e40af',
            fg=mode_color
        )
        mode_label.pack()
        
        title_text = f"Prescription ID: {prescription_id}"
        title_label = tk.Label(
            title_frame,
            text=title_text,
            font=(FONT_UI, 12, 'bold'),
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
            font=(FONT_UI, 10, 'bold'),
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
        
        # Add smooth hover effect to close button
        def on_close_enter(e):
            AnimationHelper.animate_color_transition(back_btn, '#6b7280', '#4b5563', duration=150)
        def on_close_leave(e):
            AnimationHelper.animate_color_transition(back_btn, '#4b5563', '#6b7280', duration=150)
        back_btn.bind('<Enter>', on_close_enter)
        back_btn.bind('<Leave>', on_close_leave)
        
        # Form container with padding
        form_container = tk.Frame(main_frame, bg='#ffffff')
        form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Animate form container appearance
        popup.after(100, lambda: AnimationHelper.fade_in_widget(form_container, duration=400))
        
        # Two-column layout
        left_column = tk.Frame(form_container, bg='#ffffff')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_column = tk.Frame(form_container, bg='#ffffff')
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Animate columns with slight delay
        popup.after(150, lambda: AnimationHelper.fade_in_widget(left_column, duration=300))
        popup.after(200, lambda: AnimationHelper.fade_in_widget(right_column, duration=300))
        
        # Form fields frame with better styling
        form_frame = tk.LabelFrame(
            left_column, 
            text="👤 Patient & Doctor Information", 
            font=(FONT_UI, 11, 'bold'), 
            bg='#ffffff', 
            fg='#1a237e',
            padx=20, 
            pady=15,
            relief=tk.RAISED,
            bd=2
        )
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Animate form frame appearance
        popup.after(180, lambda: AnimationHelper.fade_in_widget(form_frame, duration=350))
        
        # Status indicator frame (shows completion status)
        status_frame = tk.Frame(form_frame, bg='#ffffff', pady=5)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        status_label = tk.Label(
            status_frame,
            text="⚪ Required fields not completed",
            font=(FONT_UI, 9, 'bold'),
            bg='#ffffff',
            fg='#ef4444'
        )
        status_label.pack(side=tk.LEFT)
        
        def update_status():
            """Update status indicator with smooth animation"""
            patient_status = "✓" if selected_patient_id['value'] else "✗"
            doctor_status = "✓" if selected_doctor_id['value'] else "✗"
            med_status = "✓" if medicines else "✗"
            
            if selected_patient_id['value'] and selected_doctor_id['value'] and medicines:
                new_text = "✅ All required fields completed"
                new_color = '#10b981'
            else:
                new_text = f"⚪ Patient: {patient_status} | Doctor: {doctor_status} | Medicines: {med_status}"
                new_color = '#f59e0b'
            
            # Smooth color transition
            current_color = status_label.cget('fg')
            AnimationHelper.animate_color_transition(status_label, current_color, new_color, duration=300)
            status_label.config(text=new_text, fg=new_color)
        
        # Patient selection with popup button
        patient_label_frame = tk.Frame(form_frame, bg='#ffffff')
        patient_label_frame.pack(fill=tk.X, pady=(0, 8))
        
        patient_title_frame = tk.Frame(patient_label_frame, bg='#ffffff')
        patient_title_frame.pack(fill=tk.X)
        
        tk.Label(patient_title_frame, text="Patient *", font=(FONT_UI, 10, 'bold'), bg='#ffffff', fg='#374151').pack(side=tk.LEFT, anchor='w')
        
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
            font=(FONT_UI, 10),
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
            
            # Apply fade-in animation
            patient_popup.update_idletasks()
            AnimationHelper.fade_in_window(patient_popup, duration=200)
            
            # Header
            header_frame = tk.Frame(patient_popup, bg='#1e40af', height=60)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            tk.Label(
                header_frame,
                text="Select Patient",
                font=(FONT_UI, 14, 'bold'),
                bg='#1e40af',
                fg='white'
            ).pack(pady=18)
            
            # Search frame
            search_frame = tk.Frame(patient_popup, bg='#f5f7fa', padx=20, pady=15)
            search_frame.pack(fill=tk.X)
            
            tk.Label(
                search_frame,
                text="Search:",
                font=(FONT_UI, 10, 'bold'),
                bg='#f5f7fa',
                fg='#374151'
            ).pack(side=tk.LEFT, padx=5)
            
            search_var = tk.StringVar()
            search_entry = tk.Entry(
                search_frame,
                textvariable=search_var,
                font=(FONT_UI, 10),
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
                    tree.column(col, width=150, anchor='center')
                elif col in ['First Name', 'Last Name']:
                    tree.column(col, width=150, anchor='center')
                else:
                    tree.column(col, width=100, anchor='center')
            
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
                font=(FONT_UI, 10, 'bold'),
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
                font=(FONT_UI, 10),
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
            font=(FONT_UI, 10, 'bold'),
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
        
        # Add smooth hover effect
        if not view_only:
            def on_patient_btn_enter(e):
                AnimationHelper.animate_color_transition(patient_btn, '#3b82f6', '#2563eb', duration=150)
            def on_patient_btn_leave(e):
                AnimationHelper.animate_color_transition(patient_btn, '#2563eb', '#3b82f6', duration=150)
            patient_btn.bind('<Enter>', on_patient_btn_enter)
            patient_btn.bind('<Leave>', on_patient_btn_leave)
        
        # Doctor selection with popup button
        doctor_label_frame = tk.Frame(form_frame, bg='#ffffff')
        doctor_label_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(doctor_label_frame, text="Doctor *", font=(FONT_UI, 10, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        
        doctor_frame = tk.Frame(form_frame, bg='#ffffff')
        doctor_frame.pack(fill=tk.X, pady=(0, 15))
        
        doctor_var = tk.StringVar(value="Click to select doctor..." if not view_only else "No doctor selected")
        doctor_display = tk.Entry(
            doctor_frame,
            textvariable=doctor_var,
            font=(FONT_UI, 10),
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
            
            # Apply fade-in animation
            doctor_popup.update_idletasks()
            AnimationHelper.fade_in_window(doctor_popup, duration=200)
            
            # Header
            header_frame = tk.Frame(doctor_popup, bg='#1e40af', height=60)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            tk.Label(
                header_frame,
                text="Select Doctor",
                font=(FONT_UI, 14, 'bold'),
                bg='#1e40af',
                fg='white'
            ).pack(pady=18)
            
            # Search frame
            search_frame = tk.Frame(doctor_popup, bg='#f5f7fa', padx=20, pady=15)
            search_frame.pack(fill=tk.X)
            
            tk.Label(
                search_frame,
                text="Search:",
                font=(FONT_UI, 10, 'bold'),
                bg='#f5f7fa',
                fg='#374151'
            ).pack(side=tk.LEFT, padx=5)
            
            search_var = tk.StringVar()
            search_entry = tk.Entry(
                search_frame,
                textvariable=search_var,
                font=(FONT_UI, 10),
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
                    tree.column(col, width=150, anchor='center')
                elif col in ['First Name', 'Last Name']:
                    tree.column(col, width=150, anchor='center')
                elif col == 'Specialization':
                    tree.column(col, width=180, anchor='center')
                else:
                    tree.column(col, width=150, anchor='center')
            
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
                font=(FONT_UI, 10, 'bold'),
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
                font=(FONT_UI, 10),
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
            font=(FONT_UI, 10, 'bold'),
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
        
        # Add smooth hover effect
        if not view_only:
            def on_doctor_btn_enter(e):
                AnimationHelper.animate_color_transition(doctor_btn, '#3b82f6', '#2563eb', duration=150)
            def on_doctor_btn_leave(e):
                AnimationHelper.animate_color_transition(doctor_btn, '#2563eb', '#3b82f6', duration=150)
            doctor_btn.bind('<Enter>', on_doctor_btn_enter)
            doctor_btn.bind('<Leave>', on_doctor_btn_leave)
        
        # Appointment ID (optional)
        appointment_label_frame = tk.Frame(form_frame, bg='#ffffff')
        appointment_label_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(appointment_label_frame, text="Appointment ID (Optional)", font=(FONT_UI, 10), bg='#ffffff', fg='#6b7280').pack(anchor='w')
        appointment_var = tk.StringVar()
        appointment_entry = tk.Entry(form_frame, textvariable=appointment_var, font=(FONT_UI, 10), relief=tk.SOLID, bd=1)
        appointment_entry.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Date with calendar picker
        date_label_frame = tk.Frame(form_frame, bg='#ffffff')
        date_label_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(date_label_frame, text="Date", font=(FONT_UI, 10, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        
        date_input_frame = tk.Frame(form_frame, bg='#ffffff')
        date_input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Set entry state based on view_only
        entry_state = 'readonly' if view_only else 'normal'
        date_entry = tk.Entry(date_input_frame, font=(FONT_UI, 10), relief=tk.SOLID, bd=1, state=entry_state)
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
            
            # Apply fade-in animation
            calendar_window.update_idletasks()
            AnimationHelper.fade_in_window(calendar_window, duration=200)
            
            # Header
            header_frame = tk.Frame(calendar_window, bg='#1e40af', height=40)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            tk.Label(
                header_frame,
                text="Select Date",
                font=(FONT_UI, 12, 'bold'),
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
                        font=(FONT_UI, 9, 'bold'),
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
                        font=(FONT_UI, 9),
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
                font=(FONT_UI, 10, 'bold'),
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
                font=(FONT_UI, 11, 'bold'),
                bg='#ffffff',
                fg='#1a237e'
            )
            month_label.pack(side=tk.LEFT, expand=True)
            
            next_btn = tk.Button(
                nav_frame,
                text="▶",
                command=next_month,
                font=(FONT_UI, 10, 'bold'),
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
                font=(FONT_UI, 9),
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
                font=(FONT_UI, 9),
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
            font=(FONT_UI, 12),
            bg='#3b82f6',
            fg='white',
            width=3,
            relief=tk.FLAT,
            cursor='hand2' if not view_only else 'arrow',
            activebackground='#2563eb',
            state='normal' if not view_only else 'disabled'
        )
        calendar_btn.pack(side=tk.LEFT)
        
        # Add smooth hover effect to calendar button
        if not view_only:
            def on_calendar_enter(e):
                AnimationHelper.animate_color_transition(calendar_btn, '#3b82f6', '#2563eb', duration=150)
            def on_calendar_leave(e):
                AnimationHelper.animate_color_transition(calendar_btn, '#2563eb', '#3b82f6', duration=150)
            calendar_btn.bind('<Enter>', on_calendar_enter)
            calendar_btn.bind('<Leave>', on_calendar_leave)
        
        # Vital Signs Section - Better organized layout
        vitals_frame = tk.LabelFrame(
            form_frame,
            text="📊 Vital Signs & Measurements",
            font=(FONT_UI, 11, 'bold'),
            bg='#ffffff',
            fg='#1a237e',
            padx=20,
            pady=15,
            relief=tk.RAISED,
            bd=2
        )
        vitals_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create a grid layout for better organization
        vitals_grid = tk.Frame(vitals_frame, bg='#ffffff')
        vitals_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Configure grid columns for equal spacing
        vitals_grid.grid_columnconfigure(0, weight=1, uniform='vitals')
        vitals_grid.grid_columnconfigure(1, weight=1, uniform='vitals')
        vitals_grid.grid_columnconfigure(2, weight=1, uniform='vitals')
        vitals_grid.grid_columnconfigure(3, weight=1, uniform='vitals')
        
        # Helper function to create vital field
        def create_vital_field(parent, row, col, label_text):
            """Helper function to create a vital sign field"""
            frame = tk.Frame(parent, bg='#ffffff')
            frame.grid(row=row, column=col, padx=15, pady=8, sticky='ew')
            tk.Label(frame, text=label_text, font=(FONT_UI, 9, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w', pady=(0, 3))
            var = tk.StringVar()
            entry = tk.Entry(frame, textvariable=var, font=(FONT_UI, 10), width=15, relief=tk.SOLID, bd=1, state='normal' if not view_only else 'disabled', bg='#f9fafb')
            entry.pack(fill=tk.X)
            return var, entry
        
        # Row 1: Weight, SPO2, HR, RR
        weight_var, weight_entry = create_vital_field(vitals_grid, 0, 0, "Weight (Kgs)")
        spo2_var, spo2_entry = create_vital_field(vitals_grid, 0, 1, "SPO2 (%)")
        hr_var, hr_entry = create_vital_field(vitals_grid, 0, 2, "HR (/min)")
        rr_var, rr_entry = create_vital_field(vitals_grid, 0, 3, "RR (/min)")
        
        # Row 2: BP, Height, Ideal Body Weight, Follow-up Date
        bp_var, bp_entry = create_vital_field(vitals_grid, 1, 0, "BP (mmHg)")
        height_var, height_entry = create_vital_field(vitals_grid, 1, 1, "Height (Mtrs)")
        ibw_var, ibw_entry = create_vital_field(vitals_grid, 1, 2, "Ideal Body Weight (Kgs)")
        followup_var, followup_entry = create_vital_field(vitals_grid, 1, 3, "Follow-up Date")
        
        # Diagnosis with templates
        diagnosis_label_frame = tk.Frame(form_frame, bg='#ffffff')
        diagnosis_label_frame.pack(fill=tk.X, pady=(0, 8))
        
        diagnosis_title_frame = tk.Frame(diagnosis_label_frame, bg='#ffffff')
        diagnosis_title_frame.pack(fill=tk.X)
        
        tk.Label(diagnosis_title_frame, text="Diagnosis", font=(FONT_UI, 10, 'bold'), bg='#ffffff', fg='#374151').pack(side=tk.LEFT, anchor='w')
        
        # ICD Codes field - cleaner layout
        icd_frame = tk.Frame(diagnosis_label_frame, bg='#ffffff')
        icd_frame.pack(fill=tk.X, pady=(8, 0))
        icd_label_frame = tk.Frame(icd_frame, bg='#ffffff')
        icd_label_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(icd_label_frame, text="ICD Codes (optional):", font=(FONT_UI, 9, 'bold'), bg='#ffffff', fg='#374151').pack(side=tk.LEFT)
        tk.Label(icd_label_frame, text="💡 Enter codes separated by commas (e.g., D51.9, E55.9)", font=(FONT_UI, 8), bg='#ffffff', fg='#9ca3af').pack(side=tk.LEFT, padx=(10, 0))
        icd_var = tk.StringVar()
        icd_entry = tk.Entry(icd_frame, textvariable=icd_var, font=(FONT_UI, 10), relief=tk.SOLID, bd=1, state='normal' if not view_only else 'disabled', bg='#f9fafb')
        icd_entry.pack(fill=tk.X, pady=(0, 5), ipady=5)
        
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
            font=(FONT_UI, 8),
            bg='#f0f9ff',
            fg='#6b7280'
        ).pack(side=tk.LEFT, padx=5, pady=3)
        
        for diag in common_diagnoses[:6]:  # Show first 6
            btn = tk.Button(
                template_frame,
                text=diag[:25] + "..." if len(diag) > 25 else diag,
                command=lambda d=diag: insert_diagnosis_template(d),
                font=(FONT_UI, 7),
                bg='#dbeafe',
                fg='#1e40af',
                padx=8,
                pady=2,
                relief=tk.FLAT,
                cursor='hand2',
                activebackground='#bfdbfe'
            )
            btn.pack(side=tk.LEFT, padx=2, pady=3)
        
        diagnosis_text = tk.Text(form_frame, font=(FONT_UI, 10), height=4, wrap=tk.WORD, relief=tk.SOLID, bd=1, padx=8, pady=8, bg='#f9fafb', state='normal' if not view_only else 'disabled')
        diagnosis_text.pack(fill=tk.X, pady=(0, 15))
        
        # Additional Notes section
        notes_frame = tk.LabelFrame(
            right_column, 
            text="📝 Additional Notes", 
            font=(FONT_UI, 11, 'bold'), 
            bg='#ffffff', 
            fg='#1a237e',
            padx=20, 
            pady=15,
            relief=tk.RAISED,
            bd=2
        )
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Animate notes frame appearance
        popup.after(220, lambda: AnimationHelper.fade_in_widget(notes_frame, duration=350))
        
        notes_label_frame = tk.Frame(notes_frame, bg='#ffffff')
        notes_label_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(notes_label_frame, text="Doctor's Notes", font=(FONT_UI, 10), bg='#ffffff', fg='#6b7280').pack(anchor='w')
        notes_text = tk.Text(notes_frame, font=(FONT_UI, 10), height=12, wrap=tk.WORD, relief=tk.SOLID, bd=1, padx=5, pady=5, state='normal' if not view_only else 'disabled')
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
            
            # Set vital signs
            weight_var.set(prescription_data.get('weight', ''))
            spo2_var.set(prescription_data.get('spo2', ''))
            hr_var.set(prescription_data.get('hr', ''))
            rr_var.set(prescription_data.get('rr', ''))
            bp_var.set(prescription_data.get('bp', ''))
            height_var.set(prescription_data.get('height', ''))
            ibw_var.set(prescription_data.get('ideal_body_weight', ''))
            followup_var.set(prescription_data.get('follow_up_date', ''))
            
            # Set diagnosis and ICD codes
            diagnosis_text.delete('1.0', tk.END)
            diagnosis_text.insert('1.0', prescription_data.get('diagnosis', ''))
            icd_var.set(prescription_data.get('icd_codes', ''))
            
            # Set notes
            notes_text.delete('1.0', tk.END)
            notes_text.insert('1.0', prescription_data.get('notes', ''))
        
        # Medicines section - spans full width with better styling
        medicines_frame = tk.LabelFrame(
            main_frame, 
            text="💊 Prescribed Medicines", 
            font=(FONT_UI, 11, 'bold'), 
            bg='#ffffff', 
            fg='#1a237e',
            padx=20, 
            pady=15,
            relief=tk.RAISED,
            bd=2
        )
        medicines_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Animate medicines section appearance
        popup.after(250, lambda: AnimationHelper.fade_in_widget(medicines_frame, duration=400))
        
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
        
        # Get all medicines from medicines_master table only
        db_medicines = self.db.get_all_medicines()
        
        # Use only medicines from medicines_master, combine with default medicines as fallback
        common_medicines = list(set(default_medicines + db_medicines))
        common_medicines.sort()  # Sort alphabetically
        
        # Medicines list with remove button - better styling
        med_list_frame = tk.Frame(medicines_frame, bg='#ffffff')
        med_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Info label
        info_text = "📋 Added Medicines (Double-click to remove"
        if not view_only:
            info_text += " | Click Frequency/Duration to edit"
        info_text += ")"
        info_label = tk.Label(
            med_list_frame, 
            text=info_text, 
            font=(FONT_UI, 9), 
            bg='#ffffff', 
            fg='#6b7280',
            anchor='w'
        )
        info_label.pack(fill=tk.X, pady=(0, 5))
        
        med_columns = ('Medicine', 'Type', 'Dosage', 'Frequency', 'Duration', 'Purpose', 'Instructions')
        med_tree = ttk.Treeview(med_list_frame, columns=med_columns, show='headings', height=6)
        
        # Configure treeview style
        style = ttk.Style()
        style.configure("MedTreeview.Treeview", 
                       font=(FONT_UI, 9), 
                       rowheight=28,
                       background='#ffffff',
                       foreground='#374151',
                       fieldbackground='#ffffff')
        style.configure("MedTreeview.Treeview.Heading", 
                       font=(FONT_UI, 9, 'bold'), 
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
                med_tree.column(col, width=200, anchor='center')
            elif col == 'Type':
                med_tree.column(col, width=90, anchor='center')
            elif col == 'Purpose':
                med_tree.column(col, width=150, anchor='center')
            elif col == 'Instructions':
                med_tree.column(col, width=200, anchor='center')
            else:
                med_tree.column(col, width=120, anchor='center')
        
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
        
        # Inline editing with dropdowns for Frequency and Duration
        editing_combo = None
        editing_item = None
        editing_column = None
        
        def start_edit_cell(event):
            """Start editing a cell with dropdown"""
            nonlocal editing_combo, editing_item, editing_column
            
            # Get clicked region
            region = med_tree.identify_region(event.x, event.y)
            if region != "cell":
                return
            
            # Get clicked item and column
            item = med_tree.identify_row(event.y)
            column = med_tree.identify_column(event.x)
            
            if not item or not column:
                return
            
            # Get column index (column is like '#1', '#2', etc.)
            col_index = int(column.replace('#', '')) - 1
            column_name = med_columns[col_index] if col_index < len(med_columns) else None
            
            # Only allow editing Frequency and Duration columns
            if column_name not in ['Frequency', 'Duration']:
                return
            
            # Don't allow editing in view-only mode
            if view_only:
                return
            
            # Close any existing editor
            if editing_combo:
                editing_combo.destroy()
                editing_combo = None
            
            # Get current value
            current_values = list(med_tree.item(item, 'values'))
            current_value = current_values[col_index] if col_index < len(current_values) else ''
            
            # Get bounding box of the cell
            bbox = med_tree.bbox(item, column)
            if not bbox:
                return
            
            x, y, width, height = bbox
            
            # Determine options based on column
            if column_name == 'Frequency':
                options = [
                    "Once daily", "Twice daily", "Three times daily", "Four times daily",
                    "Once in morning", "Once in evening", "Once at night",
                    "Every 4 hours", "Every 6 hours", "Every 8 hours", "Every 12 hours",
                    "As needed", "Before meals", "After meals", "With meals",
                    "Before bedtime", "As directed", "When required",
                    "Once weekly", "Twice weekly", "Three times weekly",
                    "Every other day", "Alternate days",
                    "1x/day", "2x/day", "3x/day", "4x/day"
                ]
            else:  # Duration
                options = [
                    "1 day", "2 days", "3 days", "4 days", "5 days", "6 days", "7 days",
                    "10 days", "14 days", "15 days", "21 days",
                    "1 week", "2 weeks", "3 weeks", "4 weeks",
                    "1 month", "2 months", "3 months", "6 months",
                    "Until finished", "As needed", "As directed",
                    "For 5 days", "For 7 days", "For 10 days", "For 14 days"
                ]
            
            # Create combobox overlay
            editing_item = item
            editing_column = col_index
            
            # Get the parent window
            parent_window = med_tree.winfo_toplevel()
            
            editing_combo = ttk.Combobox(
                parent_window,
                values=options,
                font=(FONT_UI, 9),
                width=max(20, width // 8)
            )
            editing_combo.set(current_value)
            
            # Position the combobox over the cell
            # Get absolute coordinates of the tree widget
            tree_x = med_tree.winfo_rootx()
            tree_y = med_tree.winfo_rooty()
            # Get absolute coordinates of parent window
            parent_x = parent_window.winfo_rootx()
            parent_y = parent_window.winfo_rooty()
            # Calculate relative position
            rel_x = (tree_x - parent_x) + x
            rel_y = (tree_y - parent_y) + y
            editing_combo.place(x=rel_x, y=rel_y, width=width, height=height)
            editing_combo.focus_set()
            editing_combo.select_range(0, tk.END)
            
            def on_combo_select(event=None):
                """Handle combobox selection"""
                nonlocal editing_combo, editing_item, editing_column
                
                if not editing_item or editing_combo is None:
                    return
                
                new_value = editing_combo.get().strip()
                if new_value:
                    # Update tree item
                    current_values = list(med_tree.item(editing_item, 'values'))
                    if editing_column < len(current_values):
                        current_values[editing_column] = new_value
                        med_tree.item(editing_item, values=current_values)
                        
                        # Update medicine data map
                        if editing_item in medicine_data_map:
                            if editing_column == 3:  # Frequency column
                                medicine_data_map[editing_item]['frequency'] = new_value
                            elif editing_column == 4:  # Duration column
                                medicine_data_map[editing_item]['duration'] = new_value
                
                # Clean up
                if editing_combo:
                    editing_combo.destroy()
                    editing_combo = None
                editing_item = None
                editing_column = None
            
            def on_combo_escape(event):
                """Cancel editing on Escape"""
                nonlocal editing_combo, editing_item, editing_column
                if editing_combo:
                    editing_combo.destroy()
                    editing_combo = None
                editing_item = None
                editing_column = None
                return "break"
            
            def on_focus_out(event):
                """Handle focus loss - close editor when focus leaves"""
                # Only close if focus actually left (not just to dropdown)
                if editing_combo and editing_item:
                    try:
                        # Small delay to check if dropdown opened
                        parent_window.after(150, lambda: close_if_no_focus())
                    except:
                        pass
            
            def close_if_no_focus():
                """Close combobox if it doesn't have focus"""
                if editing_combo and editing_item:
                    try:
                        focused = parent_window.focus_get()
                        # If focus is not on combobox or its children, close it
                        if focused != editing_combo:
                            # Check if it's a child of combobox (dropdown list)
                            widget_str = str(focused)
                            if 'combobox' not in widget_str.lower():
                                on_combo_select()
                    except:
                        # If we can't determine focus, keep it open
                        pass
            
            def on_dropdown_click(event=None):
                """Ensure all options are shown when dropdown is clicked"""
                # Reset to all options when dropdown opens
                editing_combo['values'] = options
            
            editing_combo.bind('<<ComboboxSelected>>', on_combo_select)
            editing_combo.bind('<Return>', on_combo_select)
            editing_combo.bind('<Escape>', on_combo_escape)
            editing_combo.bind('<FocusOut>', on_focus_out)
            editing_combo.bind('<Button-1>', on_dropdown_click)
            # Also bind to down arrow key to open dropdown
            editing_combo.bind('<Down>', lambda e: (on_dropdown_click(), None))
            
            # Create StringVar and set up combobox with all options
            editing_combo_var = tk.StringVar(value=current_value)
            editing_combo.configure(textvariable=editing_combo_var)
            editing_combo['values'] = options  # Always show all options initially
            
            # Make it searchable - filter only when user types (KeyPress events)
            def on_key_press(event):
                """Filter options as user types"""
                # Get current text
                current_text = editing_combo_var.get().lower().strip()
                
                # Allow navigation keys without filtering
                if event.keysym in ['Up', 'Down', 'Return', 'Escape', 'Tab']:
                    return
                
                # Filter based on typed text
                if not current_text or len(current_text) < 1:
                    editing_combo['values'] = options
                else:
                    filtered = [opt for opt in options if current_text in opt.lower()]
                    if filtered and len(filtered) < len(options):
                        editing_combo['values'] = filtered
                    else:
                        editing_combo['values'] = options
                
                # Update after a short delay to catch the new value
                parent_window.after(10, lambda: update_filter())
            
            def update_filter():
                """Update filter based on current text"""
                if editing_combo is None:
                    return
                current_text = editing_combo_var.get().lower().strip()
                if not current_text:
                    editing_combo['values'] = options
                else:
                    filtered = [opt for opt in options if current_text in opt.lower()]
                    if filtered and len(filtered) < len(options):
                        editing_combo['values'] = filtered
                    else:
                        editing_combo['values'] = options
            
            # Bind key events for filtering
            editing_combo.bind('<KeyPress>', on_key_press)
            editing_combo.bind('<KeyRelease>', lambda e: update_filter())
            
            # Ensure all options are shown when dropdown arrow is clicked
            def ensure_all_options():
                """Reset to all options"""
                editing_combo['values'] = options
            
            # Bind to focus in to ensure all options are available
            editing_combo.bind('<FocusIn>', lambda e: ensure_all_options())
        
        # Bind single click to edit Frequency and Duration columns
        def on_tree_click(event):
            """Handle clicks on the tree"""
            # Only start editing if clicking on Frequency or Duration columns
            # and not already editing
            if editing_combo is None:
                region = med_tree.identify_region(event.x, event.y)
                if region == "cell":
                    column = med_tree.identify_column(event.x)
                    if column:
                        col_index = int(column.replace('#', '')) - 1
                        column_name = med_columns[col_index] if col_index < len(med_columns) else None
                        if column_name in ['Frequency', 'Duration'] and not view_only:
                            # Delay slightly to allow selection first
                            med_tree.after(100, lambda: start_edit_cell(event))
        
        med_tree.bind('<Button-1>', on_tree_click)
        
        # Bind double-click to remove (works on any column except when editing)
        def on_double_click(event):
            """Handle double-click to remove medicine"""
            if editing_combo is None:
                remove_selected_medicine()
        
        med_tree.bind('<Double-1>', on_double_click)
        
        # Add Remove Selected button below the medicine list
        remove_btn_frame = tk.Frame(medicines_frame, bg='#ffffff')
        remove_btn_frame.pack(fill=tk.X, pady=(5, 15))
        
        remove_selected_btn = tk.Button(
            remove_btn_frame,
            text="🗑️ Remove Selected",
            command=remove_selected_medicine,
            font=(FONT_UI, 9, 'bold'),
            bg='#ef4444',
            fg='white',
            padx=15,
            pady=6,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#dc2626'
        )
        remove_selected_btn.pack(side=tk.LEFT)
        
        # Add smooth hover effect
        if not view_only:
            def on_remove_enter(e):
                AnimationHelper.animate_color_transition(remove_selected_btn, '#ef4444', '#dc2626', duration=150)
            def on_remove_leave(e):
                AnimationHelper.animate_color_transition(remove_selected_btn, '#dc2626', '#ef4444', duration=150)
            remove_selected_btn.bind('<Enter>', on_remove_enter)
            remove_selected_btn.bind('<Leave>', on_remove_leave)
        
        # Add medicine frame with better styling
        add_med_frame = tk.LabelFrame(
            medicines_frame, 
            text="➕ Add New Medicine", 
            font=(FONT_UI, 10, 'bold'), 
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
        tk.Label(med_name_label_frame, text="Medicine Name *", font=(FONT_UI, 9, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        
        med_name_input_frame = tk.Frame(med_name_frame, bg='#ffffff')
        med_name_input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        med_name_var = tk.StringVar()
        med_name_entry = tk.Entry(
            med_name_input_frame,
            textvariable=med_name_var,
            font=(FONT_UI, 10),
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
            
            medicine_tree.column('Medicine Name', width=200, anchor='center', stretch=True)
            medicine_tree.column('Company', width=150, anchor='center', stretch=True)
            medicine_tree.column('Dosage (mg)', width=120, anchor='center', stretch=True)
            medicine_tree.column('Form', width=100, anchor='center', stretch=True)
            medicine_tree.column('Category', width=120, anchor='center', stretch=True)
            medicine_tree.column('Description', width=300, anchor='center', stretch=True)
            
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
            
            # Double-click to directly add medicine to list
            selected_medicine = {'name': None, 'dosage': None}
            
            def on_double_click(event):
                """Double-click to directly add medicine to the list"""
                selection = medicine_tree.selection()
                if not selection:
                    return
                
                item = medicine_tree.item(selection[0])
                values = item['values']
                if not values:
                    return
                
                # Get medicine details from the selected row
                med_name = values[0] if len(values) > 0 else ''
                dosage_value = values[2] if len(values) > 2 else ''
                
                if not med_name:
                    return
                
                # Close the medicine selector window first
                medicine_window.destroy()
                
                # Set medicine name and update dosage options
                med_name_var.set(med_name)
                update_dosage_options(med_name)
                
                # Set dosage if available and not comma-separated
                if dosage_value:
                    dosage_str = str(dosage_value).strip()
                    if ',' not in dosage_str and dosage_str:
                        dosage_var.set(dosage_str)
                    # If comma-separated, try to use first dosage or leave for user to select
                    elif ',' in dosage_str:
                        # Use first dosage from comma-separated list
                        first_dosage = dosage_str.split(',')[0].strip()
                        if first_dosage:
                            dosage_var.set(first_dosage)
                
                # Ensure default frequency and duration are set (use defaults from form)
                # These will be set by reset_add_medicine_defaults() or use explicit defaults
                if not frequency_var.get().strip():
                    # Try to use the default from outer scope, fallback to "Twice daily"
                    try:
                        frequency_var.set(default_frequency)
                    except NameError:
                        frequency_var.set("Twice daily")
                if not duration_var.get().strip():
                    # Try to use the default from outer scope, fallback to "5 days"
                    try:
                        duration_var.set(default_duration)
                    except NameError:
                        duration_var.set("5 days")
                
                # Directly add the medicine to the list
                # Small delay to ensure UI updates are complete
                popup.after(100, lambda: add_medicine())
            
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
            font=(FONT_UI, 9, 'bold'),
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
        
        # Add smooth hover effect
        if not view_only:
            def on_browse_enter(e):
                AnimationHelper.animate_color_transition(select_med_btn, '#6366f1', '#4f46e5', duration=150)
            def on_browse_leave(e):
                AnimationHelper.animate_color_transition(select_med_btn, '#4f46e5', '#6366f1', duration=150)
            select_med_btn.bind('<Enter>', on_browse_enter)
            select_med_btn.bind('<Leave>', on_browse_leave)
        
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
        tk.Label(dosage_label_frame, text="Dosage *", font=(FONT_UI, 9, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        
        # Common prescription presets
        presets_frame = tk.Frame(add_med_frame, bg='#ffffff')
        presets_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            presets_frame,
            text="💊 Quick Presets:",
            font=(FONT_UI, 8, 'bold'),
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
                font=(FONT_UI, 7),
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
            font=(FONT_UI, 9), 
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
        tk.Label(frequency_label_frame, text="Frequency *", font=(FONT_UI, 9, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        
        frequency_var = tk.StringVar()
        # Set combo state based on view_only
        combo_state = 'readonly' if view_only else 'normal'
        frequency_combo = ttk.Combobox(
            details_frame, 
            textvariable=frequency_var, 
            values=frequency_options, 
            font=(FONT_UI, 9), 
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
        tk.Label(duration_label_frame, text="Duration *", font=(FONT_UI, 9, 'bold'), bg='#ffffff', fg='#374151').pack(anchor='w')
        
        duration_var = tk.StringVar()
        duration_combo = ttk.Combobox(
            details_frame, 
            textvariable=duration_var, 
            values=duration_options, 
            font=(FONT_UI, 9), 
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

        # Default selections for fast entry (only in editable mode)
        def _pick_default(options, preferred):
            for p in preferred:
                if p in options:
                    return p
            return options[0] if options else ''

        default_frequency = _pick_default(
            frequency_options,
            preferred=["Twice daily", "Once daily", "2x/day", "1x/day"]
        )
        default_duration = _pick_default(
            duration_options,
            preferred=["5 days", "7 days", "For 5 days", "For 7 days"]
        )

        def reset_add_medicine_defaults():
            """Reset add-medicine inputs to defaults for quick entry."""
            if view_only:
                return
            if not frequency_var.get().strip():
                frequency_var.set(default_frequency)
            if not duration_var.get().strip():
                duration_var.set(default_duration)

        # Initialize defaults on first open
        reset_add_medicine_defaults()
        
        # Purpose field
        purpose_label_frame = tk.Frame(details_frame, bg='#ffffff')
        purpose_label_frame.grid(row=1, column=2, sticky='w', padx=(0, 8), pady=5)
        tk.Label(purpose_label_frame, text="Purpose", font=(FONT_UI, 9), bg='#ffffff', fg='#6b7280').pack(anchor='w')
        
        purpose_var = tk.StringVar()
        purpose_entry = tk.Entry(
            details_frame,
            textvariable=purpose_var,
            font=(FONT_UI, 9), 
            width=20,
            relief=tk.SOLID,
            bd=1,
            state=entry_state
        )
        purpose_entry.grid(row=1, column=3, padx=(0, 15), pady=5, sticky='ew', ipady=3)
        
        # Instructions field
        instructions_label_frame = tk.Frame(details_frame, bg='#ffffff')
        instructions_label_frame.grid(row=2, column=0, sticky='w', padx=(0, 8), pady=5)
        tk.Label(instructions_label_frame, text="Instructions", font=(FONT_UI, 9), bg='#ffffff', fg='#6b7280').pack(anchor='w')
        
        instructions_var = tk.StringVar()
        instructions_entry = tk.Entry(
            details_frame,
            textvariable=instructions_var,
            font=(FONT_UI, 9), 
            width=20,
            relief=tk.SOLID,
            bd=1,
            state=entry_state
        )
        instructions_entry.grid(row=2, column=1, padx=(0, 0), pady=5, sticky='ew', ipady=3)
        
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
            
            # Get purpose
            purpose = purpose_var.get().strip()
            
            # Add to tree (Medicine, Type, Dosage, Frequency, Duration, Purpose, Instructions)
            item = med_tree.insert('', tk.END, values=(med_name, medicine_type, dosage, frequency, duration, purpose, instructions))
            medicine_data = {
                'medicine_name': med_name,
                'dosage': dosage,
                'frequency': frequency,
                'duration': duration,
                'purpose': purpose,
                'instructions': instructions,
                'type': medicine_type
            }
            medicines.append(medicine_data)
            medicine_data_map[item] = medicine_data
            
            # Update status indicator
            update_status()
            
            # Animate the newly added item (highlight briefly)
            try:
                med_tree.selection_set(item)
                med_tree.see(item)
                # Remove selection after animation
                popup.after(500, lambda: med_tree.selection_remove(item))
            except:
                pass
            
            # Clear fields
            med_name_var.set('')
            dosage_var.set('')
            frequency_var.set(default_frequency)
            duration_var.set(default_duration)
            purpose_var.set('')
            instructions_entry.delete(0, tk.END)
            
            # Set focus back to medicine name for quick entry
            med_name_entry.focus_set()
            
            # Show success feedback with smooth animation
            med_tree.see(item)  # Scroll to show the newly added item
        
        # Add Medicine button - improved styling
        add_med_btn_frame = tk.Frame(add_med_frame, bg='#ffffff')
        add_med_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        add_med_btn = tk.Button(
            add_med_btn_frame,
            text="➕ Add Medicine to List",
            command=add_medicine if not view_only else lambda: None,
            font=(FONT_UI, 10, 'bold'),
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
        
        # Add smooth hover effect
        if not view_only:
            def on_add_med_enter(e):
                AnimationHelper.animate_color_transition(add_med_btn, '#3b82f6', '#2563eb', duration=150)
            def on_add_med_leave(e):
                AnimationHelper.animate_color_transition(add_med_btn, '#2563eb', '#3b82f6', duration=150)
            add_med_btn.bind('<Enter>', on_add_med_enter)
            add_med_btn.bind('<Leave>', on_add_med_leave)
        
        # Quick tip label
        tip_label = tk.Label(
            add_med_btn_frame,
            text="💡 Tip: Press Enter after filling fields to quickly add",
            font=(FONT_UI, 8),
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
                purpose = item.get('purpose', '')
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
                
                # Add to tree with purpose
                tree_item = med_tree.insert('', tk.END, values=(med_name, medicine_type, dosage, frequency, duration, purpose, instructions))
                medicine_data = {
                    'medicine_name': med_name,
                    'dosage': dosage,
                    'frequency': frequency,
                    'duration': duration,
                    'purpose': purpose,
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
            font=(FONT_UI, 8),
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
        
        # Animate button frame appearance
        popup.after(300, lambda: AnimationHelper.fade_in_widget(button_frame, duration=400))
        
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
                'notes': notes_text.get('1.0', tk.END).strip(),
                'weight': weight_var.get().strip(),
                'spo2': spo2_var.get().strip(),
                'hr': hr_var.get().strip(),
                'rr': rr_var.get().strip(),
                'bp': bp_var.get().strip(),
                'height': height_var.get().strip(),
                'ideal_body_weight': ibw_var.get().strip(),
                'follow_up_date': followup_var.get().strip(),
                'icd_codes': icd_var.get().strip()
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
            
            # Get vital signs
            weight = weight_var.get().strip()
            spo2 = spo2_var.get().strip()
            hr = hr_var.get().strip()
            rr = rr_var.get().strip()
            bp = bp_var.get().strip()
            height = height_var.get().strip()
            ideal_body_weight = ibw_var.get().strip()
            follow_up_date = followup_var.get().strip()
            icd_codes = icd_var.get().strip()
            
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
                    fontSize=10,
                    textColor=colors.HexColor('#1a237e'),
                    spaceAfter=2,
                    spaceBefore=4,
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
                elements.append(Spacer(1, 4*mm))
                
                # Patient Information (compact single line)
                compact_style = ParagraphStyle('Compact', parent=styles['Normal'], fontSize=9, spaceAfter=2, spaceBefore=0)
                age_gender = f"{patient_age}/{patient_gender}" if patient_age else patient_gender
                extra = []
                if patient.get('phone'):
                    extra.append(patient.get('phone'))
                if patient.get('address'):
                    addr = patient.get('address', '')
                    extra.append(addr[:40] + ('...' if len(addr) > 40 else ''))
                pt_text = f"<b>Patient:</b> {patient_name}  |  {age_gender}  |  ID: {patient_id}"
                if extra:
                    pt_text += f"  |  {' | '.join(extra)}"
                elements.append(Paragraph(pt_text, compact_style))
                elements.append(Spacer(1, 3*mm))
                
                # Vital Signs (compact single line)
                if weight or spo2 or hr or rr or bp or height or ideal_body_weight or follow_up_date:
                    v_parts = []
                    if weight:
                        v_parts.append(f"Wt:{weight}kg")
                    if height:
                        v_parts.append(f"Ht:{height}m")
                    if bp:
                        v_parts.append(f"BP:{bp}")
                    if hr:
                        v_parts.append(f"HR:{hr}")
                    if spo2:
                        v_parts.append(f"SPO2:{spo2}%")
                    if rr:
                        v_parts.append(f"RR:{rr}")
                    if ideal_body_weight:
                        v_parts.append(f"IBW:{ideal_body_weight}kg")
                    if follow_up_date:
                        v_parts.append(f"FUP:{follow_up_date}")
                    if v_parts:
                        elements.append(Paragraph(f"<b>Vitals:</b> {' | '.join(v_parts)}", compact_style))
                        elements.append(Spacer(1, 3*mm))
                
                # Diagnosis
                if diagnosis or icd_codes:
                    elements.append(Paragraph("<b>DIAGNOSIS</b>", heading_style))
                    if diagnosis:
                        elements.append(Paragraph(diagnosis.replace('\n', '<br/>'), normal_style))
                    if icd_codes:
                        elements.append(Paragraph(f"<b>ICD Codes:</b> {icd_codes}", normal_style))
                    elements.append(Spacer(1, 3*mm))
                
                # Medicines
                elements.append(Paragraph("<b>PRESCRIBED MEDICINES</b>", heading_style))
                
                med_data = [['R', 'Medicine Name', 'Dosage', 'Frequency', 'Duration', 'Purpose', 'Instructions']]
                for idx, med in enumerate(medicines, 1):
                    med_data.append([
                        str(idx),
                        med['medicine_name'],
                        med['dosage'],
                        med['frequency'],
                        med['duration'],
                        med.get('purpose', ''),
                        med.get('instructions', '')
                    ])
                
                med_table = Table(med_data, colWidths=[8*mm, 45*mm, 22*mm, 30*mm, 22*mm, 30*mm, 33*mm])
                med_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                    ('ALIGN', (5, 1), (6, -1), 'LEFT'),
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
                                          diagnosis, notes, medicines, patient_id, weight, spo2, hr, rr, bp, height, ideal_body_weight, follow_up_date, icd_codes)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}\n\nFalling back to text format...")
                _generate_text_prescription(patient, doctor, prescription_id, prescription_date, 
                                          diagnosis, notes, medicines, patient_id, weight, spo2, hr, rr, bp, height, ideal_body_weight, follow_up_date, icd_codes)
        
        def _generate_text_prescription(patient, doctor, prescription_id, prescription_date, 
                                       diagnosis, notes, medicines, patient_id, weight='', spo2='', hr='', rr='', bp='', height='', ideal_body_weight='', follow_up_date='', icd_codes=''):
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
            
            # Build vital signs text
            vitals_text = ""
            if weight or spo2 or hr or rr or bp or height or ideal_body_weight or follow_up_date:
                vitals_text = "\nVITAL SIGNS & MEASUREMENTS:\n"
                vitals_text += "-" * 60 + "\n"
                if weight:
                    vitals_text += f"Weight: {weight} Kgs\n"
                if spo2:
                    vitals_text += f"SPO2: {spo2}%\n"
                if hr:
                    vitals_text += f"HR: {hr}/min\n"
                if rr:
                    vitals_text += f"RR: {rr}/min\n"
                if bp:
                    vitals_text += f"BP: {bp} mmHg\n"
                if height:
                    vitals_text += f"Height: {height} Mtrs\n"
                if ideal_body_weight:
                    vitals_text += f"Ideal Body Weight: {ideal_body_weight} Kgs\n"
                if follow_up_date:
                    vitals_text += f"Follow-up Date: {follow_up_date}\n"
                vitals_text += "-" * 60 + "\n"
            
            print_text = f"""
================================================================
                    PRESCRIPTION
================================================================

Prescription ID: {prescription_id}
Date: {prescription_date}
{vitals_text}

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
{('ICD Codes: ' + icd_codes) if icd_codes else ''}

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
                if med.get('purpose'):
                    print_text += f"\n   Purpose: {med['purpose']}"
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
                font=(FONT_UI, 10, 'bold'),
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
                font=(FONT_UI, 10),
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
                font=(FONT_UI, 11, 'bold'),
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
            
            # Add smooth hover effect to save button
            def on_save_enter(e):
                AnimationHelper.animate_color_transition(save_btn, '#10b981', '#059669', duration=150)
            def on_save_leave(e):
                AnimationHelper.animate_color_transition(save_btn, '#059669', '#10b981', duration=150)
            save_btn.bind('<Enter>', on_save_enter)
            save_btn.bind('<Leave>', on_save_leave)
        
        # Print button - always show (can print even in view mode)
        print_btn = tk.Button(
            inner_button_frame,
            text="🖨️ Print Prescription",
            command=print_prescription,
            font=(FONT_UI, 10, 'bold'),
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
        
        # Add smooth hover effect to print button
        def on_print_enter(e):
            AnimationHelper.animate_color_transition(print_btn, '#f59e0b', '#d97706', duration=150)
        def on_print_leave(e):
            AnimationHelper.animate_color_transition(print_btn, '#d97706', '#f59e0b', duration=150)
        print_btn.bind('<Enter>', on_print_enter)
        print_btn.bind('<Leave>', on_print_leave)
        
        cancel_btn = tk.Button(
            inner_button_frame,
            text="❌ Cancel",
            command=back_to_list,
            font=(FONT_UI, 10),
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
            font=(FONT_UI, 8),
            bg='#f5f7fa',
            fg='#6b7280',
            anchor='w'
        )
        shortcuts_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Final update to ensure scroll region is correct after all widgets are created
        popup.update_idletasks()
        update_scroll_region()

