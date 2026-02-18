"""
Patient Management Module
"""
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Backend imports
from backend.database import Database

# Frontend theme
from frontend.theme import (
    BG_BASE, BG_CARD, BG_DEEP, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_BLUE, BORDER_DEFAULT, WARNING, ERROR, SUCCESS, ACCENT_PURPLE, ACCENT_TEAL,
    TABLE_HEADER_BG, BTN_SUCCESS_BG, BTN_SUCCESS_HOVER, BTN_PRIMARY_BG, BTN_PRIMARY_HOVER,
    BTN_DANGER_BG, BTN_DANGER_HOVER, BTN_SECONDARY_BG, BTN_SECONDARY_HOVER,
    FONT_UI, get_theme,
)

# Utils imports
from utils.helpers import generate_id, get_current_date
from utils.logger import (log_button_click, log_dialog_open, log_dialog_close,
                   log_database_operation, log_error, log_info, log_warning, log_debug)
from utils.xray_storage import save_xray_file, delete_xray_file

# IPD Admissions / Daily Notes
from frontend.modules.admission_module import AdmissionNotesWindow

# Patient documents PDF (bill, prescription, IPD report)
from utils.patient_docs_pdf import print_all_patient_documents


def _open_file_with_default(path):
    """Open file with the system default application."""
    if not path or not os.path.isfile(path):
        return
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception as e:
        log_error("Failed to open file", e)
        messagebox.showerror("Error", f"Could not open file: {e}")


