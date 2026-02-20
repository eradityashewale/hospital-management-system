"""
Medicine Management Module
Add and list medicines in the master catalogue.
"""
import tkinter as tk
from tkinter import ttk, messagebox

# Backend imports
from backend.database import Database

# Frontend theme
from frontend.theme import (
    BG_BASE, BG_CARD, BG_DEEP, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_BLUE, BORDER_DEFAULT,
    TABLE_HEADER_BG, BTN_SUCCESS_BG, BTN_SUCCESS_HOVER,
    FONT_UI, get_theme,
)

# Utils imports
from utils.logger import log_info, log_error


class MedicineModule:
    """Medicine master management – add new medicines and view catalogue."""

    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.create_ui()
        self.parent.after(10, self.refresh_list)

    def create_ui(self):
        """Create user interface"""
        t = get_theme()
        header = tk.Label(
            self.parent,
            text="Medicine Catalogue",
            font=(FONT_UI, 24, 'bold'),
            bg=t["BG_DEEP"],
            fg=t["TEXT_PRIMARY"]
        )
        header.pack(pady=20)

        top_frame = tk.Frame(self.parent, bg=t["BG_DEEP"])
        top_frame.pack(fill=tk.X, padx=25, pady=15)

        search_frame = tk.Frame(top_frame, bg=t["BG_DEEP"])
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            search_frame, text="Search:", font=(FONT_UI, 11, 'bold'),
            bg=t["BG_DEEP"], fg=t["TEXT_SECONDARY"]
        ).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_medicines())
        search_entry = tk.Entry(
            search_frame, textvariable=self.search_var, font=(FONT_UI, 11),
            width=30, relief=tk.FLAT, bd=2, highlightthickness=1,
            highlightbackground=t["BORDER_DEFAULT"], highlightcolor=t["ACCENT_BLUE"],
            bg=t["BG_CARD"], fg=t["TEXT_PRIMARY"], insertbackground=t["TEXT_PRIMARY"]
        )
        search_entry.pack(side=tk.LEFT, padx=8)

        add_btn = tk.Button(
            top_frame,
            text="+ Add New Medicine",
            command=self.add_medicine,
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

        content_container = tk.Frame(self.parent, bg=t["BG_DEEP"])
        content_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)

        list_frame = tk.Frame(content_container, bg=t["BG_DEEP"])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ('Medicine Name', 'Company', 'Category', 'Dosage', 'Form', 'Description')
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        style.configure(
            "MedTree.Treeview",
            font=(FONT_UI, 10),
            rowheight=28,
            background=t["BG_CARD"],
            foreground=t["TEXT_PRIMARY"],
            fieldbackground=t["BG_CARD"]
        )
        style.configure(
            "MedTree.Treeview.Heading",
            font=(FONT_UI, 11, 'bold'),
            background=t["TABLE_HEADER_BG"],
            foreground=t["TEXT_PRIMARY"],
            relief='flat'
        )
        style.map("MedTree.Treeview.Heading",
                 background=[('active', t["ACCENT_BLUE"]), ('pressed', t["ACCENT_BLUE"])])
        style.map("MedTree.Treeview",
                  background=[('selected', t["ACCENT_BLUE"])],
                  foreground=[('selected', 'white')])

        self.tree = ttk.Treeview(
            list_frame, columns=columns, show='headings', height=14,
            style="MedTree.Treeview"
        )
        style.configure(
            "Vertical.TScrollbar",
            background=t["TEXT_MUTED"],
            troughcolor=t["BG_BASE"],
            borderwidth=0,
            arrowcolor=t["ACCENT_BLUE"]
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=t["TEXT_MUTED"],
            troughcolor=t["BG_BASE"],
            borderwidth=1,
            arrowcolor=t["ACCENT_BLUE"]
        )

        col_widths = {
            'Medicine Name': 200,
            'Company': 140,
            'Category': 120,
            'Dosage': 100,
            'Form': 90,
            'Description': 220
        }
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 120), minwidth=60, stretch=True, anchor='w')

        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_list(self):
        """Reload medicine list from database"""
        self.tree.delete(*self.tree.get_children())
        try:
            medicines = self.db.get_all_medicines_master()
            for m in medicines:
                desc = (m.get('description') or '')[:50]
                if len((m.get('description') or '')) > 50:
                    desc += '…'
                self.tree.insert('', tk.END, values=(
                    m.get('medicine_name', ''),
                    m.get('company_name', ''),
                    m.get('category', ''),
                    m.get('dosage_mg', ''),
                    m.get('dosage_form', ''),
                    desc
                ))
        except Exception as e:
            log_error("Failed to load medicines", e)
            messagebox.showerror("Error", f"Failed to load medicines: {str(e)}")

    def search_medicines(self):
        """Filter list by search text"""
        query = (self.search_var.get() or '').strip()
        self.tree.delete(*self.tree.get_children())
        try:
            if query:
                medicines = self.db.search_medicines_master(query)
            else:
                medicines = self.db.get_all_medicines_master()
            for m in medicines:
                desc = (m.get('description') or '')[:50]
                if len((m.get('description') or '')) > 50:
                    desc += '…'
                self.tree.insert('', tk.END, values=(
                    m.get('medicine_name', ''),
                    m.get('company_name', ''),
                    m.get('category', ''),
                    m.get('dosage_mg', ''),
                    m.get('dosage_form', ''),
                    desc
                ))
        except Exception as e:
            log_error("Search medicines failed", e)
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def add_medicine(self):
        """Open add medicine dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New Medicine")
        dialog.geometry("520x420")
        dialog.configure(bg=BG_BASE)
        dialog.transient(self.parent)
        root = self.parent.winfo_toplevel()
        dialog.lift()
        dialog.focus_force()
        try:
            dialog.grab_set_global(False)
        except Exception:
            dialog.grab_set()

        main_container = tk.Frame(dialog, bg=BG_BASE)
        main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        fields_frame = tk.Frame(main_container, bg=BG_BASE)
        fields_frame.pack(fill=tk.BOTH, expand=True)

        entries = {}
        field_configs = [
            ('medicine_name', 'Medicine Name', True),
            ('company_name', 'Company / Brand', False),
            ('category', 'Category', False),
            ('dosage_mg', 'Dosage (e.g. 500mg)', False),
            ('dosage_form', 'Dosage Form (Tablet/Syrup/etc)', False),
            ('description', 'Description', False),
        ]
        for field, label, required in field_configs:
            frame = tk.Frame(fields_frame, bg=BG_BASE)
            frame.pack(fill=tk.X, pady=8)
            tk.Label(
                frame, text=f"{label}{' *' if required else ''}:",
                font=(FONT_UI, 10, 'bold'), bg=BG_BASE, fg=TEXT_SECONDARY,
                width=32, anchor='w'
            ).pack(side=tk.LEFT)
            if field == 'description':
                entry = tk.Text(frame, font=(FONT_UI, 10), height=3, width=28,
                                relief=tk.FLAT, bd=2, highlightthickness=1,
                                highlightbackground=BORDER_DEFAULT, highlightcolor=ACCENT_BLUE,
                                bg=BG_CARD, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries[field] = entry
            else:
                entry = tk.Entry(
                    frame, font=(FONT_UI, 10), width=32,
                    relief=tk.FLAT, bd=2, highlightthickness=1,
                    highlightbackground=BORDER_DEFAULT, highlightcolor=ACCENT_BLUE,
                    bg=BG_CARD, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY
                )
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries[field] = entry

        pediatric_frame = tk.Frame(fields_frame, bg=BG_BASE)
        pediatric_frame.pack(fill=tk.X, pady=10)
        self.pediatric_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            pediatric_frame,
            text="Pediatric / Child use",
            variable=self.pediatric_var,
            font=(FONT_UI, 10),
            bg=BG_BASE,
            fg=TEXT_PRIMARY,
            activebackground=BG_BASE,
            activeforeground=TEXT_PRIMARY,
            selectcolor=BG_CARD
        ).pack(anchor='w')

        button_frame = tk.Frame(main_container, bg=BG_BASE)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        def get_description():
            e = entries.get('description')
            if e is None:
                return ''
            try:
                return e.get("1.0", tk.END).strip()
            except Exception:
                return (e.get() if hasattr(e, 'get') else '') or ''

        def save_medicine():
            medicine_name = (entries['medicine_name'].get() or '').strip()
            if not medicine_name:
                messagebox.showerror("Error", "Medicine name is required.")
                return
            medicine_data = {
                'medicine_name': medicine_name,
                'company_name': (entries['company_name'].get() or '').strip(),
                'category': (entries['category'].get() or '').strip(),
                'dosage_mg': (entries['dosage_mg'].get() or '').strip(),
                'dosage_form': (entries['dosage_form'].get() or '').strip(),
                'description': get_description(),
                'is_pediatric': 1 if self.pediatric_var.get() else 0,
            }
            if self.db.add_medicine_to_master(medicine_data):
                try:
                    dialog.grab_release()
                except Exception:
                    pass
                dialog.destroy()
                root.update_idletasks()
                root.update()
                root.focus_force()
                root.after(150, lambda: messagebox.showinfo("Success", "Medicine added successfully."))
                root.after(250, self.refresh_list)
            else:
                messagebox.showerror("Error", "Failed to add medicine. It may already exist.")

        tk.Button(
            button_frame,
            text="Save",
            command=save_medicine,
            font=(FONT_UI, 11, 'bold'),
            bg=BTN_SUCCESS_BG,
            fg='white',
            padx=35,
            pady=10,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground=BTN_SUCCESS_HOVER,
            activeforeground='white'
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            font=(FONT_UI, 11, 'bold'),
            bg=BORDER_DEFAULT,
            fg=TEXT_PRIMARY,
            padx=25,
            pady=10,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0
        ).pack(side=tk.LEFT)
