"""
Billing Management Module
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database
from utils import generate_id, get_current_date
import tempfile
import os
import subprocess
import platform


class BillingModule:
    """Billing management interface"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        
        self.create_ui()
        # Defer refresh to make UI appear faster
        self.parent.after(10, self.refresh_list)
    
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
        
        # List frame
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
        
        # Action buttons with modern styling
        action_frame = tk.Frame(self.parent, bg='#f5f7fa')
        action_frame.pack(fill=tk.X, padx=25, pady=15)
        
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
            text="✏️ Edit",
            command=self.edit_bill,
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
        
        tk.Button(
            action_frame,
            text="🗑️ Delete",
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
        """Refresh bill list"""
        self.tree.delete(*self.tree.get_children())
        
        bills = self.db.get_all_bills()
        for bill in bills:
            self.tree.insert('', tk.END, values=(
                bill['bill_id'],
                bill.get('patient_name', ''),
                bill['bill_date'],
                f"${bill['total_amount']:.2f}",
                bill['payment_status']
            ))
    
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
        """View bill details"""
        bill_id = self.get_selected_bill_id()
        if not bill_id:
            return
        
        bill = self.db.get_bill_by_id(bill_id)
        if not bill:
            messagebox.showerror("Error", "Bill not found")
            return
        
        # Get patient details
        patient = self.db.get_patient_by_id(bill['patient_id'])
        patient_name = bill.get('patient_name', '')
        if not patient_name and patient:
            patient_name = f"{patient['first_name']} {patient['last_name']}"
        
        # Show bill details in a dialog
        details_text = f"""
Bill ID: {bill['bill_id']}
Date: {bill['bill_date']}

Patient Information:
  Name: {patient_name}
  Patient ID: {bill['patient_id']}
"""
        if patient:
            if patient.get('phone'):
                details_text += f"  Phone: {patient['phone']}\n"
            if patient.get('email'):
                details_text += f"  Email: {patient['email']}\n"

        details_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHARGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Consultation Fee:      ${bill.get('consultation_fee', 0):>15,.2f}
Medicine Cost:         ${bill.get('medicine_cost', 0):>15,.2f}
Other Charges:         ${bill.get('other_charges', 0):>15,.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL AMOUNT:          ${bill['total_amount']:>15,.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Payment Status: {bill.get('payment_status', 'Pending')}
Payment Method: {bill.get('payment_method', 'N/A')}
"""
        
        if bill.get('notes'):
            details_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Notes:
{bill['notes']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        self._show_print_dialog(details_text, f"Bill Details - {bill_id}")
    
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
    
    def edit_bill(self):
        """Edit existing bill"""
        bill_id = self.get_selected_bill_id()
        if not bill_id:
            return
        
        bill = self.db.get_bill_by_id(bill_id)
        if not bill:
            messagebox.showerror("Error", "Bill not found")
            return
        
        # Open edit dialog with existing data
        self.bill_dialog(bill_id=bill_id, bill_data=bill)
    
    def delete_bill(self):
        """Delete a bill"""
        bill_id = self.get_selected_bill_id()
        if not bill_id:
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete bill {bill_id}?\n\nThis action cannot be undone.",
            icon='warning'
        )
        
        if result:
            if self.db.delete_bill(bill_id):
                messagebox.showinfo("Success", f"Bill {bill_id} deleted successfully")
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Failed to delete bill")
    
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
    
    def bill_dialog(self, bill_id=None, bill_data=None):
        """Bill form dialog - for adding new or editing existing bill"""
        is_edit = bill_id is not None
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Bill" if is_edit else "New Bill")
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
        
        # Button frame - pack first to ensure it's at the bottom
        button_frame = tk.Frame(dialog, bg='#f5f7fa', relief=tk.FLAT, bd=0)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)
        
        main_frame = tk.Frame(dialog, bg='#f5f7fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
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
        
        patient_combo = ttk.Combobox(
            form_frame, 
            textvariable=patient_var,
            values=patient_options,
            font=('Arial', 10),
            width=37,
            state='normal'  # 'normal' allows typing to search
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
        date_entry = tk.Entry(form_frame, font=('Arial', 10), width=40)
        if is_edit and bill_data:
            date_entry.insert(0, bill_data.get('bill_date', get_current_date()))
        else:
            date_entry.insert(0, get_current_date())
        date_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Consultation Fee:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        consultation_entry = tk.Entry(form_frame, font=('Arial', 10), width=40)
        if is_edit and bill_data:
            consultation_entry.insert(0, str(bill_data.get('consultation_fee', 0)))
        else:
            consultation_entry.insert(0, "0")
        consultation_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Medicine Cost:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        medicine_entry = tk.Entry(form_frame, font=('Arial', 10), width=40)
        if is_edit and bill_data:
            medicine_entry.insert(0, str(bill_data.get('medicine_cost', 0)))
        else:
            medicine_entry.insert(0, "0")
        medicine_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Other Charges:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        other_entry = tk.Entry(form_frame, font=('Arial', 10), width=40)
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
        status_combo = ttk.Combobox(form_frame, textvariable=status_var, values=['Pending', 'Paid', 'Partial'], width=37)
        if is_edit and bill_data:
            status_var.set(bill_data.get('payment_status', 'Pending'))
        else:
            status_var.set('Pending')
        status_combo.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Payment Method:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        payment_var = tk.StringVar()
        payment_combo = ttk.Combobox(form_frame, textvariable=payment_var, values=['Cash', 'Card', 'Online', 'Insurance'], width=37)
        if is_edit and bill_data:
            payment_var.set(bill_data.get('payment_method', ''))
        payment_combo.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Notes:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        notes_text = tk.Text(form_frame, font=('Arial', 10), width=37, height=3)
        if is_edit and bill_data:
            notes_text.insert('1.0', bill_data.get('notes', ''))
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
