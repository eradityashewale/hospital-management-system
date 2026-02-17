"""
Patient Documents PDF Generator

Generates PDFs for all patient-related documents: bills, prescriptions, IPD reports.
Used by the "Print All Documents" feature in the Patient module.
"""
import os
from datetime import datetime
from typing import Optional

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def _get_pdf_styles():
    """Shared PDF styles for all document types."""
    styles = getSampleStyleSheet()
    return {
        'heading': ParagraphStyle(
            'CustomHeading', parent=styles['Heading2'],
            fontSize=12, textColor=colors.HexColor('#1a237e'),
            spaceAfter=6, spaceBefore=12, fontName='Helvetica-Bold'
        ),
        'normal': ParagraphStyle(
            'CustomNormal', parent=styles['Normal'],
            fontSize=10, textColor=colors.black, spaceAfter=6, fontName='Helvetica'
        ),
    }


def _format_date(date_str: str) -> str:
    """Format YYYY-MM-DD to DD.MM.YYYY."""
    if not date_str:
        return ''
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d.%m.%Y')
    except (ValueError, TypeError):
        return date_str


def generate_bill_pdf(db, bill: dict, filepath: str) -> bool:
    """Generate PDF for a bill. Returns True on success."""
    if not REPORTLAB_AVAILABLE:
        return False
    try:
        patient = db.get_patient_by_id(bill['patient_id'])
        if not patient:
            return False
        patient_name = bill.get('patient_name') or f"{patient['first_name']} {patient['last_name']}"
        doctor = None
        if bill.get('appointment_id'):
            apt = db.get_appointment_by_id(bill['appointment_id'])
            if apt and apt.get('doctor_id'):
                doctor = db.get_doctor_by_id(apt['doctor_id'])
        if not doctor:
            doctors = db.get_all_doctors()
            doctor = doctors[0] if doctors else None
        return _build_bill_pdf(bill, patient, patient_name, doctor, filepath)
    except Exception:
        return False


def _build_bill_elements(bill, patient, patient_name, doctor):
    """Return list of flowables for a bill (for merging into one PDF)."""
    s = _get_pdf_styles()
    elements = []

    doctor_name = "Dr. Hospital"
    doctor_qual, doctor_spec = "MBBS", "General"
    if doctor:
        doctor_name = f"Dr. {doctor.get('first_name', '')} {doctor.get('last_name', '')}".strip() or doctor_name
        doctor_qual = doctor.get('qualification') or doctor_qual
        doctor_spec = doctor.get('specialization') or doctor_spec
    patient_age = ""
    if patient.get('date_of_birth'):
        try:
            dob = datetime.strptime(patient['date_of_birth'], '%Y-%m-%d')
            patient_age = str((datetime.now() - dob).days // 365)
        except (ValueError, TypeError):
            pass
    formatted_date = _format_date(bill.get('bill_date', ''))
    bill_id = bill.get('bill_id', '')

    header_data = [[
        Paragraph(f"<b>{doctor_name}</b><br/>{doctor_qual}<br/>Specialization: {doctor_spec}", s['normal']),
        Paragraph(f"<b>BILL / INVOICE</b><br/>Date: {formatted_date}<br/>Bill ID: {bill_id}", s['normal'])
    ]]
    header_table = Table(header_data, colWidths=[90*mm, 90*mm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8*mm))

    patient_info = [['Name:', patient_name.upper()], ['Age/Gender:', f"{patient_age}/{patient.get('gender','')}" if patient_age else patient.get('gender','')],
                    ['Patient ID:', bill.get('patient_id','')]]
    pt = Table(patient_info, colWidths=[30*mm, 150*mm])
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(Paragraph("<b>PATIENT INFORMATION</b>", s['heading']))
    elements.append(pt)
    elements.append(Spacer(1, 6*mm))

    elements.append(Paragraph("<b>CHARGES</b>", s['heading']))
    charges_data = [['R', 'Description', 'Amount']]
    row_n = 1
    for label, key in [('Consultation Fee', 'consultation_fee'), ('Medicine Cost', 'medicine_cost'), ('Other Charges', 'other_charges')]:
        val = bill.get(key, 0) or 0
        if val > 0:
            charges_data.append([str(row_n), label, f"${float(val):,.2f}"])
            row_n += 1
    if row_n == 1:
        charges_data.append(['1', 'Consultation Fee', f"${float(bill.get('consultation_fee',0)):,.2f}"])
    ct = Table(charges_data, colWidths=[8*mm, 120*mm, 52*mm])
    ct.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))
    elements.append(ct)
    elements.append(Paragraph(f"<b>Total Amount: ${float(bill.get('total_amount',0)):,.2f}</b>", s['normal']))
    elements.append(Paragraph(f"<b>Payment:</b> {bill.get('payment_status','')} | {bill.get('payment_method','')}", s['normal']))
    elements.append(Table([['Signature: _________________________', f'Date: {formatted_date}']], colWidths=[90*mm, 90*mm]))
    return elements


