"""
Reports and Analytics Module
Enhanced with multiple report types, filtering, and export capabilities
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta, date
import csv
import os
from typing import Dict, List, Optional

# Backend imports
from backend.database import Database

# Try to import reportlab for PDF export
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Try to import tkcalendar for date picker
try:
    from tkcalendar import DateEntry
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False


class ReportsModule:
    """Enhanced Reports and analytics interface"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.current_report_type = "overview"
        self.from_date = None
        self.to_date = None
        
        self.create_ui()
        # Defer statistics loading to make UI appear faster
        self.parent.after(10, self.load_statistics)
    
    def create_ui(self):
        """Create enhanced user interface"""
        # Header with modern styling
        header = tk.Label(
            self.parent,
            text="Reports & Analytics Dashboard",
            font=('Segoe UI', 24, 'bold'),
            bg='#f5f7fa',
            fg='#1a237e'
        )
        header.pack(pady=15)
        
        # Main content frame
        content_frame = tk.Frame(self.parent, bg='#f5f7fa')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Filter frame
        filter_frame = tk.LabelFrame(
            content_frame,
            text="Report Filters",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#1a237e',
            relief=tk.FLAT,
            bd=0
        )
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Date range selection
        date_frame = tk.Frame(filter_frame, bg='white')
        date_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            date_frame,
            text="From Date:",
            font=('Segoe UI', 10),
            bg='white',
            fg='#374151'
        ).pack(side=tk.LEFT, padx=5)
        
        if CALENDAR_AVAILABLE:
            # Use calendar date picker
            default_from_date = datetime.now() - timedelta(days=30)
            self.from_date_entry = DateEntry(
                date_frame,
                font=('Segoe UI', 10),
                width=12,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd',
                year=default_from_date.year,
                month=default_from_date.month,
                day=default_from_date.day
            )
            self.from_date_entry.pack(side=tk.LEFT, padx=5)
            
            tk.Label(
                date_frame,
                text="To Date:",
                font=('Segoe UI', 10),
                bg='white',
                fg='#374151'
            ).pack(side=tk.LEFT, padx=5)
            
            default_to_date = datetime.now()
            self.to_date_entry = DateEntry(
                date_frame,
                font=('Segoe UI', 10),
                width=12,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd',
                year=default_to_date.year,
                month=default_to_date.month,
                day=default_to_date.day
            )
            self.to_date_entry.pack(side=tk.LEFT, padx=5)
        else:
            # Fallback to text entry if tkcalendar is not available
            self.from_date_entry = tk.Entry(
                date_frame,
                font=('Segoe UI', 10),
                width=12
            )
            self.from_date_entry.pack(side=tk.LEFT, padx=5)
            self.from_date_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
            
            tk.Label(
                date_frame,
                text="To Date:",
                font=('Segoe UI', 10),
                bg='white',
                fg='#374151'
            ).pack(side=tk.LEFT, padx=5)
            
            self.to_date_entry = tk.Entry(
                date_frame,
                font=('Segoe UI', 10),
                width=12
            )
            self.to_date_entry.pack(side=tk.LEFT, padx=5)
            self.to_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        tk.Button(
            date_frame,
            text="Apply Filters",
            command=self.apply_filters,
            font=('Segoe UI', 9, 'bold'),
            bg='#3b82f6',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#2563eb'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            date_frame,
            text="Reset",
            command=self.reset_filters,
            font=('Segoe UI', 9),
            bg='#6b7280',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#4b5563'
        ).pack(side=tk.LEFT, padx=5)
        
        # Report type selection
        report_type_frame = tk.Frame(filter_frame, bg='white')
        report_type_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Label(
            report_type_frame,
            text="Report Type:",
            font=('Segoe UI', 10),
            bg='white',
            fg='#374151'
        ).pack(side=tk.LEFT, padx=5)
        
        self.report_type_var = tk.StringVar(value="overview")
        report_types = [
            ("Overview", "overview"),
            ("Financial", "financial"),
            ("Patient", "patient"),
            ("Doctor Performance", "doctor"),
            ("Appointments", "appointment"),
            ("Prescriptions", "prescription"),
            ("Custom", "custom")
        ]
        
        for text, value in report_types:
            tk.Radiobutton(
                report_type_frame,
                text=text,
                variable=self.report_type_var,
                value=value,
                command=self.on_report_type_change,
                font=('Segoe UI', 9),
                bg='white',
                fg='#374151',
                selectcolor='white',
                activebackground='white'
            ).pack(side=tk.LEFT, padx=10)
        
        # Report display area with scrollbar
        report_frame = tk.LabelFrame(
            content_frame,
            text="Report Output",
            font=('Segoe UI', 14, 'bold'),
            bg='white',
            fg='#1a237e',
            relief=tk.FLAT,
            bd=0
        )
        report_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(report_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.report_text = tk.Text(
            report_frame,
            font=('Consolas', 10),
            bg='white',
            fg='#374151',
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
            yscrollcommand=scrollbar.set
        )
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        scrollbar.config(command=self.report_text.yview)
        
        # Action buttons frame
        button_frame = tk.Frame(content_frame, bg='#f5f7fa')
        button_frame.pack(fill=tk.X, pady=10)
        
        # Generate report button
        tk.Button(
            button_frame,
            text="🔄 Generate Report",
            command=self.generate_report,
            font=('Segoe UI', 11, 'bold'),
            bg='#3b82f6',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#2563eb'
        ).pack(side=tk.LEFT, padx=5)
        
        # Export buttons
        tk.Button(
            button_frame,
            text="📄 Export PDF",
            command=lambda: self.export_report('pdf'),
            font=('Segoe UI', 11, 'bold'),
            bg='#ef4444',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#dc2626'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="📊 Export CSV",
            command=lambda: self.export_report('csv'),
            font=('Segoe UI', 11, 'bold'),
            bg='#10b981',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#059669'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="📝 Export TXT",
            command=lambda: self.export_report('txt'),
            font=('Segoe UI', 11, 'bold'),
            bg='#f59e0b',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#d97706'
        ).pack(side=tk.LEFT, padx=5)
    
    def apply_filters(self):
        """Apply date filters"""
        try:
            if CALENDAR_AVAILABLE:
                # DateEntry returns a date object directly
                from_date_value = self.from_date_entry.get_date()
                to_date_value = self.to_date_entry.get_date()
                
                # Convert to date if it's a datetime
                if isinstance(from_date_value, datetime):
                    self.from_date = from_date_value.date()
                elif isinstance(from_date_value, date):
                    self.from_date = from_date_value
                else:
                    self.from_date = datetime.strptime(str(from_date_value), '%Y-%m-%d').date()
                
                if isinstance(to_date_value, datetime):
                    self.to_date = to_date_value.date()
                elif isinstance(to_date_value, date):
                    self.to_date = to_date_value
                else:
                    self.to_date = datetime.strptime(str(to_date_value), '%Y-%m-%d').date()
            else:
                # Text entry returns a string
                from_date_str = self.from_date_entry.get()
                to_date_str = self.to_date_entry.get()
                
                # Validate dates
                self.from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
                self.to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
            
            if self.from_date > self.to_date:
                messagebox.showerror("Error", "From date cannot be after To date")
                return
            
            self.generate_report()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
        except Exception as e:
            messagebox.showerror("Error", f"Error applying filters: {str(e)}")
    
    def reset_filters(self):
        """Reset filters to default"""
        default_from_date = datetime.now() - timedelta(days=30)
        default_to_date = datetime.now()
        
        if CALENDAR_AVAILABLE:
            # DateEntry uses set_date() method
            self.from_date_entry.set_date(default_from_date.date())
            self.to_date_entry.set_date(default_to_date.date())
        else:
            # Text entry uses delete and insert
            self.from_date_entry.delete(0, tk.END)
            self.from_date_entry.insert(0, default_from_date.strftime('%Y-%m-%d'))
            self.to_date_entry.delete(0, tk.END)
            self.to_date_entry.insert(0, default_to_date.strftime('%Y-%m-%d'))
        
        self.from_date = None
        self.to_date = None
        self.generate_report()
    
    def on_report_type_change(self):
        """Handle report type change"""
        self.generate_report()
    
    def generate_report(self):
        """Generate report based on selected type"""
        report_type = self.report_type_var.get()
        
        try:
            if report_type == "overview":
                self.generate_overview_report()
            elif report_type == "financial":
                self.generate_financial_report()
            elif report_type == "patient":
                self.generate_patient_report()
            elif report_type == "doctor":
                self.generate_doctor_report()
            elif report_type == "appointment":
                self.generate_appointment_report()
            elif report_type == "prescription":
                self.generate_prescription_report()
            elif report_type == "custom":
                self.generate_custom_report()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def get_date_filter(self):
        """Get date filter as date objects"""
        if self.from_date and self.to_date:
            # Ensure they are date objects, not strings
            if isinstance(self.from_date, str):
                from_date = datetime.strptime(self.from_date, '%Y-%m-%d').date()
            elif isinstance(self.from_date, datetime):
                from_date = self.from_date.date()
            else:
                from_date = self.from_date
            
            if isinstance(self.to_date, str):
                to_date = datetime.strptime(self.to_date, '%Y-%m-%d').date()
            elif isinstance(self.to_date, datetime):
                to_date = self.to_date.date()
            else:
                to_date = self.to_date
            
            return from_date, to_date
        return None, None
    
    def parse_date_safe(self, date_value):
        """Safely parse a date value that could be string, date, or None"""
        if date_value is None:
            return None
        if isinstance(date_value, datetime):
            return date_value.date()
        if isinstance(date_value, date):
            return date_value
        if isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                # Try other common formats
                try:
                    return datetime.strptime(date_value, '%Y/%m/%d').date()
                except (ValueError, TypeError):
                    return None
        return None
    
    def generate_overview_report(self):
        """Generate overview statistics report"""
        from_date, to_date = self.get_date_filter()
        
        # Always fetch all data first
        patients = self.db.get_all_patients()
        doctors = self.db.get_all_doctors()
        appointments = self.db.get_all_appointments()
        bills = self.db.get_all_bills()
        
        # Filter appointments and bills by date if needed
        if from_date and to_date:
            filtered_appointments = []
            for a in appointments:
                appt_date = self.parse_date_safe(a.get('appointment_date'))
                if appt_date and from_date <= appt_date <= to_date:
                    filtered_appointments.append(a)
            appointments = filtered_appointments
            
            filtered_bills = []
            for b in bills:
                bill_date = self.parse_date_safe(b.get('bill_date'))
                if bill_date and from_date <= bill_date <= to_date:
                    filtered_bills.append(b)
            bills = filtered_bills
            # get_date_range_statistics expects strings
            stats = self.db.get_date_range_statistics(from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d'))
            date_range_text = f"Date Range: {from_date} to {to_date}"
        else:
            stats = self.db.get_statistics()
            date_range_text = "All Time"
        
        total_appointments = len(appointments)
        pending_bills = sum(1 for b in bills if b['payment_status'] == 'Pending')
        paid_bills = sum(1 for b in bills if b['payment_status'] == 'Paid')
        total_bill_amount = sum(float(b.get('total_amount', 0)) for b in bills)
        paid_amount = sum(float(b.get('total_amount', 0)) for b in bills if b['payment_status'] == 'Paid')
        
        # Calculate demographics
        gender_dist = {}
        age_groups = {'0-18': 0, '19-35': 0, '36-50': 0, '51-65': 0, '65+': 0}
        
        for patient in patients:
            gender = patient.get('gender', 'Unknown')
            gender_dist[gender] = gender_dist.get(gender, 0) + 1
            
            try:
                dob = datetime.strptime(patient.get('date_of_birth', '2000-01-01'), '%Y-%m-%d')
                age = (datetime.now() - dob).days // 365
                if age <= 18:
                    age_groups['0-18'] += 1
                elif age <= 35:
                    age_groups['19-35'] += 1
                elif age <= 50:
                    age_groups['36-50'] += 1
                elif age <= 65:
                    age_groups['51-65'] += 1
                else:
                    age_groups['65+'] += 1
            except:
                pass
            
            report_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              HOSPITAL MANAGEMENT SYSTEM - OVERVIEW REPORT                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{date_range_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SYSTEM OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Patients:              {stats['total_patients']:>10}
  Total Doctors:                {stats['total_doctors']:>10}
  Total Appointments:           {total_appointments:>10}
  Scheduled Appointments:       {stats['scheduled_appointments']:>10}
  Completed Appointments:       {stats['completed_appointments']:>10}
  Cancelled Appointments:       {sum(1 for a in appointments if a.get('status') == 'Cancelled'):>10}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 FINANCIAL SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Revenue (Paid):         ${paid_amount:>20,.2f}
  Total Bills Generated:        {len(bills):>10}
  Paid Bills:                   {paid_bills:>10}
  Pending Bills:                {pending_bills:>10}
  Total Bill Amount:            ${total_bill_amount:>20,.2f}
  Average Bill Amount:          ${(total_bill_amount / max(1, len(bills))):>20,.2f}
  Collection Rate:              {(paid_amount / max(1, total_bill_amount) * 100):>19.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 PATIENT DEMOGRAPHICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Gender Distribution:
"""
        
        for gender, count in sorted(gender_dist.items()):
            percentage = (count / max(1, len(patients)) * 100)
            report_text += f"    {gender:20s} {count:>6} ({percentage:>5.1f}%)\n"
        
        report_text += f"""
  Age Group Distribution:
"""
        for age_group, count in age_groups.items():
            percentage = (count / max(1, len(patients)) * 100)
            report_text += f"    {age_group:20s} {count:>6} ({percentage:>5.1f}%)\n"
        
        report_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 PERFORMANCE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Appointment Completion Rate:  {(stats['completed_appointments'] / max(1, total_appointments) * 100):>19.1f}%
  Average Revenue per Bill:     ${(paid_amount / max(1, paid_bills)):>20,.2f}
  Patients per Doctor:          {(len(patients) / max(1, stats['total_doctors'])):>20.1f}
  Appointments per Patient:     {(total_appointments / max(1, len(patients))):>20.1f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

═══════════════════════════════════════════════════════════════════════════════
"""
        
        self.display_report(report_text)
    
    def generate_financial_report(self):
        """Generate detailed financial report"""
        from_date, to_date = self.get_date_filter()
        
        bills = self.db.get_all_bills()
        
        if from_date and to_date:
            filtered_bills = []
            for b in bills:
                bill_date = self.parse_date_safe(b.get('bill_date'))
                if bill_date and from_date <= bill_date <= to_date:
                    filtered_bills.append(b)
            bills = filtered_bills
            date_range_text = f"Date Range: {from_date} to {to_date}"
        else:
            date_range_text = "All Time"
        
        paid_bills = [b for b in bills if b['payment_status'] == 'Paid']
        pending_bills = [b for b in bills if b['payment_status'] == 'Pending']
        
        total_revenue = sum(float(b.get('total_amount', 0)) for b in paid_bills)
        total_pending = sum(float(b.get('total_amount', 0)) for b in pending_bills)
        total_amount = sum(float(b.get('total_amount', 0)) for b in bills)
        
        # Daily revenue breakdown
        daily_revenue = {}
        for bill in paid_bills:
            date = bill.get('bill_date', 'Unknown')
            amount = float(bill.get('total_amount', 0))
            daily_revenue[date] = daily_revenue.get(date, 0) + amount
        
        # Payment method breakdown
        payment_methods = {}
        for bill in bills:
            method = bill.get('payment_method', 'Unknown')
            payment_methods[method] = payment_methods.get(method, 0) + 1
        
        report_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              HOSPITAL MANAGEMENT SYSTEM - FINANCIAL REPORT                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{date_range_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 FINANCIAL SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Revenue (Paid):         ${total_revenue:>20,.2f}
  Pending Amount:               ${total_pending:>20,.2f}
  Total Bill Amount:            ${total_amount:>20,.2f}
  Total Bills:                  {len(bills):>10}
  Paid Bills:                   {len(paid_bills):>10}
  Pending Bills:                {len(pending_bills):>10}
  Collection Rate:              {(total_revenue / max(1, total_amount) * 100):>19.1f}%
  Average Bill Amount:          ${(total_amount / max(1, len(bills))):>20,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 DAILY REVENUE BREAKDOWN (Top 10 Days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        sorted_daily = sorted(daily_revenue.items(), key=lambda x: x[1], reverse=True)[:10]
        for date, amount in sorted_daily:
            report_text += f"  {date:15s} ${amount:>15,.2f}\n"
        
        report_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💳 PAYMENT METHOD DISTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for method, count in sorted(payment_methods.items()):
            percentage = (count / max(1, len(bills)) * 100)
            report_text += f"  {method:20s} {count:>6} ({percentage:>5.1f}%)\n"
        
        report_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 PENDING BILLS SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        if pending_bills:
            report_text += "  Bill ID          Patient Name              Amount      Date\n"
            report_text += "  " + "-" * 70 + "\n"
            for bill in pending_bills[:20]:  # Show top 20
                patient_name = bill.get('patient_name', 'Unknown')
                bill_id = bill.get('bill_id', 'N/A')
                amount = float(bill.get('total_amount', 0))
                date = bill.get('bill_date', 'N/A')
                report_text += f"  {bill_id:15s} {patient_name[:25]:25s} ${amount:>10,.2f}  {date}\n"
            if len(pending_bills) > 20:
                report_text += f"\n  ... and {len(pending_bills) - 20} more pending bills\n"
        else:
            report_text += "  No pending bills\n"
        
        report_text += "\n" + "═" * 75 + "\n"
        
        self.display_report(report_text)
    
    def generate_patient_report(self):
        """Generate patient statistics report"""
        from_date, to_date = self.get_date_filter()
        
        patients = self.db.get_all_patients()
        appointments = self.db.get_all_appointments()
        prescriptions = self.db.get_all_prescriptions()
        
        if from_date and to_date:
            filtered_appointments = []
            for a in appointments:
                appt_date = self.parse_date_safe(a.get('appointment_date'))
                if appt_date and from_date <= appt_date <= to_date:
                    filtered_appointments.append(a)
            appointments = filtered_appointments
            
            filtered_prescriptions = []
            for p in prescriptions:
                presc_date = self.parse_date_safe(p.get('prescription_date'))
                if presc_date and from_date <= presc_date <= to_date:
                    filtered_prescriptions.append(p)
            prescriptions = filtered_prescriptions
            date_range_text = f"Date Range: {from_date} to {to_date}"
        else:
            date_range_text = "All Time"
        
        # Patient statistics
        gender_dist = {}
        age_groups = {'0-18': 0, '19-35': 0, '36-50': 0, '51-65': 0, '65+': 0}
        blood_group_dist = {}
        
        # Patient visit frequency
        patient_visits = {}
        for appointment in appointments:
            patient_id = appointment.get('patient_id')
            if patient_id:
                patient_visits[patient_id] = patient_visits.get(patient_id, 0) + 1
        
        for patient in patients:
            gender = patient.get('gender', 'Unknown')
            gender_dist[gender] = gender_dist.get(gender, 0) + 1
            
            blood_group = patient.get('blood_group', 'Unknown')
            if blood_group:
                blood_group_dist[blood_group] = blood_group_dist.get(blood_group, 0) + 1
            
            try:
                dob = datetime.strptime(patient.get('date_of_birth', '2000-01-01'), '%Y-%m-%d')
                age = (datetime.now() - dob).days // 365
                if age <= 18:
                    age_groups['0-18'] += 1
                elif age <= 35:
                    age_groups['19-35'] += 1
                elif age <= 50:
                    age_groups['36-50'] += 1
                elif age <= 65:
                    age_groups['51-65'] += 1
                else:
                    age_groups['65+'] += 1
            except:
                pass
        
        # Most frequent patients
        top_patients = sorted(patient_visits.items(), key=lambda x: x[1], reverse=True)[:10]
        
        report_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              HOSPITAL MANAGEMENT SYSTEM - PATIENT REPORT                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{date_range_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 PATIENT STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Patients:                {len(patients):>10}
  Total Appointments:            {len(appointments):>10}
  Total Prescriptions:           {len(prescriptions):>10}
  Average Appointments/Patient:  {(len(appointments) / max(1, len(patients))):>20.1f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 GENDER DISTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for gender, count in sorted(gender_dist.items()):
            percentage = (count / max(1, len(patients)) * 100)
            report_text += f"  {gender:20s} {count:>6} ({percentage:>5.1f}%)\n"
        
        report_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎂 AGE GROUP DISTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for age_group, count in age_groups.items():
            percentage = (count / max(1, len(patients)) * 100)
            report_text += f"  {age_group:20s} {count:>6} ({percentage:>5.1f}%)\n"
        
        if blood_group_dist:
            report_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🩸 BLOOD GROUP DISTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for bg, count in sorted(blood_group_dist.items()):
                percentage = (count / max(1, len(patients)) * 100)
                report_text += f"  {bg:20s} {count:>6} ({percentage:>5.1f}%)\n"
        
        if top_patients:
            report_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ MOST FREQUENT PATIENTS (Top 10)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Patient ID         Visits
"""
            for patient_id, visits in top_patients:
                patient = next((p for p in patients if p.get('patient_id') == patient_id), None)
                name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}" if patient else patient_id
                report_text += f"  {patient_id:15s} {visits:>6}\n"
        
        report_text += "\n" + "═" * 75 + "\n"
        
        self.display_report(report_text)
    
    def generate_doctor_report(self):
        """Generate doctor performance report"""
        from_date, to_date = self.get_date_filter()
        
        doctors = self.db.get_all_doctors()
        appointments = self.db.get_all_appointments()
        
        if from_date and to_date:
            filtered_appointments = []
            for a in appointments:
                appt_date = self.parse_date_safe(a.get('appointment_date'))
                if appt_date and from_date <= appt_date <= to_date:
                    filtered_appointments.append(a)
            appointments = filtered_appointments
            date_range_text = f"Date Range: {from_date} to {to_date}"
        else:
            date_range_text = "All Time"
        
        # Doctor statistics
        doctor_stats = {}
        specialization_dist = {}
        
        for doctor in doctors:
            doctor_id = doctor.get('doctor_id')
            specialization = doctor.get('specialization', 'Unknown')
            specialization_dist[specialization] = specialization_dist.get(specialization, 0) + 1
            
            doctor_appointments = [a for a in appointments if a.get('doctor_id') == doctor_id]
            completed = sum(1 for a in doctor_appointments if a.get('status') == 'Completed')
            
            doctor_stats[doctor_id] = {
                'name': f"{doctor.get('first_name', '')} {doctor.get('last_name', '')}",
                'specialization': specialization,
                'total': len(doctor_appointments),
                'completed': completed,
                'scheduled': sum(1 for a in doctor_appointments if a.get('status') == 'Scheduled'),
                'cancelled': sum(1 for a in doctor_appointments if a.get('status') == 'Cancelled')
            }
        
        # Sort by total appointments
        sorted_doctors = sorted(doctor_stats.items(), key=lambda x: x[1]['total'], reverse=True)
        
        report_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          HOSPITAL MANAGEMENT SYSTEM - DOCTOR PERFORMANCE REPORT              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{date_range_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👨‍⚕️ DOCTOR PERFORMANCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Doctors:                 {len(doctors):>10}
  Total Appointments:             {len(appointments):>10}
  Average Appointments/Doctor:    {(len(appointments) / max(1, len(doctors))):>20.1f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏥 SPECIALIZATION DISTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for spec, count in sorted(specialization_dist.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / max(1, len(doctors)) * 100)
            report_text += f"  {spec:30s} {count:>6} ({percentage:>5.1f}%)\n"
        
        report_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 INDIVIDUAL DOCTOR PERFORMANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Doctor Name                    Specialization          Total  Completed  Scheduled  Cancelled  Rate
"""
        
        for doctor_id, stats in sorted_doctors:
            completion_rate = (stats['completed'] / max(1, stats['total']) * 100)
            name = stats['name'][:28]
            spec = stats['specialization'][:22]
            report_text += f"  {name:28s} {spec:22s} {stats['total']:>5}  {stats['completed']:>9}  {stats['scheduled']:>9}  {stats['cancelled']:>9}  {completion_rate:>5.1f}%\n"
        
        report_text += "\n" + "═" * 75 + "\n"
        
        self.display_report(report_text)
    
    def generate_appointment_report(self):
        """Generate appointment statistics report"""
        from_date, to_date = self.get_date_filter()
        
        appointments = self.db.get_all_appointments()
        
        if from_date and to_date:
            filtered_appointments = []
            for a in appointments:
                appt_date = self.parse_date_safe(a.get('appointment_date'))
                if appt_date and from_date <= appt_date <= to_date:
                    filtered_appointments.append(a)
            appointments = filtered_appointments
            date_range_text = f"Date Range: {from_date} to {to_date}"
        else:
            date_range_text = "All Time"
        
        # Status breakdown
        status_dist = {}
        daily_appointments = {}
        
        for appointment in appointments:
            status = appointment.get('status', 'Unknown')
            status_dist[status] = status_dist.get(status, 0) + 1
            
            date = appointment.get('appointment_date', 'Unknown')
            daily_appointments[date] = daily_appointments.get(date, 0) + 1
        
        # Top 10 busiest days
        sorted_daily = sorted(daily_appointments.items(), key=lambda x: x[1], reverse=True)[:10]
        
        report_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           HOSPITAL MANAGEMENT SYSTEM - APPOINTMENT REPORT                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{date_range_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 APPOINTMENT STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Appointments:            {len(appointments):>10}
  Average Appointments/Day:      {(len(appointments) / max(1, len(set(a.get('appointment_date') for a in appointments)))):>20.1f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 STATUS DISTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for status, count in sorted(status_dist.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / max(1, len(appointments)) * 100)
            report_text += f"  {status:20s} {count:>6} ({percentage:>5.1f}%)\n"
        
        if sorted_daily:
            report_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 BUSIEST DAYS (Top 10)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Date              Appointments
"""
            for date, count in sorted_daily:
                report_text += f"  {date:15s} {count:>6}\n"
        
        report_text += "\n" + "═" * 75 + "\n"
        
        self.display_report(report_text)
    
    def generate_prescription_report(self):
        """Generate prescription statistics report"""
        from_date, to_date = self.get_date_filter()
        
        prescriptions = self.db.get_all_prescriptions()
        
        if from_date and to_date:
            filtered_prescriptions = []
            for p in prescriptions:
                presc_date = self.parse_date_safe(p.get('prescription_date'))
                if presc_date and from_date <= presc_date <= to_date:
                    filtered_prescriptions.append(p)
            prescriptions = filtered_prescriptions
            date_range_text = f"Date Range: {from_date} to {to_date}"
        else:
            date_range_text = "All Time"
        
        # Medicine usage statistics
        medicine_usage = {}
        daily_prescriptions = {}
        
        for prescription in prescriptions:
            date = prescription.get('prescription_date', 'Unknown')
            daily_prescriptions[date] = daily_prescriptions.get(date, 0) + 1
            
            # Get prescription items
            prescription_id = prescription.get('prescription_id')
            if prescription_id:
                items = self.db.get_prescription_items(prescription_id)
                for item in items:
                    medicine = item.get('medicine_name', 'Unknown')
                    medicine_usage[medicine] = medicine_usage.get(medicine, 0) + 1
        
        # Top prescribed medicines
        sorted_medicines = sorted(medicine_usage.items(), key=lambda x: x[1], reverse=True)[:20]
        
        report_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          HOSPITAL MANAGEMENT SYSTEM - PRESCRIPTION REPORT                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{date_range_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💊 PRESCRIPTION STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Prescriptions:           {len(prescriptions):>10}
  Unique Medicines Prescribed:   {len(medicine_usage):>10}
  Average Prescriptions/Day:     {(len(prescriptions) / max(1, len(daily_prescriptions))):>20.1f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 MOST PRESCRIBED MEDICINES (Top 20)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Medicine Name                              Count
"""
        
        for medicine, count in sorted_medicines:
            report_text += f"  {medicine[:40]:40s} {count:>6}\n"
        
        report_text += "\n" + "═" * 75 + "\n"
        
        self.display_report(report_text)
    
    def generate_custom_report(self):
        """Generate custom comprehensive report"""
        from_date, to_date = self.get_date_filter()
        
        if from_date and to_date:
            # get_date_range_statistics expects strings
            stats = self.db.get_date_range_statistics(from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d'))
            date_range_text = f"Date Range: {from_date} to {to_date}"
        else:
            stats = self.db.get_statistics()
            date_range_text = "All Time"
        
        patients = self.db.get_all_patients()
        doctors = self.db.get_all_doctors()
        appointments = self.db.get_all_appointments()
        bills = self.db.get_all_bills()
        prescriptions = self.db.get_all_prescriptions()
        
        # Filter by date if needed
        if from_date and to_date:
            filtered_appointments = []
            for a in appointments:
                appt_date = self.parse_date_safe(a.get('appointment_date'))
                if appt_date and from_date <= appt_date <= to_date:
                    filtered_appointments.append(a)
            appointments = filtered_appointments
            
            filtered_bills = []
            for b in bills:
                bill_date = self.parse_date_safe(b.get('bill_date'))
                if bill_date and from_date <= bill_date <= to_date:
                    filtered_bills.append(b)
            bills = filtered_bills
            
            filtered_prescriptions = []
            for p in prescriptions:
                presc_date = self.parse_date_safe(p.get('prescription_date'))
                if presc_date and from_date <= presc_date <= to_date:
                    filtered_prescriptions.append(p)
            prescriptions = filtered_prescriptions
        
        paid_bills = [b for b in bills if b['payment_status'] == 'Paid']
        total_revenue = sum(float(b.get('total_amount', 0)) for b in paid_bills)
        
        report_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         HOSPITAL MANAGEMENT SYSTEM - COMPREHENSIVE CUSTOM REPORT             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{date_range_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Patients:                {len(patients):>10}
  Total Doctors:                 {len(doctors):>10}
  Total Appointments:            {len(appointments):>10}
  Total Prescriptions:           {len(prescriptions):>10}
  Total Bills:                   {len(bills):>10}
  Total Revenue:                 ${total_revenue:>20,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This comprehensive report combines all aspects of the hospital management system
including patient demographics, financial performance, doctor productivity, and
operational metrics for the selected time period.

═══════════════════════════════════════════════════════════════════════════════
"""
        
        self.display_report(report_text)
    
    def display_report(self, text: str):
        """Display report in text widget"""
        self.report_text.config(state='normal')
        self.report_text.delete('1.0', tk.END)
        self.report_text.insert('1.0', text)
        self.report_text.config(state='disabled')
        self.current_report_text = text
    
    def export_report(self, format_type: str):
        """Export report to file"""
        if not hasattr(self, 'current_report_text'):
            messagebox.showwarning("Warning", "Please generate a report first")
            return
        
        try:
            report_type = self.report_type_var.get()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"hospital_report_{report_type}_{timestamp}"
            
            if format_type == 'pdf':
                if not REPORTLAB_AVAILABLE:
                    messagebox.showerror("Error", "PDF export requires reportlab library.\nPlease install it: pip install reportlab")
                    return
                
                filename = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=default_filename
                )
                if filename:
                    self.export_to_pdf(filename)
                    messagebox.showinfo("Success", f"Report exported to PDF:\n{filename}")
            
            elif format_type == 'csv':
                filename = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv")],
                    initialfile=default_filename
                )
                if filename:
                    self.export_to_csv(filename)
                    messagebox.showinfo("Success", f"Report exported to CSV:\n{filename}")
            
            elif format_type == 'txt':
                filename = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt")],
                    initialfile=default_filename
                )
                if filename:
                    self.export_to_txt(filename)
                    messagebox.showinfo("Success", f"Report exported to TXT:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")
    
    def export_to_pdf(self, filename: str):
        """Export report to PDF"""
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Add title
        title = Paragraph("Hospital Management System - Report", title_style)
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Convert text to paragraphs
        lines = self.current_report_text.split('\n')
        for line in lines:
            if line.strip():
                # Format headers
                if line.strip().startswith('║') or line.strip().startswith('╔') or line.strip().startswith('╚'):
                    p = Paragraph(line.replace('║', '').replace('╔', '').replace('╚', '').replace('═', '').strip(), 
                                 styles['Heading2'])
                elif line.strip().startswith('━━'):
                    p = Paragraph(line.replace('━', '-').strip(), styles['Heading3'])
                else:
                    p = Paragraph(line, styles['Normal'])
                story.append(p)
            else:
                story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
    
    def export_to_csv(self, filename: str):
        """Export report data to CSV"""
        report_type = self.report_type_var.get()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Hospital Management System - Report'])
            writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow(['Report Type:', report_type])
            writer.writerow([])
            
            # Export data based on report type
            if report_type == 'financial':
                bills = self.db.get_all_bills()
                writer.writerow(['Bill ID', 'Patient Name', 'Amount', 'Status', 'Date'])
                for bill in bills:
                    writer.writerow([
                        bill.get('bill_id', ''),
                        bill.get('patient_name', ''),
                        bill.get('total_amount', ''),
                        bill.get('payment_status', ''),
                        bill.get('bill_date', '')
                    ])
            elif report_type == 'patient':
                patients = self.db.get_all_patients()
                writer.writerow(['Patient ID', 'Name', 'Gender', 'Date of Birth', 'Phone', 'Email'])
                for patient in patients:
                    writer.writerow([
                        patient.get('patient_id', ''),
                        f"{patient.get('first_name', '')} {patient.get('last_name', '')}",
                        patient.get('gender', ''),
                        patient.get('date_of_birth', ''),
                        patient.get('phone', ''),
                        patient.get('email', '')
                    ])
            elif report_type == 'doctor':
                doctors = self.db.get_all_doctors()
                writer.writerow(['Doctor ID', 'Name', 'Specialization', 'Phone', 'Email'])
                for doctor in doctors:
                    writer.writerow([
                        doctor.get('doctor_id', ''),
                        f"{doctor.get('first_name', '')} {doctor.get('last_name', '')}",
                        doctor.get('specialization', ''),
                        doctor.get('phone', ''),
                        doctor.get('email', '')
                    ])
            elif report_type == 'appointment':
                appointments = self.db.get_all_appointments()
                writer.writerow(['Appointment ID', 'Patient', 'Doctor', 'Date', 'Time', 'Status'])
                for appointment in appointments:
                    writer.writerow([
                        appointment.get('appointment_id', ''),
                        appointment.get('patient_name', ''),
                        appointment.get('doctor_name', ''),
                        appointment.get('appointment_date', ''),
                        appointment.get('appointment_time', ''),
                        appointment.get('status', '')
                    ])
    
    def export_to_txt(self, filename: str):
        """Export report to plain text file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.current_report_text)
    
    def load_statistics(self):
        """Load and display default overview statistics"""
        self.generate_overview_report()
