"""
Reports and Analytics Module
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database


class ReportsModule:
    """Reports and analytics interface"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        
        self.create_ui()
        # Defer statistics loading to make UI appear faster
        self.parent.after(10, self.load_statistics)
    
    def create_ui(self):
        """Create user interface"""
        # Header
        header = tk.Label(
            self.parent,
            text="Reports & Analytics",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        header.pack(pady=10)
        
        # Main content frame
        content_frame = tk.Frame(self.parent, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Statistics section
        stats_frame = tk.LabelFrame(
            content_frame,
            text="System Statistics",
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.stats_text = tk.Text(
            stats_frame,
            font=('Arial', 12),
            bg='white',
            fg='#2c3e50',
            wrap=tk.WORD,
            height=15
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons frame
        button_frame = tk.Frame(content_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            button_frame,
            text="Refresh Statistics",
            command=self.load_statistics,
            font=('Arial', 11),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Export Report",
            command=self.export_report,
            font=('Arial', 11),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="View Patient Reports",
            command=self.view_patient_reports,
            font=('Arial', 11),
            bg='#f39c12',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
    
    def load_statistics(self):
        """Load and display statistics"""
        try:
            stats = self.db.get_statistics()
            
            # Get additional data
            patients = self.db.get_all_patients()
            doctors = self.db.get_all_doctors()
            appointments = self.db.get_all_appointments()
            bills = self.db.get_all_bills()
            
            # Calculate additional stats
            total_appointments = len(appointments)
            pending_bills = sum(1 for b in bills if b['payment_status'] == 'Pending')
            paid_bills = sum(1 for b in bills if b['payment_status'] == 'Paid')
            
            report_text = f"""
╔══════════════════════════════════════════════════════════════╗
║           HOSPITAL MANAGEMENT SYSTEM - STATISTICS            ║
╚══════════════════════════════════════════════════════════════╝

📊 OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Patients:          {stats['total_patients']:>10}
  Total Doctors:          {stats['total_doctors']:>10}
  Total Appointments:     {total_appointments:>10}
  Scheduled Appointments: {stats['scheduled_appointments']:>10}
  Completed Appointments: {stats['completed_appointments']:>10}

💰 FINANCIAL SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Revenue:          ${stats['total_revenue']:>15,.2f}
  Total Bills:            {len(bills):>10}
  Paid Bills:             {paid_bills:>10}
  Pending Bills:          {pending_bills:>10}

📋 RECENT ACTIVITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Recent Patients:        {min(5, len(patients)):>10} (last 5)
  Active Doctors:         {len(doctors):>10}

📈 PERFORMANCE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Completion Rate:        {(stats['completed_appointments'] / max(1, total_appointments) * 100):>9.1f}%
  Average Revenue/Bill:   ${(stats['total_revenue'] / max(1, paid_bills)):>13,.2f}

═══════════════════════════════════════════════════════════════════

Note: All data is stored locally. This is an offline system.
            """
            
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert('1.0', report_text)
            self.stats_text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load statistics: {str(e)}")
    
    def export_report(self):
        """Export report to file"""
        messagebox.showinfo("Export", "Export functionality would save report to a file")
    
    def view_patient_reports(self):
        """View detailed patient reports"""
        messagebox.showinfo("Patient Reports", "Patient reports view would show detailed patient history")