def _build_bill_pdf(bill, patient, patient_name, doctor, filepath):
    """Build bill PDF to file (standalone)."""
    elements = _build_bill_elements(bill, patient, patient_name, doctor)
    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)
    doc.build(elements)
    return True


def generate_prescription_pdf(db, prescription: dict, items: list, filepath: str) -> bool:
    """Generate PDF for a prescription. Returns True on success."""
    if not REPORTLAB_AVAILABLE:
        return False
    try:
        patient = db.get_patient_by_id(prescription.get('patient_id'))
        doctor = db.get_doctor_by_id(prescription.get('doctor_id'))
        if not patient or not doctor:
            return False
        return _build_prescription_pdf(prescription, items, patient, doctor, filepath)
    except Exception:
        return False


def _build_prescription_elements(prescription, items, patient, doctor):
    """Return list of flowables for a prescription (for merging into one PDF)."""
    s = _get_pdf_styles()
    elements = []

    patient_name = f"{patient.get('first_name','')} {patient.get('last_name','')}".strip().upper()
    prescription_date = prescription.get('prescription_date', '')
    formatted_date = _format_date(prescription_date)
    prescription_id = prescription.get('prescription_id', '')

    header_data = [[
        Paragraph(f"<b>Dr. {doctor.get('first_name','')} {doctor.get('last_name','')}</b><br/>"
                  f"{doctor.get('qualification','')}<br/>Specialization: {doctor.get('specialization','')}", s['normal']),
        Paragraph(f"<b>PRESCRIPTION</b><br/>Date: {formatted_date}<br/>ID: {prescription_id}", s['normal'])
    ]]
    header_table = Table(header_data, colWidths=[90*mm, 90*mm])
    header_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTSIZE', (0, 0), (-1, -1), 10)]))
    elements.append(header_table)
    elements.append(Spacer(1, 8*mm))

    patient_age = ""
    if patient.get('date_of_birth'):
        try:
            dob = datetime.strptime(patient['date_of_birth'], '%Y-%m-%d')
            patient_age = str((datetime.now() - dob).days // 365)
        except (ValueError, TypeError):
            pass
    pt_info = [['Name:', patient_name], ['Age/Gender:', f"{patient_age}/{patient.get('gender','')}" if patient_age else patient.get('gender','')],
               ['Patient ID:', prescription.get('patient_id','')]]
    pt = Table(pt_info, colWidths=[30*mm, 150*mm])
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(Paragraph("<b>PATIENT INFORMATION</b>", s['heading']))
    elements.append(pt)
    elements.append(Spacer(1, 6*mm))

    diagnosis = prescription.get('diagnosis', '')
    if diagnosis:
        elements.append(Paragraph("<b>DIAGNOSIS</b>", s['heading']))
        elements.append(Paragraph(diagnosis.replace('\n', '<br/>'), s['normal']))
        elements.append(Spacer(1, 6*mm))

    if items:
        elements.append(Paragraph("<b>PRESCRIBED MEDICINES</b>", s['heading']))
        med_data = [['R', 'Medicine', 'Type', 'Dosage', 'Frequency', 'Duration', 'Instructions']]
        for idx, it in enumerate(items, 1):
            med_data.append([
                str(idx), it.get('medicine_name',''), it.get('medicine_type',''), it.get('dosage',''),
                it.get('frequency',''), it.get('duration',''), it.get('instructions','')
            ])
        mt = Table(med_data, colWidths=[8*mm, 40*mm, 20*mm, 22*mm, 25*mm, 22*mm, 43*mm])
        mt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 9), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(mt)
    notes = prescription.get('notes', '')
    if notes:
        elements.append(Paragraph("<b>DOCTOR'S NOTES</b>", s['heading']))
        elements.append(Paragraph(notes.replace('\n', '<br/>'), s['normal']))
    elements.append(Table([['Signature: _________________________', f'Date: {formatted_date}']], colWidths=[90*mm, 90*mm]))
    return elements


