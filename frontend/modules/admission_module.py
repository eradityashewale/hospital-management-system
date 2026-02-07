"""
Admission (IPD) Module - Daily Progress Notes

Allows admitting a patient and writing day-wise progress notes so doctors can
quickly review Day 1 / Day 2 / Day 3 changes and plans.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from backend.database import Database
from utils.helpers import generate_id, get_current_date, get_current_time
from utils.logger import log_info, log_error, log_button_click, log_dialog_open, log_dialog_close


class AdmissionNotesWindow:
    """Toplevel window to manage admissions and daily notes for a patient."""

    def __init__(self, parent, db: Database, patient_id: str):
        self.parent = parent
        self.db = db
        self.patient_id = patient_id

        self.patient = self.db.get_patient_by_id(patient_id)
        if not self.patient:
            messagebox.showerror("Error", "Patient not found")
            return

        self.window = tk.Toplevel(parent)
        self.window.title("IPD Admission - Daily Notes")
        self.window.configure(bg="#f5f7fa")
        self.window.transient(parent)
        self.window.lift()
        self.window.focus_force()
        # Maximize window on Windows
        try:
            self.window.state('zoomed')
        except:
            # Fallback for non-Windows systems
            self.window.attributes('-zoomed', True)

        self.selected_admission_id = None
        self.admissions = []

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = tk.Label(
            self.window,
            text=f"IPD / Daily Notes — {self.patient.get('first_name','')} {self.patient.get('last_name','')} ({self.patient_id})",
            font=("Segoe UI", 18, "bold"),
            bg="#f5f7fa",
            fg="#1a237e",
        )
        header.pack(pady=16)

        top = tk.Frame(self.window, bg="#f5f7fa")
        top.pack(fill=tk.X, padx=18, pady=(0, 12))

        tk.Label(top, text="Admission:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").pack(side=tk.LEFT, padx=(0, 8))
        self.admission_var = tk.StringVar()
        self.admission_combo = ttk.Combobox(top, textvariable=self.admission_var, state="readonly", width=60)
        self.admission_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.admission_combo.bind("<<ComboboxSelected>>", lambda e: self._on_select_admission())

        self.status_label = tk.Label(top, text="", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#10b981")
        self.status_label.pack(side=tk.LEFT, padx=(10, 10))

        main = tk.Frame(self.window, bg="#f5f7fa")
        main.pack(fill=tk.BOTH, expand=True, padx=18, pady=12)

        left = tk.Frame(main, bg="#f5f7fa")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(left, text="Daily Progress Notes", font=("Segoe UI", 12, "bold"), bg="#f5f7fa", fg="#374151").pack(anchor="w", pady=(0, 8))

        cols = ("Day", "Date", "Time", "By", "Note")
        self.notes_tree = ttk.Treeview(left, columns=cols, show="headings", height=16)
        for c in cols:
            self.notes_tree.heading(c, text=c)
        self.notes_tree.column("Day", width=60, anchor="center")
        self.notes_tree.column("Date", width=110, anchor="center")
        self.notes_tree.column("Time", width=80, anchor="center")
        self.notes_tree.column("By", width=140, anchor="w")
        self.notes_tree.column("Note", width=480, anchor="w")

        vsb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.notes_tree.yview)
        self.notes_tree.configure(yscrollcommand=vsb.set)
        self.notes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        right = tk.Frame(main, bg="#f5f7fa")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        tk.Label(right, text="Add / Update Today's Note", font=("Segoe UI", 12, "bold"), bg="#f5f7fa", fg="#374151").pack(anchor="w", pady=(0, 8))

        form = tk.Frame(right, bg="#f5f7fa")
        form.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Date:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").grid(row=0, column=0, sticky="w", pady=6)
        self.note_date_var = tk.StringVar(value=get_current_date())
        tk.Entry(form, textvariable=self.note_date_var, width=18).grid(row=0, column=1, sticky="w", padx=(8, 0), pady=6)

        tk.Label(form, text="Written by:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").grid(row=1, column=0, sticky="w", pady=6)
        self.created_by_var = tk.StringVar()
        tk.Entry(form, textvariable=self.created_by_var, width=28).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=6)

        tk.Label(right, text="Note (Day-wise):", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").pack(anchor="w", pady=(6, 4))
        self.note_text = tk.Text(right, height=14, width=36, wrap="word")
        self.note_text.pack(fill=tk.BOTH, expand=True)

        btns = tk.Frame(right, bg="#f5f7fa")
        btns.pack(fill=tk.X, pady=10)

        self.save_note_btn = tk.Button(
            btns,
            text="Save Note",
            command=self.save_note,
            font=("Segoe UI", 10, "bold"),
            bg="#3b82f6",
            fg="white",
            padx=18,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#2563eb",
            activeforeground="white",
        )
        self.save_note_btn.pack(side=tk.LEFT)

        tk.Button(
            btns,
            text="Refresh",
            command=self.refresh,
            font=("Segoe UI", 10, "bold"),
            bg="#6b7280",
            fg="white",
            padx=18,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#4b5563",
            activeforeground="white",
        ).pack(side=tk.LEFT, padx=8)

    def refresh(self):
        """Reload admissions and notes."""
        try:
            self.admissions = self.db.get_admissions_by_patient(self.patient_id)

            combo_items = []
            active_adm = None
            for a in self.admissions:
                label = f"{a['admission_id']}  |  {a.get('admission_date','')}  |  {a.get('status','')}"
                if a.get('doctor_name'):
                    label += f"  |  Dr. {a.get('doctor_name')}"
                combo_items.append(label)
                if a.get("status") == "Admitted" and not active_adm:
                    active_adm = a

            self.admission_combo["values"] = combo_items

            # Select active admission if exists, else most recent
            if active_adm:
                self._select_admission(active_adm["admission_id"])
            elif self.admissions:
                self._select_admission(self.admissions[0]["admission_id"])
            else:
                self.selected_admission_id = None
                self.admission_var.set("")
                self.status_label.config(text="No admissions yet", fg="#ef4444")
                self._refresh_notes_tree([])
                self._set_note_entry_enabled(False)
        except Exception as e:
            log_error("Failed to refresh IPD admissions", e)
            messagebox.showerror("Error", f"Failed to load admissions: {e}")

    def _select_admission(self, admission_id: str):
        self.selected_admission_id = admission_id
        # Update combo selection text
        for idx, a in enumerate(self.admissions):
            if a["admission_id"] == admission_id:
                self.admission_combo.current(idx)
                break
        self._on_select_admission()

    def _on_select_admission(self):
        try:
            idx = self.admission_combo.current()
            if idx < 0 or idx >= len(self.admissions):
                return
            admission = self.admissions[idx]
            self.selected_admission_id = admission["admission_id"]

            status = admission.get("status", "")
            if status == "Admitted":
                self.status_label.config(text="ACTIVE (Admitted)", fg="#10b981")
                self._set_note_entry_enabled(True)
            else:
                self.status_label.config(text=f"{status}", fg="#6b7280")
                self._set_note_entry_enabled(False)

            notes = self.db.get_admission_notes(self.selected_admission_id)
            self._refresh_notes_tree(notes)
        except Exception as e:
            log_error("Failed selecting admission", e)
            messagebox.showerror("Error", f"Failed to load notes: {e}")

    def _refresh_notes_tree(self, notes):
        for item in self.notes_tree.get_children():
            self.notes_tree.delete(item)
        for n in notes:
            day = n.get("day_number", "")
            date = n.get("note_date", "")
            time = n.get("note_time", "") or ""
            by = n.get("created_by", "")
            note = (n.get("note_text", "") or "").replace("\n", " ").strip()
            if len(note) > 140:
                note = note[:140] + "..."
            self.notes_tree.insert("", "end", values=(day, date, time, by, note))

    def _set_note_entry_enabled(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        try:
            self.save_note_btn.config(state=tk.NORMAL if enabled else tk.DISABLED)
            self.note_text.config(state=state)
        except Exception:
            pass

    def open_admit_dialog(self):
        """Open dialog to admit this patient."""
        log_button_click("Admit", "AdmissionNotesWindow")
        log_dialog_open("Admit Patient")

        dialog = tk.Toplevel(self.window)
        dialog.title("Admit Patient (IPD)")
        dialog.geometry("520x420")
        dialog.configure(bg="#f5f7fa")
        dialog.transient(self.window)
        dialog.lift()
        dialog.focus_force()

        frm = tk.Frame(dialog, bg="#f5f7fa")
        frm.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        # Patient context (read-only)
        patient_name = f"{self.patient.get('first_name','')} {self.patient.get('last_name','')}".strip()
        if not patient_name:
            patient_name = "(Unknown)"
        tk.Label(
            frm,
            text=f"Patient: {patient_name} ({self.patient_id})",
            font=("Segoe UI", 11, "bold"),
            bg="#f5f7fa",
            fg="#1a237e",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        doctors = self.db.get_all_doctors()
        doctor_labels = ["(None)"] + [f"{d['doctor_id']} - Dr. {d['first_name']} {d['last_name']}" for d in doctors]

        tk.Label(frm, text="Assigned Doctor (optional):", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").grid(row=1, column=0, sticky="w", pady=8)
        doctor_var = tk.StringVar(value=doctor_labels[0])
        doctor_combo = ttk.Combobox(frm, textvariable=doctor_var, values=doctor_labels, state="readonly", width=34)
        doctor_combo.grid(row=1, column=1, sticky="w", pady=8)

        tk.Label(frm, text="Admission Date:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").grid(row=2, column=0, sticky="w", pady=8)
        adm_date_var = tk.StringVar(value=get_current_date())
        tk.Entry(frm, textvariable=adm_date_var, width=18).grid(row=2, column=1, sticky="w", pady=8)

        tk.Label(frm, text="Expected Days:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").grid(row=3, column=0, sticky="w", pady=8)
        exp_days_var = tk.StringVar(value="3")
        tk.Entry(frm, textvariable=exp_days_var, width=10).grid(row=3, column=1, sticky="w", pady=8)

        tk.Label(frm, text="Ward:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").grid(row=4, column=0, sticky="w", pady=8)
        ward_var = tk.StringVar()
        tk.Entry(frm, textvariable=ward_var, width=22).grid(row=4, column=1, sticky="w", pady=8)

        tk.Label(frm, text="Bed:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").grid(row=5, column=0, sticky="w", pady=8)
        bed_var = tk.StringVar()
        tk.Entry(frm, textvariable=bed_var, width=22).grid(row=5, column=1, sticky="w", pady=8)

        tk.Label(frm, text="Reason / Diagnosis:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").grid(row=6, column=0, sticky="nw", pady=8)
        reason_txt = tk.Text(frm, height=5, width=34, wrap="word")
        reason_txt.grid(row=6, column=1, sticky="w", pady=8)

        btns = tk.Frame(frm, bg="#f5f7fa")
        btns.grid(row=7, column=0, columnspan=2, sticky="w", pady=(14, 0))

        def do_save():
            try:
                # Prevent multiple active admissions (simple rule)
                active = self.db.get_active_admission_by_patient(self.patient_id)
                if active:
                    messagebox.showwarning("Already Admitted", f"Patient already has an active admission: {active['admission_id']}")
                    return

                doctor_id = None
                if doctor_var.get() != "(None)":
                    doctor_id = doctor_var.get().split(" - ", 1)[0].strip()

                admission_id = generate_id("ADM")
                data = {
                    "admission_id": admission_id,
                    "patient_id": self.patient_id,
                    "doctor_id": doctor_id,
                    "admission_date": adm_date_var.get().strip(),
                    "expected_days": exp_days_var.get().strip(),
                    "ward": ward_var.get().strip(),
                    "bed": bed_var.get().strip(),
                    "reason": reason_txt.get("1.0", "end").strip(),
                }

                if not data["admission_date"]:
                    messagebox.showerror("Error", "Admission date is required")
                    return

                ok = self.db.add_admission(data)
                if ok:
                    log_info(f"Admitted patient {self.patient_id} => {admission_id}")
                    messagebox.showinfo("Success", f"Patient admitted: {admission_id}")
                    log_dialog_close("Admit Patient")
                    dialog.destroy()
                    self.refresh()
                else:
                    messagebox.showerror("Error", "Failed to admit patient")
            except Exception as e:
                log_error("Admit failed", e)
                messagebox.showerror("Error", f"Failed to admit patient: {e}")

        tk.Button(
            btns,
            text="Save Admission",
            command=do_save,
            font=("Segoe UI", 10, "bold"),
            bg="#10b981",
            fg="white",
            padx=16,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#059669",
            activeforeground="white",
        ).pack(side=tk.LEFT)

        tk.Button(
            btns,
            text="Cancel",
            command=lambda: (log_dialog_close("Admit Patient"), dialog.destroy()),
            font=("Segoe UI", 10, "bold"),
            bg="#6b7280",
            fg="white",
            padx=16,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#4b5563",
            activeforeground="white",
        ).pack(side=tk.LEFT, padx=8)

    def open_discharge_dialog(self):
        """Discharge the currently selected admission."""
        if not self.selected_admission_id:
            return
        idx = self.admission_combo.current()
        if idx < 0:
            return
        admission = self.admissions[idx]
        if admission.get("status") != "Admitted":
            return

        log_button_click("Discharge", "AdmissionNotesWindow")
        log_dialog_open("Discharge Patient")

        dialog = tk.Toplevel(self.window)
        dialog.title("Discharge Patient")
        dialog.geometry("520x360")
        dialog.configure(bg="#f5f7fa")
        dialog.transient(self.window)
        dialog.lift()
        dialog.focus_force()

        frm = tk.Frame(dialog, bg="#f5f7fa")
        frm.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        tk.Label(frm, text=f"Admission: {admission['admission_id']}", font=("Segoe UI", 11, "bold"), bg="#f5f7fa", fg="#1a237e").pack(anchor="w", pady=(0, 10))

        row = tk.Frame(frm, bg="#f5f7fa")
        row.pack(fill=tk.X, pady=6)
        tk.Label(row, text="Discharge Date:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").pack(side=tk.LEFT)
        discharge_date_var = tk.StringVar(value=get_current_date())
        tk.Entry(row, textvariable=discharge_date_var, width=18).pack(side=tk.LEFT, padx=10)

        tk.Label(frm, text="Discharge Summary:", font=("Segoe UI", 10, "bold"), bg="#f5f7fa", fg="#374151").pack(anchor="w", pady=(10, 4))
        summary = tk.Text(frm, height=8, width=48, wrap="word")
        summary.pack(fill=tk.BOTH, expand=True)

        btns = tk.Frame(frm, bg="#f5f7fa")
        btns.pack(fill=tk.X, pady=12)

        def do_discharge():
            try:
                ok = self.db.discharge_admission(
                    admission["admission_id"],
                    discharge_date=discharge_date_var.get().strip(),
                    discharge_summary=summary.get("1.0", "end").strip(),
                )
                if ok:
                    messagebox.showinfo("Success", "Patient discharged successfully")
                    log_dialog_close("Discharge Patient")
                    dialog.destroy()
                    self.refresh()
                else:
                    messagebox.showerror("Error", "Failed to discharge")
            except Exception as e:
                log_error("Discharge failed", e)
                messagebox.showerror("Error", f"Failed to discharge: {e}")

        tk.Button(
            btns,
            text="Confirm Discharge",
            command=do_discharge,
            font=("Segoe UI", 10, "bold"),
            bg="#ef4444",
            fg="white",
            padx=16,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#dc2626",
            activeforeground="white",
        ).pack(side=tk.LEFT)

        tk.Button(
            btns,
            text="Cancel",
            command=lambda: (log_dialog_close("Discharge Patient"), dialog.destroy()),
            font=("Segoe UI", 10, "bold"),
            bg="#6b7280",
            fg="white",
            padx=16,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#4b5563",
            activeforeground="white",
        ).pack(side=tk.LEFT, padx=8)

    def save_note(self):
        """Save a new daily note for the selected active admission."""
        if not self.selected_admission_id:
            messagebox.showwarning("No Admission", "Please admit the patient first (or select an admission).")
            return

        idx = self.admission_combo.current()
        if idx < 0:
            return
        admission = self.admissions[idx]
        if admission.get("status") != "Admitted":
            messagebox.showwarning("Discharged", "This admission is discharged. Notes are read-only.")
            return

        note_text = self.note_text.get("1.0", "end").strip()
        if not note_text:
            messagebox.showwarning("Empty Note", "Please write a note first.")
            return

        note_date = self.note_date_var.get().strip()
        if not note_date:
            messagebox.showerror("Error", "Note date is required (YYYY-MM-DD).")
            return

        data = {
            "note_id": generate_id("ADN"),
            "admission_id": self.selected_admission_id,
            "note_date": note_date,
            "note_time": get_current_time(),
            "note_text": note_text,
            "created_by": self.created_by_var.get().strip(),
        }

        try:
            ok = self.db.add_admission_note(data)
            if ok:
                messagebox.showinfo("Saved", "Daily note saved.")
                self.note_text.delete("1.0", "end")
                self._on_select_admission()
            else:
                messagebox.showerror("Error", "Failed to save note.")
        except Exception as e:
            log_error("Save note failed", e)
            messagebox.showerror("Error", f"Failed to save note: {e}")


