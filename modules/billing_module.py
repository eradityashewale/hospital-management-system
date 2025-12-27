"""
Billing Management Module
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import generate_id, get_current_date


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
        # Header
        header = tk.Label(
            self.parent,
            text="Billing Management",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        header.pack(pady=10)
        
        # Top frame
        top_frame = tk.Frame(self.parent, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add bill button
        add_btn = tk.Button(
            top_frame,
            text="+ New Bill",
            command=self.add_bill,
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        add_btn.pack(side=tk.RIGHT, padx=10)
        
        # List frame
        list_frame = tk.Frame(self.parent, bg='#f0f0f0')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ('Bill ID', 'Patient', 'Date', 'Total Amount', 'Status')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure style for better visibility
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 10), rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<Double-1>', self.view_bill)
        
        # Action buttons
        action_frame = tk.Frame(self.parent, bg='#f0f0f0')
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(
            action_frame,
            text="View Details",
            command=self.view_bill,
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="Mark Paid",
            command=self.mark_paid,
            font=('Arial', 10),
            bg='#2ecc71',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
    
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
        messagebox.showinfo("Bill", f"View details for {bill_id}")
    
    def mark_paid(self):
        """Mark bill as paid"""
        bill_id = self.get_selected_bill_id()
        if not bill_id:
            return
        messagebox.showinfo("Info", "Mark paid functionality would update payment status")
        self.refresh_list()
    
    def bill_dialog(self):
        """Bill form dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("New Bill")
        dialog.geometry("500x500")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.parent)
        dialog.grab_set()
        
        main_frame = tk.Frame(dialog, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        bill_id = generate_id('BILL')
        tk.Label(main_frame, text=f"Bill ID: {bill_id}", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=5)
        
        # Form fields
        form_frame = tk.Frame(main_frame, bg='#f0f0f0')
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(form_frame, text="Patient ID *:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        patient_entry = tk.Entry(form_frame, font=('Arial', 10), width=40)
        patient_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Date:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        date_entry = tk.Entry(form_frame, font=('Arial', 10), width=40)
        date_entry.insert(0, get_current_date())
        date_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Consultation Fee:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        consultation_entry = tk.Entry(form_frame, font=('Arial', 10), width=40)
        consultation_entry.insert(0, "0")
        consultation_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Medicine Cost:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        medicine_entry = tk.Entry(form_frame, font=('Arial', 10), width=40)
        medicine_entry.insert(0, "0")
        medicine_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Other Charges:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        other_entry = tk.Entry(form_frame, font=('Arial', 10), width=40)
        other_entry.insert(0, "0")
        other_entry.pack(fill=tk.X, pady=5)
        
        # Total display
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
        
        tk.Label(form_frame, text="Payment Method:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=5)
        payment_var = tk.StringVar()
        payment_combo = ttk.Combobox(form_frame, textvariable=payment_var, values=['Cash', 'Card', 'Online', 'Insurance'], width=37)
        payment_combo.pack(fill=tk.X, pady=5)
        
        def save_bill():
            if not patient_entry.get():
                messagebox.showerror("Error", "Patient ID is required")
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
                'bill_id': bill_id,
                'patient_id': patient_entry.get(),
                'bill_date': date_entry.get() or get_current_date(),
                'consultation_fee': consultation,
                'medicine_cost': medicine,
                'other_charges': other,
                'total_amount': total,
                'payment_status': 'Paid' if payment_var.get() else 'Pending',
                'payment_method': payment_var.get() or '',
                'notes': ''
            }
            
            if self.db.add_bill(data):
                messagebox.showinfo("Success", "Bill created successfully")
                dialog.destroy()
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Failed to create bill")
        
        button_frame = tk.Frame(dialog, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(
            button_frame,
            text="Save Bill",
            command=save_bill,
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=30,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="Close",
            command=dialog.destroy,
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            padx=30,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)