def _build_prescription_pdf(prescription, items, patient, doctor, filepath):
    """Build prescription PDF to file (standalone)."""
    elements = _build_prescription_elements(prescription, items, patient, doctor)
    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)
    doc.build(elements)
    return True


def generate_ipd_report_pdf(db, admission: dict, notes: list, patient: dict, filepath: str) -> bool:
    """Generate PDF for IPD admission report with daily notes. Returns True on success."""
    if not REPORTLAB_AVAILABLE:
        return False
    try:
        return _build_ipd_report_pdf(admission, notes, patient, filepath)
    except Exception:
        return False


def _build_ipd_report_elements(admission, notes, patient):
    """Return list of flowables for IPD report (for merging into one PDF)."""
    s = _get_pdf_styles()
    elements = []

    patient_name = f"{patient.get('first_name','')} {patient.get('last_name','')}".strip().upper()
    admission_id = admission.get('admission_id', '')
    adm_date = _format_date(admission.get('admission_date', ''))
    status = admission.get('status', '')
    doctor_name = admission.get('doctor_name', '') or 'N/A'

    header_data = [[
        Paragraph(f"<b>IPD ADMISSION REPORT</b>", s['heading']),
        Paragraph(f"Admission ID: {admission_id}<br/>Date: {adm_date}<br/>Status: {status}", s['normal'])
    ]]
    header_table = Table(header_data, colWidths=[90*mm, 90*mm])
    header_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTSIZE', (0, 0), (-1, -1), 10)]))
    elements.append(header_table)
    elements.append(Spacer(1, 8*mm))

    pt_info = [['Patient Name:', patient_name], ['Patient ID:', patient.get('patient_id','')],
               ['Doctor:', f"Dr. {doctor_name}"], ['Ward/Bed:', f"{admission.get('ward','')} / {admission.get('bed','')}"]]
    pt = Table(pt_info, colWidths=[35*mm, 145*mm])
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(Paragraph("<b>PATIENT INFORMATION</b>", s['heading']))
    elements.append(pt)
    elements.append(Spacer(1, 6*mm))

    reason = admission.get('reason', '')
    if reason:
        elements.append(Paragraph("<b>REASON / DIAGNOSIS</b>", s['heading']))
        elements.append(Paragraph(reason.replace('\n', '<br/>'), s['normal']))
        elements.append(Spacer(1, 6*mm))

    if notes:
        elements.append(Paragraph("<b>DAILY PROGRESS NOTES</b>", s['heading']))
        notes_data = [['Day', 'Date', 'Time', 'By', 'Note']]
        for n in notes:
            note_text = (n.get('note_text', '') or '').replace('\n', ' ')
            if len(note_text) > 200:
                note_text = note_text[:200] + '...'
            notes_data.append([
                str(n.get('day_number', '')), n.get('note_date', ''), n.get('note_time', ''),
                n.get('created_by', ''), note_text
            ])
        nt = Table(notes_data, colWidths=[15*mm, 30*mm, 25*mm, 40*mm, 90*mm])
        nt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 9), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(nt)
    discharge = admission.get('discharge_summary', '')
    if discharge:
        elements.append(Spacer(1, 6*mm))
        elements.append(Paragraph("<b>DISCHARGE SUMMARY</b>", s['heading']))
        elements.append(Paragraph(discharge.replace('\n', '<br/>'), s['normal']))
    elements.append(Spacer(1, 8*mm))
    elements.append(Table([['Signature: _________________________', f'Date: {_format_date(admission.get('discharge_date') or admission.get('admission_date', ''))}']], colWidths=[90*mm, 90*mm]))
    return elements


