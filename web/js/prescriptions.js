/**
 * Prescription Management Module
 * Handles prescription list, add, edit, and filter operations
 */

let prescriptionItems = []; // Temporary storage for prescription items being added

async function showPrescriptions() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Prescription Management</h2>
        <div style="display: flex; justify-content: space-between; margin: 20px 0; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <input type="text" id="prescription-search" placeholder="Search by patient name..." 
                       style="padding: 10px; width: 250px; border: 1px solid #ddd; border-radius: 5px;"
                       onkeyup="searchPrescriptions()">
                <input type="date" id="prescription-date-filter" 
                       style="padding: 10px; border: 1px solid #ddd; border-radius: 5px;"
                       onchange="filterPrescriptionsByDate()">
                <button onclick="loadPrescriptions()" style="padding: 10px 15px;">Reset Filters</button>
            </div>
            <button onclick="showAddPrescriptionForm()" class="btn-success">+ New Prescription</button>
        </div>
        <div id="prescriptions-list">Loading...</div>
    `;
    await loadPrescriptions();
}

async function loadPrescriptions() {
    try {
        const result = await PrescriptionAPI.getAll();
        displayPrescriptions(result.prescriptions);
    } catch (error) {
        document.getElementById('prescriptions-list').innerHTML = 
            '<p style="color: red;">Error loading prescriptions: ' + error.message + '</p>';
    }
}

async function searchPrescriptions() {
    const query = document.getElementById('prescription-search').value;
    const date = document.getElementById('prescription-date-filter').value;
    
    try {
        let url = '/prescriptions?';
        const params = [];
        
        if (query) params.push(`patient_name=${encodeURIComponent(query)}`);
        if (date) params.push(`date=${date}`);
        
        if (params.length > 0) {
            url += params.join('&');
        } else {
            url = '/prescriptions';
        }
        
        const result = await apiCall(url);
        displayPrescriptions(result.prescriptions);
    } catch (error) {
        console.error('Search error:', error);
        document.getElementById('prescriptions-list').innerHTML = 
            '<p style="color: red;">Error searching prescriptions: ' + error.message + '</p>';
    }
}

async function filterPrescriptionsByDate() {
    searchPrescriptions();
}

function displayPrescriptions(prescriptions) {
    const listDiv = document.getElementById('prescriptions-list');
    
    if (!prescriptions || prescriptions.length === 0) {
        listDiv.innerHTML = '<p>No prescriptions found.</p>';
        return;
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>Prescription ID</th>
                    <th>Patient Name</th>
                    <th>Doctor Name</th>
                    <th>Date</th>
                    <th>Diagnosis</th>
                    <th>Medicines</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    prescriptions.forEach(prescription => {
        const itemCount = prescription.items ? prescription.items.length : 0;
        
        html += `
            <tr>
                <td>${prescription.prescription_id || ''}</td>
                <td>${prescription.patient_name || 'N/A'}</td>
                <td>${prescription.doctor_name || 'N/A'}</td>
                <td>${prescription.prescription_date || ''}</td>
                <td>${prescription.diagnosis || 'N/A'}</td>
                <td>${itemCount} medicine(s)</td>
                <td>
                    <button onclick="viewPrescriptionDetails('${prescription.prescription_id}')">View</button>
                    <button onclick="editPrescription('${prescription.prescription_id}')">Edit</button>
                </td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    listDiv.innerHTML = html;
}