class XRayReportsWindow:
    """Toplevel window to manage X-ray reports for a patient."""

    BODY_PARTS = ("Chest", "Spine", "Abdomen", "Skull", "Extremity", "Other")

    def __init__(self, parent, db: Database, patient_id: str):
        self.parent = parent
        self.db = db
        self.patient_id = patient_id
        self.patient = self.db.get_patient_by_id(patient_id)
        if not self.patient:
            messagebox.showerror("Error", "Patient not found")
            return
        t = get_theme()
        self.window = tk.Toplevel(parent)
        self.window.title("X-Ray Reports")
        self.window.configure(bg=t["BG_DEEP"])
        self.window.transient(parent)
        self.window.geometry("720x420")
        self.window.lift()
        self.window.focus_force()
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        t = get_theme()
        header = tk.Label(
            self.window,
            text=f"X-Ray Reports — {self.patient.get('first_name', '')} {self.patient.get('last_name', '')} ({self.patient_id})",
            font=(FONT_UI, 16, "bold"),
            bg=t["BG_DEEP"],
            fg=t["TEXT_PRIMARY"],
        )
        header.pack(pady=12)

        list_frame = tk.Frame(self.window, bg=t["BG_DEEP"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        cols = ("report_id", "report_date", "body_part", "file_name")
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(
            "Treeview",
            font=(FONT_UI, 10),
            rowheight=26,
            background=t["BG_CARD"],
            foreground=t["TEXT_PRIMARY"],
            fieldbackground=t["BG_CARD"],
        )
        style.configure(
            "Treeview.Heading",
            font=(FONT_UI, 10, "bold"),
            background=t["TABLE_HEADER_BG"],
            foreground=t["TEXT_PRIMARY"],
        )
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=10)
        self.tree.heading("report_date", text="Date")
        self.tree.heading("body_part", text="Body Part")
        self.tree.heading("file_name", text="File")
        self.tree.column("report_date", width=120)
        self.tree.column("body_part", width=120)
        self.tree.column("file_name", width=380)
        self.tree["displaycolumns"] = ("report_date", "body_part", "file_name")
        vsb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self.window, bg=t["BG_DEEP"])
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 12))
        tk.Button(
            btn_frame,
            text="+ Add X-Ray Report",
            command=self._on_add,
            font=(FONT_UI, 10, "bold"),
            bg=BTN_SUCCESS_BG,
            fg="white",
            padx=18,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground=BTN_SUCCESS_HOVER,
            activeforeground="white",
        ).pack(side=tk.LEFT, padx=6)
        tk.Button(
            btn_frame,
            text="View",
            command=self._on_view,
            font=(FONT_UI, 10, "bold"),
            bg=BTN_PRIMARY_BG,
            fg="white",
            padx=18,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground=BTN_PRIMARY_HOVER,
            activeforeground="white",
        ).pack(side=tk.LEFT, padx=6)
        tk.Button(
            btn_frame,
            text="Delete",
            command=self._on_delete,
            font=(FONT_UI, 10, "bold"),
            bg=BTN_DANGER_BG,
            fg="white",
            padx=18,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground=BTN_DANGER_HOVER,
            activeforeground="white",
        ).pack(side=tk.LEFT, padx=6)

    def _refresh_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        reports = self.db.get_xray_reports_by_patient(self.patient_id)
        for r in reports:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    r.get("report_id", ""),
                    r.get("report_date", ""),
                    r.get("body_part", "") or "—",
                    r.get("file_name_original", "") or os.path.basename(r.get("file_path", "") or ""),
                ),
            )

    def _get_selected_report(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a report.")
            return None
        item = self.tree.item(sel[0])
        vals = item.get("values") or ()
        report_id = vals[0] if vals else None
        if not report_id:
            return None
        return self.db.get_xray_report_by_id(report_id)

    def _on_view(self):
        report = self._get_selected_report()
        if not report:
            return
        path = report.get("file_path")
        if not path or not os.path.isfile(path):
            messagebox.showerror("Error", "File not found.")
            return
        _open_file_with_default(path)

    def _on_delete(self):
        report = self._get_selected_report()
        if not report:
            return
        if not messagebox.askyesno("Confirm", "Delete this X-ray report? The file will be removed."):
            return
        report_id = report.get("report_id")
        file_path = report.get("file_path")
        delete_xray_file(file_path)
        if self.db.delete_xray_report(report_id):
            messagebox.showinfo("Done", "Report deleted.")
            self._refresh_list()
        else:
            messagebox.showerror("Error", "Failed to delete report from database.")

    def _on_add(self):
        t = get_theme()
        d = tk.Toplevel(self.window)
        d.title("Add X-Ray Report")
        d.configure(bg=t["BG_BASE"])
        d.transient(self.window)
        d.geometry("480x380")
        d.lift()
        d.focus_force()
        fields = tk.Frame(d, bg=t["BG_BASE"])
        fields.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        tk.Label(fields, text="Report date (YYYY-MM-DD):", font=(FONT_UI, 10, "bold"), bg=t["BG_BASE"], fg=t["TEXT_PRIMARY"]).grid(row=0, column=0, sticky="w", pady=6)
        date_var = tk.StringVar(value=get_current_date())
        tk.Entry(fields, textvariable=date_var, width=14, font=(FONT_UI, 10), bg=t["BG_CARD"], fg=t["TEXT_PRIMARY"]).grid(row=0, column=1, sticky="w", padx=(8, 0), pady=6)
        tk.Label(fields, text="Body part:", font=(FONT_UI, 10, "bold"), bg=t["BG_BASE"], fg=t["TEXT_PRIMARY"]).grid(row=1, column=0, sticky="w", pady=6)
        body_var = tk.StringVar()
        body_combo = ttk.Combobox(fields, textvariable=body_var, values=list(self.BODY_PARTS), width=18, state="readonly")
        body_combo.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=6)
        if self.BODY_PARTS:
            body_combo.set(self.BODY_PARTS[0])
        tk.Label(fields, text="Findings (optional):", font=(FONT_UI, 10, "bold"), bg=t["BG_BASE"], fg=t["TEXT_PRIMARY"]).grid(row=2, column=0, sticky="nw", pady=6)
        findings_text = tk.Text(fields, height=6, width=42, wrap="word", font=(FONT_UI, 10), bg=t["BG_CARD"], fg=t["TEXT_PRIMARY"])
        findings_text.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=6)
        tk.Label(fields, text="File (image/PDF):", font=(FONT_UI, 10, "bold"), bg=t["BG_BASE"], fg=t["TEXT_PRIMARY"]).grid(row=3, column=0, sticky="w", pady=6)
        file_var = tk.StringVar()
        file_frame = tk.Frame(fields, bg=t["BG_BASE"])
        file_frame.grid(row=3, column=1, sticky="w", padx=(8, 0), pady=6)
        tk.Entry(file_frame, textvariable=file_var, width=32, state="readonly", font=(FONT_UI, 9), bg=t["BG_CARD"], fg=t["TEXT_PRIMARY"]).pack(side=tk.LEFT, padx=(0, 8))
        def choose_file():
            path = filedialog.askopenfilename(
                title="Select X-Ray image or PDF",
                filetypes=[
                    ("Image/PDF", "*.png *.jpg *.jpeg *.gif *.bmp *.pdf"),
                    ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("PDF", "*.pdf"),
                    ("All files", "*.*"),
                ],
            )
            if path:
                file_var.set(path)
        tk.Button(file_frame, text="Choose file…", command=choose_file, font=(FONT_UI, 9, "bold"), bg=BTN_SECONDARY_BG, fg=t["TEXT_PRIMARY"], padx=10, pady=4, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT)
        btns = tk.Frame(d, bg=t["BG_BASE"])
        btns.pack(fill=tk.X, padx=20, pady=(0, 16))
        def save():
            report_date = date_var.get().strip()
            if not report_date:
                messagebox.showwarning("Warning", "Enter report date.")
                return
            source_path = file_var.get().strip()
            if not source_path or not os.path.isfile(source_path):
                messagebox.showwarning("Warning", "Select an image or PDF file.")
                return
            report_id = generate_id("XR")
            ok, dest_path = save_xray_file(self.patient_id, report_id, source_path)
            if not ok or not dest_path:
                messagebox.showerror("Error", "Failed to save file.")
                return
            file_name_original = os.path.basename(source_path)
            body_part = (body_var.get() or "").strip()
            findings = findings_text.get("1.0", tk.END).strip()
            rid = self.db.add_xray_report(
                self.patient_id,
                report_date,
                body_part,
                findings,
                dest_path,
                file_name_original,
                report_id=report_id,
            )
            if rid:
                messagebox.showinfo("Done", "X-Ray report added.")
                self._refresh_list()
                d.destroy()
            else:
                messagebox.showerror("Error", "Failed to save report to database.")
        tk.Button(btns, text="Save", command=save, font=(FONT_UI, 10, "bold"), bg=BTN_SUCCESS_BG, fg="white", padx=20, pady=8, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=6)
        tk.Button(btns, text="Cancel", command=d.destroy, font=(FONT_UI, 10, "bold"), bg=BTN_SECONDARY_BG, fg=t["TEXT_PRIMARY"], padx=20, pady=8, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=6)