def _build_ipd_report_pdf(admission, notes, patient, filepath):
    """Build IPD report PDF to file (standalone)."""
    elements = _build_ipd_report_elements(admission, notes, patient)
    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)
    doc.build(elements)
    return True


def print_all_patient_documents(parent, db, patient_id: str) -> Optional[list]:
    """
    Generate all patient documents (bills, prescriptions, IPD reports) into ONE merged PDF file.
    Returns the file path if successful, or None if cancelled/error.
    """
    from tkinter import filedialog, messagebox

    if not REPORTLAB_AVAILABLE:
        messagebox.showerror("Error", "reportlab is not installed. Run: pip install reportlab")
        return None

    patient = db.get_patient_by_id(patient_id)
    if not patient:
        messagebox.showerror("Error", "Patient not found")
        return None

    default_name = f"Patient_{patient_id}_All_Documents.pdf"

    filepath = filedialog.asksaveasfilename(
        title="Save merged PDF",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        initialfile=default_name,
    )
    if not filepath:
        return None

    all_elements = []
    doc_count = 0

    # Bills
    bills = db.get_bills_by_patient_id(patient_id)
    for bill in bills:
        patient_ref = db.get_patient_by_id(bill['patient_id'])
        if not patient_ref:
            continue
        patient_name_val = bill.get('patient_name') or f"{patient_ref['first_name']} {patient_ref['last_name']}"
        doctor = None
        if bill.get('appointment_id'):
            apt = db.get_appointment_by_id(bill['appointment_id'])
            if apt and apt.get('doctor_id'):
                doctor = db.get_doctor_by_id(apt['doctor_id'])
        if not doctor:
            doctors = db.get_all_doctors()
            doctor = doctors[0] if doctors else None
        if doc_count > 0:
            all_elements.append(PageBreak())
        all_elements.extend(_build_bill_elements(bill, patient_ref, patient_name_val, doctor))
        doc_count += 1

    # Prescriptions
    prescriptions = db.get_prescriptions_by_patient(patient_id)
    for rx in prescriptions:
        patient_ref = db.get_patient_by_id(rx.get('patient_id'))
        if not patient_ref:
            continue
        doctor = db.get_doctor_by_id(rx.get('doctor_id'))
        if not doctor:
            doctors = db.get_all_doctors()
            doctor = doctors[0] if doctors else {}
        items = db.get_prescription_items(rx.get('prescription_id', ''))
        if doc_count > 0:
            all_elements.append(PageBreak())
        all_elements.extend(_build_prescription_elements(rx, items, patient_ref, doctor or {}))
        doc_count += 1

    # IPD reports
    admissions = db.get_admissions_by_patient(patient_id)
    for adm in admissions:
        notes = db.get_admission_notes(adm.get('admission_id', ''))
        if doc_count > 0:
            all_elements.append(PageBreak())
        all_elements.extend(_build_ipd_report_elements(adm, notes, patient))
        doc_count += 1

    if not all_elements:
        messagebox.showwarning("No Documents", "No documents were found for this patient.")
        return []

    try:
        doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm,
                               topMargin=15*mm, bottomMargin=15*mm)
        doc.build(all_elements)
        messagebox.showinfo("Success", f"Generated 1 PDF with {doc_count} document(s) successfully!\n\n{filepath}")
        return [filepath]
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate PDF: {e}")
        return []
