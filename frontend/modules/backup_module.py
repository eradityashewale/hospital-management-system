"""
Backup & Restore Module - Desktop UI
Cloud backup to Google Cloud Storage
"""
import json
import os
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from frontend.theme import (
    BG_BASE, BG_CARD, BG_DEEP, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_BLUE, SUCCESS, WARNING, BTN_PRIMARY_BG, BTN_PRIMARY_HOVER,
    BTN_SUCCESS_BG, BTN_DANGER_BG, TABLE_HEADER_BG,
    get_theme,
)
from backend.database import Database
from backend.cloud_backup import (
    GCSBackupService,
    create_backup_filename,
    is_gcs_available,
)
from utils.logger import log_info, log_error


class BackupModule:
    """Backup and restore database via Google Cloud Storage."""

    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        self.root = parent.winfo_toplevel()
        self.selected_backup = None
        self.create_ui()

    def create_ui(self):
        """Create backup/restore interface."""
        t = get_theme()
        # Header (theme-aware)
        header = tk.Label(
            self.parent,
            text="☁️ Cloud Backup & Restore",
            font=('Segoe UI', 24, 'bold'),
            bg=t["BG_DEEP"],
            fg=t["TEXT_PRIMARY"],
        )
        header.pack(pady=20)

        desc = tk.Label(
            self.parent,
            text="Backup your database to Google Cloud Storage. Restore if your account crashes.",
            font=('Segoe UI', 11),
            bg=t["BG_DEEP"],
            fg=t["TEXT_MUTED"],
        )
        desc.pack(pady=(0, 20))

        # Status
        self.status_var = tk.StringVar()
        if is_gcs_available():
            self.status_var.set("✅ Google Cloud Storage ready")
            status_fg = SUCCESS
        else:
            self.status_var.set("⚠️ Install: pip install google-cloud-storage")
            status_fg = WARNING
        status_label = tk.Label(
            self.parent,
            textvariable=self.status_var,
            font=('Segoe UI', 10),
            bg=t["BG_DEEP"],
            fg=status_fg,
        )
        status_label.pack(pady=(0, 15))

        # Config frame
        config_frame = tk.LabelFrame(
            self.parent,
            text="Configuration",
            font=('Segoe UI', 11, 'bold'),
            bg=t["BG_DEEP"],
            fg=t["TEXT_SECONDARY"],
        )
        config_frame.pack(fill=tk.X, padx=25, pady=10)

        # Bucket name
        row1 = tk.Frame(config_frame, bg=t["BG_DEEP"])
        row1.pack(fill=tk.X, padx=15, pady=10)
        tk.Label(row1, text="Bucket Name:", font=('Segoe UI', 10), bg=t["BG_DEEP"], fg=t["TEXT_SECONDARY"], width=14, anchor='w').pack(side=tk.LEFT, padx=(0, 8))
        self.bucket_entry = tk.Entry(row1, font=('Segoe UI', 10), width=35, bg=t["BG_CARD"], fg=t["TEXT_PRIMARY"], insertbackground=t["TEXT_PRIMARY"])
        self.bucket_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.bucket_entry.insert(0, "")

        # Credentials - file path or JSON
        row2 = tk.Frame(config_frame, bg=t["BG_DEEP"])
        row2.pack(fill=tk.X, padx=15, pady=10)
        tk.Label(row2, text="Credentials:", font=('Segoe UI', 10), bg=t["BG_DEEP"], fg=t["TEXT_SECONDARY"], width=14, anchor='w').pack(side=tk.LEFT, padx=(0, 8))
        self.creds_path_entry = tk.Entry(row2, font=('Segoe UI', 10), width=30, bg=t["BG_CARD"], fg=t["TEXT_PRIMARY"], insertbackground=t["TEXT_PRIMARY"])
        self.creds_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        browse_btn = tk.Button(
            row2,
            text="Browse...",
            command=self._browse_credentials,
            font=('Segoe UI', 9),
            bg=t["BG_BASE"],
            fg=t["TEXT_PRIMARY"],
            cursor='hand2',
        )
        browse_btn.pack(side=tk.LEFT)
        tk.Label(config_frame, text="Or paste JSON below:", font=('Segoe UI', 9), bg=t["BG_DEEP"], fg=t["TEXT_MUTED"]).pack(anchor='w', padx=15, pady=(0, 4))
        self.creds_text = tk.Text(config_frame, height=5, font=('Consolas', 9), wrap=tk.WORD, width=60, bg=t["BG_CARD"], fg=t["TEXT_PRIMARY"], insertbackground=t["TEXT_PRIMARY"])
        self.creds_text.pack(fill=tk.X, padx=15, pady=(0, 10))

        # Buttons
        btn_frame = tk.Frame(config_frame, bg=t["BG_DEEP"])
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        tk.Button(
            btn_frame,
            text="📤 Upload Backup",
            command=self._upload_backup,
            font=('Segoe UI', 10, 'bold'),
            bg=BTN_PRIMARY_BG,
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(
            btn_frame,
            text="📋 List Backups",
            command=self._list_backups,
            font=('Segoe UI', 10, 'bold'),
            bg=BTN_SUCCESS_BG,
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
        ).pack(side=tk.LEFT)

        # Backups list
        list_frame = tk.LabelFrame(
            self.parent,
            text="Available Backups",
            font=('Segoe UI', 11, 'bold'),
            bg=t["BG_DEEP"],
            fg=t["TEXT_SECONDARY"],
        )
        list_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)

        columns = ('Name', 'Date', 'Size', 'Path')
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure("Treeview", font=('Segoe UI', 10), rowheight=28, background=t["BG_CARD"], foreground=t["TEXT_PRIMARY"], fieldbackground=t["BG_CARD"])
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'), background=t["TABLE_HEADER_BG"], foreground=t["TEXT_PRIMARY"])
        style.map("Treeview", background=[('selected', t["ACCENT_BLUE"])], foreground=[('selected', 'white')])

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8, yscrollcommand=scrollbar.set, selectmode='browse')
        scrollbar.config(command=self.tree.yview)
        self.tree.heading('Name', text='Backup Name')
        self.tree.heading('Date', text='Last Modified')
        self.tree.heading('Size', text='Size')
        self.tree.heading('Path', text='')
        self.tree.column('Name', width=280)
        self.tree.column('Date', width=180)
        self.tree.column('Size', width=80)
        self.tree.column('Path', width=0, minwidth=0, stretch=False)  # Hidden
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

        restore_btn_frame = tk.Frame(list_frame, bg=t["BG_DEEP"])
        restore_btn_frame.pack(fill=tk.X, padx=5, pady=(0, 10))
        tk.Button(
            restore_btn_frame,
            text="↩️ Restore Selected",
            command=self._restore_backup,
            font=('Segoe UI', 10, 'bold'),
            bg=BTN_DANGER_BG,
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
        ).pack(side=tk.LEFT)

    def _browse_credentials(self):
        path = filedialog.askopenfilename(
            title="Select Service Account JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            self.creds_path_entry.delete(0, tk.END)
            self.creds_path_entry.insert(0, path)

    def _get_config(self):
        """Get bucket and credentials. Returns (bucket, creds_json, creds_path) or None."""
        bucket = self.bucket_entry.get().strip()
        if not bucket:
            messagebox.showerror("Error", "Bucket name is required.")
            return None

        creds_path = self.creds_path_entry.get().strip()
        creds_text = self.creds_text.get("1.0", tk.END).strip()

        creds_json = None
        if creds_text:
            try:
                creds_json = json.loads(creds_text)
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid JSON in credentials field.")
                return None
        elif creds_path and os.path.isfile(creds_path):
            pass  # use creds_path
        else:
            messagebox.showerror("Error", "Provide credentials: select a JSON file or paste JSON content.")
            return None

        return (bucket, creds_json, creds_path if not creds_json else None)

    def _upload_backup(self):
        if not is_gcs_available():
            messagebox.showerror("Error", "Install: pip install google-cloud-storage")
            return
        cfg = self._get_config()
        if not cfg:
            return
        bucket, creds_json, creds_path = cfg
        try:
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
                tmp_path = tmp.name
            try:
                self.db.create_local_backup(tmp_path)
                service = GCSBackupService(bucket_name=bucket, credentials_json=creds_json, credentials_path=creds_path)
                name = create_backup_filename()
                service.upload_backup(tmp_path, name)
                messagebox.showinfo("Success", "Backup uploaded to Google Cloud successfully.")
                self._list_backups()
            finally:
                if os.path.isfile(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass
        except Exception as e:
            log_error("Backup upload error", e)
            messagebox.showerror("Error", str(e))

    def _list_backups(self):
        if not is_gcs_available():
            messagebox.showerror("Error", "Install: pip install google-cloud-storage")
            return
        cfg = self._get_config()
        if not cfg:
            return
        bucket, creds_json, creds_path = cfg
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            service = GCSBackupService(bucket_name=bucket, credentials_json=creds_json, credentials_path=creds_path)
            backups = service.list_backups()
            for b in backups:
                date_str = b.get('updated', '-')
                if date_str and date_str != '-':
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d %H:%M')
                    except Exception:
                        pass
                size = b.get('size', 0) or 0
                if size >= 1024 * 1024:
                    size_str = f"{size / (1024*1024):.1f} MB"
                elif size >= 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size} B"
                self.tree.insert('', tk.END, values=(b['name'], date_str, size_str, b['full_path']))
        except Exception as e:
            log_error("List backups error", e)
            messagebox.showerror("Error", str(e))

    def _on_select(self, event):
        sel = self.tree.selection()
        if sel:
            item = self.tree.item(sel[0])
            vals = item.get('values', ())
            self.selected_backup = vals[3] if len(vals) > 3 else None
        else:
            self.selected_backup = None

    def _restore_backup(self):
        if not self.selected_backup:
            messagebox.showwarning("No Selection", "Select a backup from the list first.")
            return
        if not messagebox.askyesno("Confirm Restore", "This will replace your current database. Continue?"):
            return
        if not is_gcs_available():
            messagebox.showerror("Error", "Install: pip install google-cloud-storage")
            return
        cfg = self._get_config()
        if not cfg:
            return
        bucket, creds_json, creds_path = cfg
        try:
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
                tmp_path = tmp.name
            try:
                service = GCSBackupService(bucket_name=bucket, credentials_json=creds_json, credentials_path=creds_path)
                service.download_backup(self.selected_backup, tmp_path)
                success = self.db.restore_from_file(tmp_path)
                if success:
                    messagebox.showinfo("Success", "Database restored. The application will close. Please start it again.")
                    self.root.destroy()
                else:
                    messagebox.showerror("Error", "Restore failed.")
            finally:
                if os.path.isfile(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass
        except Exception as e:
            log_error("Restore error", e)
            messagebox.showerror("Error", str(e))