async function showAddPrescriptionForm() {
    // Load patients, doctors, and appointments
    let patients = [];
    let doctors = [];
    let appointments = [];
    
    try {
        const patientsResult = await PatientAPI.getAll();
        patients = patientsResult.patients || [];
        
        const doctorsResult = await DoctorAPI.getAll();
        doctors = doctorsResult.doctors || [];
        
        const appointmentsResult = await AppointmentAPI.getAll();
        appointments = appointmentsResult.appointments || [];
    } catch (error) {
        alert('Error loading data: ' + error.message);
        return;
    }

    prescriptionItems = []; // Reset items

    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Create New Prescription</h2>
        <form id="prescription-form" onsubmit="savePrescription(event)">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <div class="form-group">
                        <label>Prescription ID *</label>
                        <input type="text" id="prescription_id" placeholder="Auto-generated if empty">
                        <small style="color: #666;">Leave empty to auto-generate</small>
                    </div>
                    
                    <div class="form-group">
                        <label>Patient *</label>
                        <select id="patient_id" required onchange="loadPatientAppointments()">
                            <option value="">Select Patient...</option>
                            ${patients.map(p => `<option value="${p.patient_id}">${p.patient_id} - ${p.first_name} ${p.last_name}</option>`).join('')}
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Doctor *</label>
                        <select id="doctor_id" required>
                            <option value="">Select Doctor...</option>
                            ${doctors.map(d => `<option value="${d.doctor_id}">${d.doctor_id} - ${d.first_name} ${d.last_name} (${d.specialization})</option>`).join('')}
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Appointment (Optional)</label>
                        <select id="appointment_id">
                            <option value="">No Appointment</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Prescription Date *</label>
                        <input type="date" id="prescription_date" required>
                    </div>
                </div>
                
                <div>
                    <div class="form-group">
                        <label>Diagnosis</label>
                        <textarea id="diagnosis" rows="3" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Notes</label>
                        <textarea id="notes" rows="3" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Vital Signs</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <input type="text" id="weight" placeholder="Weight (kg)">
                            <input type="text" id="height" placeholder="Height (cm)">
                            <input type="text" id="bp" placeholder="Blood Pressure">
                            <input type="text" id="spo2" placeholder="SpO2 (%)">
                            <input type="text" id="hr" placeholder="Heart Rate (bpm)">
                            <input type="text" id="rr" placeholder="Respiratory Rate">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Follow-up Date</label>
                        <input type="date" id="follow_up_date">
                    </div>
                </div>
            </div>
            
            <hr style="margin: 20px 0;">
            
            <h3>Medicines</h3>
            <div id="medicine-items" style="margin: 20px 0;">
                <p style="color: #666;">No medicines added yet. Click "Add Medicine" below.</p>
            </div>
            
            <div style="background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h4>Add Medicine</h4>
                <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                    <input type="text" id="medicine_name" placeholder="Medicine Name" 
                           onkeyup="searchMedicines(this.value)" list="medicine-list">
                    <datalist id="medicine-list"></datalist>
                    <input type="text" id="dosage" placeholder="Dosage (e.g., 500mg)">
                    <input type="text" id="frequency" placeholder="Frequency (e.g., 2x/day)">
                    <input type="text" id="duration" placeholder="Duration (e.g., 7 days)">
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                    <textarea id="instructions" rows="2" placeholder="Instructions (e.g., After meals)"></textarea>
                    <textarea id="purpose" rows="2" placeholder="Purpose (e.g., For fever)"></textarea>
                </div>
                <button type="button" onclick="addMedicineItem()" style="background: #4caf50;">Add Medicine</button>
            </div>
            
            <button type="submit" class="btn-success">Save Prescription</button>
            <button type="button" onclick="showPrescriptions()">Cancel</button>
        </form>
    `;
    
    // Set today's date as default
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('prescription_date').value = today;
    
    // Load medicine autocomplete
    loadMedicineAutocomplete();
}

async function loadMedicineAutocomplete() {
    try {
        const result = await MedicineAPI.getAutocomplete();
        const medicines = result.medicines || [];
        const datalist = document.getElementById('medicine-list');
        datalist.innerHTML = medicines.map(m => `<option value="${m}">`).join('');
    } catch (error) {
        console.error('Error loading medicines:', error);
    }
}

async function searchMedicines(query) {
    if (query.length < 2) return;
    try {
        const result = await MedicineAPI.search(query);
        const medicines = result.medicines || [];
        const datalist = document.getElementById('medicine-list');
        datalist.innerHTML = medicines.map(m => `<option value="${m.medicine_name || m}">`).join('');
    } catch (error) {
        console.error('Error searching medicines:', error);
    }
}

function addMedicineItem() {
    const medicineName = document.getElementById('medicine_name').value.trim();
    const dosage = document.getElementById('dosage').value.trim();
    const frequency = document.getElementById('frequency').value.trim();
    const duration = document.getElementById('duration').value.trim();
    const instructions = document.getElementById('instructions').value.trim();
    const purpose = document.getElementById('purpose').value.trim();
    
    if (!medicineName || !dosage || !frequency || !duration) {
        alert('Please fill in Medicine Name, Dosage, Frequency, and Duration');
        return;
    }
    
    const item = {
        medicine_name: medicineName,
        dosage: dosage,
        frequency: frequency,
        duration: duration,
        instructions: instructions,
        purpose: purpose
    };
    
    prescriptionItems.push(item);
    displayMedicineItems();
    
    // Clear form
    document.getElementById('medicine_name').value = '';
    document.getElementById('dosage').value = '';
    document.getElementById('frequency').value = '';
    document.getElementById('duration').value = '';
    document.getElementById('instructions').value = '';
    document.getElementById('purpose').value = '';
}

function displayMedicineItems() {
    const container = document.getElementById('medicine-items');
    
    if (prescriptionItems.length === 0) {
        container.innerHTML = '<p style="color: #666;">No medicines added yet. Click "Add Medicine" below.</p>';
        return;
    }
    
    let html = `
        <table>
            <thead>
                <tr>
                    <th>Medicine</th>
                    <th>Dosage</th>
                    <th>Frequency</th>
                    <th>Duration</th>
                    <th>Instructions</th>
                    <th>Purpose</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    prescriptionItems.forEach((item, index) => {
        html += `
            <tr>
                <td>${item.medicine_name}</td>
                <td>${item.dosage}</td>
                <td>${item.frequency}</td>
                <td>${item.duration}</td>
                <td>${item.instructions || '-'}</td>
                <td>${item.purpose || '-'}</td>
                <td><button onclick="removeMedicineItem(${index})" class="btn-danger">Remove</button></td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    container.innerHTML = html;
}

function removeMedicineItem(index) {
    prescriptionItems.splice(index, 1);
    displayMedicineItems();
}

async function loadPatientAppointments() {
    const patientId = document.getElementById('patient_id').value;
    if (!patientId) {
        document.getElementById('appointment_id').innerHTML = '<option value="">No Appointment</option>';
        return;
    }
    
    try {
        const result = await AppointmentAPI.getAll();
        const appointments = result.appointments || [];
        const patientAppointments = appointments.filter(a => a.patient_id === patientId);
        
        const select = document.getElementById('appointment_id');
        select.innerHTML = '<option value="">No Appointment</option>' +
            patientAppointments.map(a => 
                `<option value="${a.appointment_id}">${a.appointment_id} - ${a.appointment_date} ${a.appointment_time}</option>`
            ).join('');
    } catch (error) {
        console.error('Error loading appointments:', error);
    }
}

async function savePrescription(event) {
    event.preventDefault();
    
    if (prescriptionItems.length === 0) {
        alert('Please add at least one medicine to the prescription');
        return;
    }
    
    let prescriptionId = document.getElementById('prescription_id').value.trim();
    if (!prescriptionId) {
        prescriptionId = 'PRES' + Date.now().toString().slice(-8);
    }
    
    const prescriptionData = {
        prescription: {
            prescription_id: prescriptionId,
            patient_id: document.getElementById('patient_id').value,
            doctor_id: document.getElementById('doctor_id').value,
            appointment_id: document.getElementById('appointment_id').value || null,
            prescription_date: document.getElementById('prescription_date').value,
            diagnosis: document.getElementById('diagnosis').value || '',
            notes: document.getElementById('notes').value || '',
            weight: document.getElementById('weight').value || '',
            height: document.getElementById('height').value || '',
            bp: document.getElementById('bp').value || '',
            spo2: document.getElementById('spo2').value || '',
            hr: document.getElementById('hr').value || '',
            rr: document.getElementById('rr').value || '',
            follow_up_date: document.getElementById('follow_up_date').value || ''
        },
        items: prescriptionItems
    };

    try {
        await PrescriptionAPI.create(prescriptionData);
        alert('Prescription created successfully!');
        showPrescriptions();
    } catch (error) {
        alert('Error creating prescription: ' + error.message);
    }
}

async function viewPrescriptionDetails(prescriptionId) {
    try {
        const result = await PrescriptionAPI.getById(prescriptionId);
        const prescription = result.prescription;
        const items = prescription.items || [];
        
        const content = document.getElementById('content');
        content.innerHTML = `
            <h2>Prescription Details</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                <div style="background: #f9f9f9; padding: 20px; border-radius: 5px;">
                    <h3>Prescription Information</h3>
                    <p><strong>Prescription ID:</strong> ${prescription.prescription_id || 'N/A'}</p>
                    <p><strong>Patient:</strong> ${prescription.patient_name || 'N/A'}</p>
                    <p><strong>Doctor:</strong> ${prescription.doctor_name || 'N/A'}</p>
                    <p><strong>Date:</strong> ${prescription.prescription_date || 'N/A'}</p>
                    <p><strong>Diagnosis:</strong> ${prescription.diagnosis || 'N/A'}</p>
                    <p><strong>Notes:</strong> ${prescription.notes || 'N/A'}</p>
                </div>
                
                <div style="background: #f9f9f9; padding: 20px; border-radius: 5px;">
                    <h3>Vital Signs</h3>
                    <p><strong>Weight:</strong> ${prescription.weight || 'N/A'}</p>
                    <p><strong>Height:</strong> ${prescription.height || 'N/A'}</p>
                    <p><strong>Blood Pressure:</strong> ${prescription.bp || 'N/A'}</p>
                    <p><strong>SpO2:</strong> ${prescription.spo2 || 'N/A'}</p>
                    <p><strong>Heart Rate:</strong> ${prescription.hr || 'N/A'}</p>
                    <p><strong>Respiratory Rate:</strong> ${prescription.rr || 'N/A'}</p>
                    <p><strong>Follow-up Date:</strong> ${prescription.follow_up_date || 'N/A'}</p>
                </div>
            </div>
            
            <h3>Medicines (${items.length})</h3>
            ${items.length > 0 ? `
                <table style="margin-top: 20px;">
                    <thead>
                        <tr>
                            <th>Medicine</th>
                            <th>Dosage</th>
                            <th>Frequency</th>
                            <th>Duration</th>
                            <th>Instructions</th>
                            <th>Purpose</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${items.map(item => `
                            <tr>
                                <td>${item.medicine_name || ''}</td>
                                <td>${item.dosage || ''}</td>
                                <td>${item.frequency || ''}</td>
                                <td>${item.duration || ''}</td>
                                <td>${item.instructions || '-'}</td>
                                <td>${item.purpose || '-'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            ` : '<p>No medicines in this prescription.</p>'}
            
            <div style="margin-top: 20px;">
                <button onclick="editPrescription('${prescriptionId}')">Edit Prescription</button>
                <button onclick="showPrescriptions()">Back to List</button>
            </div>
        `;
    } catch (error) {
        alert('Error loading prescription details: ' + error.message);
    }
}

async function editPrescription(prescriptionId) {
    // Similar to showAddPrescriptionForm but with pre-filled data
    // This is a simplified version - you can expand it similar to editPatient
    alert('Edit prescription feature - similar to add form but with pre-filled data. Full implementation can be added.');
}

