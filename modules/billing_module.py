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
            fg='black',
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
        dialog.geometry("500x600")  # Increased height to ensure buttons are visible
        dialog.configure(bg='#f0f0f0')
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
        button_frame = tk.Frame(dialog, bg='#f0f0f0', relief=tk.RAISED, bd=2)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)
        
        main_frame = tk.Frame(dialog, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        bill_id = generate_id('BILL')
        tk.Label(main_frame, text=f"Bill ID: {bill_id}", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=5)
        
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
                'bill_id': bill_id,
                'patient_id': patient_id,
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
        inner_button_frame = tk.Frame(button_frame, bg='#f0f0f0')
        inner_button_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Button(
            inner_button_frame,
            text="Save",
            command=save_bill,
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='black',
            padx=30,
            pady=8,
            cursor='hand2',
            relief=tk.RAISED,
            bd=2,
            activebackground='#229954',
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
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            padx=30,
            pady=8,
            cursor='hand2',
            relief=tk.RAISED,
            bd=2
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