class PatientModule:
    """Patient management interface"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        # Get root window for focus management
        self.root = parent.winfo_toplevel()
        
        self.create_ui()
        # Defer refresh to make UI appear faster
        self.parent.after(10, self.refresh_list)
    
    def create_ui(self):
        """Create user interface"""
        t = get_theme()
        # Header with modern styling (theme-aware)
        header = tk.Label(
            self.parent,
            text="Patient Management",
            font=(FONT_UI, 24, 'bold'),
            bg=t["BG_DEEP"],
            fg=t["TEXT_PRIMARY"]
        )
        header.pack(pady=20)
        
        # Top frame for search and add button
        top_frame = tk.Frame(self.parent, bg=t["BG_DEEP"])
        top_frame.pack(fill=tk.X, padx=25, pady=15)
        
        # Search frame
        search_frame = tk.Frame(top_frame, bg=t["BG_DEEP"])
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(search_frame, text="Search:", font=(FONT_UI, 11, 'bold'), bg=t["BG_DEEP"], fg=t["TEXT_SECONDARY"]).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_patients())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=(FONT_UI, 11), width=30, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground=t["BORDER_DEFAULT"], highlightcolor=t["ACCENT_BLUE"], bg=t["BG_CARD"], fg=t["TEXT_PRIMARY"], insertbackground=t["TEXT_PRIMARY"])
        search_entry.pack(side=tk.LEFT, padx=8)
        
        # Add patient button with modern styling
        add_btn = tk.Button(
            top_frame,
            text="+ Add New Patient",
            command=self.add_patient,
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
        
        # Container for list and buttons to ensure both are visible
        content_container = tk.Frame(self.parent, bg=t["BG_DEEP"])
        content_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)
        
        # List frame - fixed height to ensure buttons are visible
        list_frame = tk.Frame(content_container, bg=t["BG_DEEP"])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for patient list
        columns = ('ID', 'Name', 'DOB', 'Gender', 'Phone', 'Email')
        
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
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
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
        
        # Configure column widths based on content - more appropriate sizes
        column_widths = {
            'ID': 150,
            'Name': 200,
            'DOB': 120,
            'Gender': 100,
            'Phone': 150,
            'Email': 220
        }
        
        # Minimum widths to ensure content is readable
        min_widths = {
            'ID': 120,
            'Name': 150,
            'DOB': 100,
            'Gender': 80,
            'Phone': 120,
            'Email': 150
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
        
        # Ensure tree can receive focus and clicks immediately after dialog closes
        self.tree.configure(takefocus=1)
        
        # Use pack layout like other modules for consistency and reliability
        # Pack horizontal scrollbar first at bottom, then treeview and vertical scrollbar
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Pack treeview and vertical scrollbar side by side
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double click (opens view mode)
        self.tree.bind('<Double-1>', self.view_patient)
        
        # Add right-click context menu for quick access
        context_menu = tk.Menu(self.parent, tearoff=0)
        context_menu.add_command(label="View Details", command=self.view_patient)
        context_menu.add_command(label="✏️ Edit Patient", command=self.edit_patient)
        context_menu.add_command(label="🖨️ Print All Documents", command=self.print_all_documents)
        context_menu.add_command(label="📷 X-Ray Reports", command=self.open_xray_reports)
        context_menu.add_separator()
        context_menu.add_command(label="Delete Patient", command=self.delete_patient)
        
        def show_context_menu(event):
            """Show context menu on right-click"""
            try:
                # Select the item under cursor if not already selected
                item = self.tree.identify_row(event.y)
                if item:
                    self.tree.selection_set(item)
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        self.tree.bind('<Button-3>', show_context_menu)  # Right-click on Windows
        self.tree.bind('<Button-2>', show_context_menu)  # Right-click on Mac/Linux
        
        # Action buttons with modern styling - placed in container AFTER list frame so always visible
        action_frame = tk.Frame(content_container, bg=t["BG_DEEP"])
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            action_frame,
            text="View Details",
            command=self.view_patient,
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
            text="IPD / Daily Notes",
            command=self.open_ipd_notes,
            font=(FONT_UI, 10, 'bold'),
            bg=ACCENT_PURPLE,
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
            text="🖨️ Print All Documents",
            command=self.print_all_documents,
            font=(FONT_UI, 10, 'bold'),
            bg=ACCENT_TEAL,
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#0891b2',
            activeforeground='white'
        ).pack(side=tk.LEFT, padx=6)

        tk.Button(
            action_frame,
            text="📷 X-Ray Reports",
            command=self.open_xray_reports,
            font=(FONT_UI, 10, 'bold'),
            bg=ACCENT_PURPLE,
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#7c3aed',
            activeforeground='white'
        ).pack(side=tk.LEFT, padx=6)
        
        edit_btn = tk.Button(
            action_frame,
            text="✏️ Edit Patient",
            command=self.edit_patient,
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
        )
        edit_btn.pack(side=tk.LEFT, padx=6)
        # Store reference for potential focus management
        self.edit_button = edit_btn
        
        tk.Button(
            action_frame,
            text="Delete",
            command=self.delete_patient,
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

    def open_ipd_notes(self):
        """Open IPD admission + day-wise notes for selected patient."""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return
        try:
            AdmissionNotesWindow(self.parent, self.db, patient_id)
        except Exception as e:
            log_error("Failed to open IPD notes window", e)
            messagebox.showerror("Error", f"Failed to open IPD notes: {e}")

    def print_all_documents(self):
        """Print all patient-related PDFs (bills, prescriptions, IPD reports, X-ray reports) in one click."""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return
        try:
            print_all_patient_documents(self.parent, self.db, patient_id)
        except Exception as e:
            log_error("Failed to print patient documents", e)
            messagebox.showerror("Error", f"Failed to generate documents: {e}")

    def open_xray_reports(self):
        """Open X-Ray Reports window for the selected patient."""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return
        try:
            XRayReportsWindow(self.parent, self.db, patient_id)
        except Exception as e:
            log_error("Failed to open X-Ray reports window", e)
            messagebox.showerror("Error", f"Failed to open X-Ray reports: {e}")
    
    def _focus_tree(self):
        """Ensure tree widget is immediately interactive for selection"""
        try:
            # Ensure root window has focus first
            self.root.focus_force()
            self.root.update_idletasks()
            self.root.update()
            
            # For Treeview, focus the widget to make it immediately interactive
            # Treeview widgets can receive clicks even without focus, but setting focus
            # ensures the widget is ready to receive events immediately
            self.tree.focus_set()
            
            # Force event processing to ensure tree is interactive
            self.root.update_idletasks()
            self.root.update()
            log_debug("Tree widget focused and ready for immediate selection")
        except Exception as e:
            log_debug(f"Could not focus tree: {e}")
    
    def refresh_list(self):
        """Refresh patient list - optimized for performance"""
        log_info("Refreshing patient list...")
        # Clear existing items efficiently
        self.tree.delete(*self.tree.get_children())
        
        # Get patients from database
        patients = self.db.get_all_patients()
        log_info(f"Retrieved {len(patients)} patients from database")
        
        # Insert items - treeview handles this efficiently
        for patient in patients:
            name = f"{patient['first_name']} {patient['last_name']}"
            self.tree.insert('', tk.END, values=(
                patient['patient_id'],
                name,
                patient['date_of_birth'],
                patient['gender'],
                patient['phone'],
                patient['email']
            ))
        log_info("Patient list refreshed successfully")
        
        # Return focus to tree after refresh for immediate selection
        self.root.after(10, self._focus_tree)
    
    def search_patients(self):
        """Search patients - optimized"""
        query = self.search_var.get()
        if not query:
            self.refresh_list()
            return
        
        # Clear existing items efficiently
        self.tree.delete(*self.tree.get_children())
        
        # Get search results
        patients = self.db.search_patients(query)
        
        # Insert items
        for patient in patients:
            name = f"{patient['first_name']} {patient['last_name']}"
            self.tree.insert('', tk.END, values=(
                patient['patient_id'],
                name,
                patient['date_of_birth'],
                patient['gender'],
                patient['phone'],
                patient['email']
            ))
    
    def get_selected_patient_id(self):
        """Get selected patient ID"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a patient")
            return None
        item = self.tree.item(selection[0])
        return item['values'][0]
    
    def add_patient(self):
        """Open add patient dialog"""
        log_button_click("Add New Patient", "PatientModule")
        self.patient_dialog(None)
    
    def view_patient(self, event=None):
        """View patient details"""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return
        
        patient = self.db.get_patient_by_id(patient_id)
        if not patient:
            messagebox.showerror("Error", "Patient not found")
            return
        
        self.patient_dialog(patient, view_only=True)
    
    def edit_patient(self):
        """Edit patient - explicitly opens in EDIT mode (not view_only)"""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return
        
        patient = self.db.get_patient_by_id(patient_id)
        if not patient:
            messagebox.showerror("Error", "Patient not found")
            return
        
        log_info(f"Editing patient: {patient_id}, data fields: {list(patient.keys())}")
        # Explicitly pass view_only=False to ensure fields are editable
        self.patient_dialog(patient, view_only=False)
    
    def delete_patient(self):
        """Delete patient"""
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this patient?"):
            return
        
        # Note: In a real application, you'd want to check for related records
        # For now, we'll just show a message
        messagebox.showinfo("Info", "Delete functionality would check for related records first")
    
    def patient_dialog(self, patient=None, view_only=False):
        """Patient form dialog"""
        dialog_type = "Edit Patient" if patient else "Add New Patient"
        dialog_name = dialog_type  # Alias for use in closures
        log_dialog_open(dialog_type)
        log_info(f"Opening {dialog_type} dialog - view_only={view_only}")
        
        dialog = tk.Toplevel(self.parent)
        # Set title based on mode
        if view_only:
            dialog.title("View Patient Details")
        elif patient:
            dialog.title("Edit Patient - Editable")
        else:
            dialog.title("Add New Patient")
        dialog.geometry("600x700")
        dialog.configure(bg=BG_BASE)
        dialog.transient(self.parent)
        
        # Make dialog modal but ensure input works
        dialog.lift()  # Bring dialog to front first
        dialog.focus_force()  # Force focus on dialog
        log_info("Dialog focus set")
        # Use grab_set_global=False to allow other windows to work
        try:
            dialog.grab_set_global(False)
            log_info("Dialog grab set (global=False)")
        except:
            dialog.grab_set()  # Fallback for older tkinter versions
            log_info("Dialog grab set (fallback)")
        
        # Form fields
        fields_frame = tk.Frame(dialog, bg=BG_BASE)
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        entries = {}
        
        # Add mode indicator
        if view_only:
            mode_label = tk.Label(fields_frame, text="📖 VIEW MODE (Read Only)", 
                                 font=(FONT_UI, 11, 'bold'), bg=BG_BASE, fg=ERROR)
            mode_label.pack(pady=5)
        elif patient:
            mode_label = tk.Label(fields_frame, text="✏️ EDIT MODE (Editable)", 
                                 font=(FONT_UI, 11, 'bold'), bg=BG_BASE, fg=SUCCESS)
            mode_label.pack(pady=5)
        
        if patient:
            patient_id = patient['patient_id']
            tk.Label(fields_frame, text=f"Patient ID: {patient_id}", font=(FONT_UI, 13, 'bold'), bg=BG_BASE, fg=TEXT_PRIMARY).pack(pady=8)
        else:
            patient_id = generate_id('PAT')
            tk.Label(fields_frame, text=f"Patient ID: {patient_id}", font=(FONT_UI, 13, 'bold'), bg=BG_BASE, fg=TEXT_PRIMARY).pack(pady=8)
        
        field_configs = [
            ('first_name', 'First Name', True),
            ('last_name', 'Last Name', True),
            ('date_of_birth', 'Date of Birth (YYYY-MM-DD)', True),
            ('gender', 'Gender', True),
            ('phone', 'Phone', False),
            ('email', 'Email', False),
            ('address', 'Address', False),
            ('emergency_contact', 'Emergency Contact', False),
            ('emergency_phone', 'Emergency Phone', False),
            ('blood_group', 'Blood Group', False),
            ('allergies', 'Allergies', False)
        ]
        
        for field, label, required in field_configs:
            frame = tk.Frame(fields_frame, bg=BG_BASE)
            frame.pack(fill=tk.X, pady=10)
            
            tk.Label(frame, text=f"{label}{' *' if required else ''}:", font=(FONT_UI, 10, 'bold'), bg=BG_BASE, fg=TEXT_SECONDARY, width=20, anchor='w').pack(side=tk.LEFT)
            
            if field == 'gender':
                # Get gender value from patient if available, otherwise empty string
                gender_value = ''
                if patient and field in patient:
                    gender_value = str(patient[field]) if patient[field] else ''
                var = tk.StringVar(value=gender_value)
                # For Combobox, use 'readonly' to allow dropdown selection but prevent typing
                # But make it 'normal' if not view_only to allow editing
                combo_state = 'readonly' if view_only else 'readonly'  # Keep readonly for dropdown
                combo = ttk.Combobox(frame, textvariable=var, values=['Male', 'Female', 'Other'], 
                                   state=combo_state, width=30)
                combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries[field] = var
            else:
                # Entry fields should be 'normal' (editable) when not in view_only mode
                # Always create in 'normal' state first, then set to readonly if needed
                entry_state = 'readonly' if view_only else 'normal'
                entry = tk.Entry(frame, font=(FONT_UI, 10), width=35, 
                               state=entry_state, relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground=BORDER_DEFAULT, highlightcolor=ACCENT_BLUE, bg=BG_CARD, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY)
                
                # Insert patient data BEFORE packing
                if patient and field in patient:
                    patient_value = patient[field]
                    if patient_value is not None:
                        # Temporarily set to normal to insert data if it's readonly
                        if entry_state == 'readonly':
                            entry.config(state='normal')
                        entry.insert(0, str(patient_value))
                        # Restore state after insertion
                        if entry_state == 'readonly':
                            entry.config(state='readonly')
                        log_debug(f"Inserted {field} = '{patient_value}' into entry field (state={entry_state})")
                    else:
                        log_debug(f"Field {field} is None in patient data")
                else:
                    if patient:
                        log_debug(f"Field {field} not found in patient data (available fields: {list(patient.keys())})")
                
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries[field] = entry
                
                # Final verification: ensure field is editable when not in view_only mode
                if not view_only:
                    current_state = entry.cget('state')
                    if current_state != 'normal':
                        log_warning(f"Field {field} state is '{current_state}', forcing to 'normal'")
                        entry.config(state='normal')
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=BG_BASE)
        button_frame.pack(fill=tk.X, padx=25, pady=25)
        
        if not view_only:
            def save_patient():
                # CRITICAL: Process events immediately when save button is clicked
                # This ensures the button click event is fully processed
                dialog.update_idletasks()
                dialog.update()
                dialog.update_idletasks()
                
                log_button_click("Save Patient", "PatientDialog")
                log_info(f"Save button clicked - attempting to save patient: {patient_id}")
                
                # Additional event processing to ensure everything is ready
                dialog.update_idletasks()
                
                data = {'patient_id': patient_id}
                for field, widget in entries.items():
                    if isinstance(widget, tk.StringVar):
                        data[field] = widget.get()
                    else:
                        data[field] = widget.get()
                
                log_info(f"Patient data collected: {list(data.keys())}")
                
                # Validation
                required_fields = ['first_name', 'last_name', 'date_of_birth', 'gender']
                for field in required_fields:
                    if not data.get(field):
                        log_warning(f"Validation failed: {field} is required")
                        messagebox.showerror("Error", f"{field.replace('_', ' ').title()} is required")
                        return
                
                log_info("Validation passed")
                
                if patient:
                    log_info(f"Updating existing patient: {patient_id}")
                    if self.db.update_patient(patient_id, data):
                        log_database_operation("UPDATE", "patients", True, f"Patient ID: {patient_id}")
                        # Release grab BEFORE destroying dialog
                        try:
                            dialog.grab_release()
                            log_debug("Dialog grab released")
                        except Exception as e:
                            log_debug(f"Error releasing grab: {e}")
                        
                        log_dialog_close("Edit Patient")
                        
                        # Destroy dialog first
                        dialog.destroy()
                        
                        # Process all pending events immediately - CRITICAL for immediate button response
                        self.root.update_idletasks()
                        self.root.update()
                        self.root.update_idletasks()
                        
                        # Return focus to main window immediately
                        self.root.focus_force()
                        self.root.update_idletasks()
                        self.root.update()
                        
                        # Ensure all events are processed and UI is ready
                        self.root.update_idletasks()
                        
                        # Final update to ensure buttons are immediately responsive
                        self.root.update()
                        self.root.update_idletasks()
                        
                        # CRITICAL: Explicitly ensure all navigation buttons are enabled
                        # Access the main app instance through root
                        try:
                            if hasattr(self.root, 'app_instance'):
                                app = self.root.app_instance
                                if hasattr(app, 'nav_buttons'):
                                    for button_name, btn in app.nav_buttons.items():
                                        if btn['state'] != tk.NORMAL:
                                            btn.config(state=tk.NORMAL)
                                    log_debug("Navigation buttons explicitly enabled after patient update")
                                    # Force one more update after enabling buttons
                                    self.root.update_idletasks()
                                    self.root.update()
                        except Exception as e:
                            log_debug(f"Could not access nav_buttons: {e}")
                        
                        # Additional event processing to ensure buttons are ready
                        self.root.update_idletasks()
                        self.root.update()
                        
                        # Focus tree immediately so user can select another patient right away
                        self._focus_tree()
                        
                        # Refresh list asynchronously (before showing messagebox to avoid focus issues)
                        self.root.after(50, self.refresh_list)
                        
                        # Show message after dialog is closed and list refreshed - delayed to not interfere
                        def show_success_and_refocus():
                            messagebox.showinfo("Success", "Patient updated successfully")
                            # Return focus to tree after messagebox closes
                            self._focus_tree()
                        self.root.after(300, show_success_and_refocus)
                        
                        log_info("Patient update process completed")
                    else:
                        log_database_operation("UPDATE", "patients", False, f"Patient ID: {patient_id}")
                        messagebox.showerror("Error", "Failed to update patient")
                else:
                    log_info(f"Adding new patient: {patient_id}")
                    if self.db.add_patient(data):
                        log_database_operation("INSERT", "patients", True, f"Patient ID: {patient_id}, Name: {data.get('first_name')} {data.get('last_name')}")
                        # Release grab BEFORE destroying dialog
                        try:
                            dialog.grab_release()
                            log_debug("Dialog grab released")
                        except Exception as e:
                            log_debug(f"Error releasing grab: {e}")
                        
                        log_dialog_close("Add New Patient")
                        
                        # Destroy dialog first
                        dialog.destroy()
                        
                        # Process all pending events immediately - CRITICAL for immediate button response
                        self.root.update_idletasks()
                        self.root.update()
                        self.root.update_idletasks()
                        
                        # Return focus to main window immediately
                        self.root.focus_force()
                        self.root.update_idletasks()
                        self.root.update()
                        
                        # Ensure all events are processed and UI is ready
                        self.root.update_idletasks()
                        
                        # Final update to ensure buttons are immediately responsive
                        self.root.update()
                        self.root.update_idletasks()
                        
                        # CRITICAL: Explicitly ensure all navigation buttons are enabled
                        # Access the main app instance through root
                        try:
                            if hasattr(self.root, 'app_instance'):
                                app = self.root.app_instance
                                if hasattr(app, 'nav_buttons'):
                                    for button_name, btn in app.nav_buttons.items():
                                        if btn['state'] != tk.NORMAL:
                                            btn.config(state=tk.NORMAL)
                                    log_debug("Navigation buttons explicitly enabled after patient add")
                                    # Force one more update after enabling buttons
                                    self.root.update_idletasks()
                                    self.root.update()
                        except Exception as e:
                            log_debug(f"Could not access nav_buttons: {e}")
                        
                        # Additional event processing to ensure buttons are ready
                        self.root.update_idletasks()
                        self.root.update()
                        
                        # Focus tree immediately so user can select another patient right away
                        self._focus_tree()
                        
                        # Refresh list asynchronously (before showing messagebox to avoid focus issues)
                        self.root.after(50, self.refresh_list)
                        
                        # Show message after dialog is closed and list refreshed - delayed to not interfere
                        def show_success_and_refocus():
                            messagebox.showinfo("Success", "Patient added successfully")
                            # Return focus to tree after messagebox closes
                            self._focus_tree()
                        self.root.after(300, show_success_and_refocus)
                        
                        log_info("Patient add process completed")
                    else:
                        log_database_operation("INSERT", "patients", False, f"Patient ID: {patient_id} - ID might already exist")
                        messagebox.showerror("Error", "Failed to add patient (ID might already exist)")
            
            # Create wrapper to ensure events are processed
            def on_save_button_click():
                """Wrapper to ensure events are processed before save"""
                log_info("Save button wrapper called - processing events")
                # Process events immediately
                dialog.update_idletasks()
                dialog.update()
                dialog.update_idletasks()
                # Call the actual save function
                save_patient()
            
            save_btn = tk.Button(
                button_frame,
                text="Save",
                command=on_save_button_click,
                font=(FONT_UI, 11, 'bold'),
                bg=BTN_SUCCESS_BG,
                fg='white',
                padx=35,
                pady=10,
                cursor='hand2',
                state=tk.NORMAL,
                activebackground=BTN_SUCCESS_HOVER,
                activeforeground='white',
                relief=tk.FLAT,
                bd=0
            )
            save_btn.pack(side=tk.LEFT, padx=10)
            
            # Also bind to Button-1 event as backup to ensure it works
            def on_save_click_event(event):
                """Handle Button-1 click on save button"""
                log_info("Save button Button-1 event triggered")
                dialog.update_idletasks()
                dialog.update()
                on_save_button_click()
                return "break"  # Prevent default behavior
            
            save_btn.bind('<Button-1>', on_save_click_event)
            
            # Store save_btn reference for focus handlers
            dialog._save_btn = save_btn
        
        def close_dialog():
            log_button_click("Close Dialog", "PatientDialog")
            # Release grab BEFORE destroying
            try:
                dialog.grab_release()
                log_debug("Dialog grab released on close")
            except Exception as e:
                log_debug(f"Error releasing grab on close: {e}")
            
            log_dialog_close(dialog_name)
            
            # Destroy dialog
            dialog.destroy()
            
            # Process all pending events immediately - CRITICAL for immediate button response
            self.root.update_idletasks()
            self.root.update()
            self.root.update_idletasks()
            
            # Return focus to main window immediately
            self.root.focus_force()
            self.root.update_idletasks()
            self.root.update()
            
            # Ensure all events are processed and UI is ready
            self.root.update_idletasks()
            log_info("Dialog closed, focus returned to main window")
        
        close_btn = tk.Button(
            button_frame,
            text="Close",
            command=close_dialog,
            font=(FONT_UI, 11, 'bold'),
            bg=BTN_SECONDARY_BG,
            fg='white',
            padx=35,
            pady=10,
            cursor='hand2',
            state=tk.NORMAL,
            activebackground=BTN_SECONDARY_HOVER,
            activeforeground='white',
            relief=tk.FLAT,
            bd=0
        )
        close_btn.pack(side=tk.LEFT, padx=10)
        
        # Ensure everything is ready
        dialog.update_idletasks()
        
        # Make sure entry fields can receive input (they should already be in correct state)
        # This is a critical safety check to ensure fields are editable when not in view_only mode
        if not view_only:
            log_info("Ensuring all entry fields are editable (not view_only mode)")
            for field, widget in entries.items():
                if not isinstance(widget, tk.StringVar):
                    # Force state to normal for editable fields
                    current_state = widget.cget('state')
                    if current_state != 'normal':
                        log_warning(f"Field {field} was in state '{current_state}', forcing to 'normal'")
                        widget.config(state='normal')
                    # Verify it's actually normal now
                    final_state = widget.cget('state')
                    if final_state != 'normal':
                        log_error(f"Field {field} could not be set to 'normal', current state: '{final_state}'")
                    else:
                        log_debug(f"Field {field} confirmed editable (state='normal')")
                    widget.update_idletasks()
        else:
            log_info("Dialog is in view_only mode - fields should be readonly")
        
        # Set focus on first name field when adding new patient
        # Do this AFTER all widgets are created and dialog is updated
        if not patient and not view_only:
            # Find the first_name entry field
            first_name_entry = entries.get('first_name')
            if first_name_entry and not isinstance(first_name_entry, tk.StringVar):
                # Prevent other widgets from taking focus initially
                # Temporarily disable focus on other entry fields
                for field, widget in entries.items():
                    if field != 'first_name' and not isinstance(widget, tk.StringVar):
                        widget.config(takefocus=0)  # Disable focus temporarily
                
                # Set focus on dialog first to prevent other widgets from grabbing it
                dialog.focus_set()
                dialog.update_idletasks()
                
                # Use multiple attempts to ensure focus is set correctly
                def set_focus_initial():
                    # Make sure first_name entry is ready
                    first_name_entry.update_idletasks()
                    first_name_entry.focus_set()
                    first_name_entry.icursor(0)  # Set cursor at start
                    log_debug("Focus set on first_name field (initial)")
                
                def set_focus_backup():
                    # Backup focus set to ensure it sticks
                    first_name_entry.focus_set()
                    first_name_entry.icursor(0)
                    log_debug("Focus set on first_name field (backup)")
                
                def re_enable_focus():
                    # Re-enable focus on other fields after first_name has focus
                    for field, widget in entries.items():
                        if field != 'first_name' and not isinstance(widget, tk.StringVar):
                            widget.config(takefocus=1)  # Re-enable focus
                
                # Set focus after dialog is fully rendered
                dialog.after(50, set_focus_initial)
                dialog.after(150, set_focus_backup)
                dialog.after(200, re_enable_focus)
        
        # Bind Enter key to move to next field or Save
        if not view_only:
            def on_return(event):
                # Get the widget that has focus
                focused_widget = dialog.focus_get()
                
                # If focus is on an entry field, move to next field
                if isinstance(focused_widget, tk.Entry):
                    # Find current field index
                    field_list = list(entries.keys())
                    current_field = None
                    for field, widget in entries.items():
                        if widget == focused_widget:
                            current_field = field
                            break
                    
                    if current_field:
                        current_index = field_list.index(current_field)
                        # Move to next field
                        if current_index < len(field_list) - 1:
                            next_field = field_list[current_index + 1]
                            next_widget = entries[next_field]
                            if not isinstance(next_widget, tk.StringVar):
                                next_widget.focus_set()
                                return "break"  # Prevent default Enter behavior
                    
                    # If on last field or can't find next, save
                    save_patient()
                    return "break"
                else:
                    # If not on entry field, save
                    save_patient()
                    return "break"
            
            dialog.bind('<Return>', on_return)
            # Also bind to entry fields individually
            for field, widget in entries.items():
                if not isinstance(widget, tk.StringVar):
                    widget.bind('<Return>', on_return)
                    # Bind Tab to move to next field
                    def make_tab_handler(current_field):
                        def on_tab(event):
                            field_list = list(entries.keys())
                            current_index = field_list.index(current_field)
                            if current_index < len(field_list) - 1:
                                next_field = field_list[current_index + 1]
                                next_widget = entries[next_field]
                                if not isinstance(next_widget, tk.StringVar):
                                    next_widget.focus_set()
                                    return "break"
                            return None
                        return on_tab
                    widget.bind('<Tab>', make_tab_handler(field))
        
        def on_escape(event):
            log_info("Escape key pressed, closing dialog")
            try:
                dialog.grab_release()
            except:
                pass
            log_dialog_close(dialog_name)
            dialog.destroy()
            
            # Process all pending events immediately - CRITICAL for immediate button response
            self.root.update_idletasks()
            self.root.update()
            self.root.update_idletasks()
            
            # Return focus to main window immediately
            self.root.focus_force()
            self.root.update_idletasks()
            self.root.update()
            
            # Ensure all events are processed and UI is ready
            self.root.update_idletasks()
            return "break"
        dialog.bind('<Escape>', on_escape)
        
        # Ensure dialog releases grab when closed
        def on_close():
            log_info("Dialog window close (X) clicked")
            try:
                dialog.grab_release()
            except:
                pass
            log_dialog_close(dialog_name)
            dialog.destroy()
            
            # Process all pending events immediately - CRITICAL for immediate button response
            self.root.update_idletasks()
            self.root.update()
            self.root.update_idletasks()
            
            # Return focus to main window immediately
            self.root.focus_force()
            self.root.update_idletasks()
            self.root.update()
            
            # Ensure all events are processed and UI is ready
            self.root.update_idletasks()
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
        # Set up focus event handlers for dialog to ensure buttons work when dialog is active
        # Track last focus processing time to avoid excessive logging and processing
        dialog._last_focus_process = 0
        
        def on_dialog_focus_in(event):
            """Handle dialog gaining focus - process pending events"""
            import time
            current_time = time.time()
            # Only process if it's been at least 0.3 seconds since last processing
            if current_time - dialog._last_focus_process > 0.3:
                log_debug("Dialog gained focus - processing events")
                dialog._last_focus_process = current_time
                dialog.update_idletasks()
                # Ensure save button is enabled
                if not view_only and hasattr(dialog, '_save_btn'):
                    if dialog._save_btn['state'] != tk.NORMAL:
                        dialog._save_btn.config(state=tk.NORMAL)
                dialog.update_idletasks()
            return True
        
        def on_dialog_focus_out(event):
            """Handle dialog losing focus"""
            # Don't log every focus out event to reduce log spam
            return True
        
        # Bind focus events to dialog
        dialog.bind('<FocusIn>', on_dialog_focus_in)
        dialog.bind('<FocusOut>', on_dialog_focus_out)
        
        # Start periodic event processing for dialog to ensure save button always works
        def process_dialog_events_periodically():
            """Periodically process events in dialog to ensure buttons remain responsive"""
            try:
                # Check if dialog still exists
                if not dialog.winfo_exists():
                    return
                
                # Process pending idle tasks
                dialog.update_idletasks()
                
                # Ensure save button is enabled
                if not view_only and hasattr(dialog, '_save_btn'):
                    if dialog._save_btn['state'] != tk.NORMAL:
                        dialog._save_btn.config(state=tk.NORMAL)
                
                # Schedule next processing (every 300ms for dialog - more frequent than main window)
                dialog.after(300, process_dialog_events_periodically)
            except Exception as e:
                # If dialog is destroyed, stop processing
                log_debug(f"Dialog event processing stopped: {e}")
        
        # Start periodic processing after a short delay
        if not view_only:
            dialog.after(100, process_dialog_events_periodically)
            log_info("Dialog periodic event processing started")
        
        # Final update to ensure everything is interactive
        dialog.update()

