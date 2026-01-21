/**
 * Patient Management Module
 * Handles patient list, add, edit operations
 */

async function showPatients() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Patient Management</h2>
        <div style="display: flex; justify-content: space-between; margin: 20px 0;">
            <input type="text" id="patient-search" placeholder="Search patients..." 
                   style="padding: 10px; width: 300px; border: 1px solid #ddd; border-radius: 5px;"
                   onkeyup="searchPatients()">
            <button onclick="showAddPatientForm()" class="btn-success">+ Add Patient</button>
        </div>
        <div id="patients-list">Loading...</div>
    `;
    loadPatients();
}

async function loadPatients() {
    try {
        const result = await PatientAPI.getAll();
        displayPatients(result.patients);
    } catch (error) {
        document.getElementById('patients-list').innerHTML = 
            '<p style="color: red;">Error loading patients: ' + error.message + '</p>';
    }
}

async function searchPatients() {
    const query = document.getElementById('patient-search').value;
    if (query.length < 2) {
        loadPatients();
        return;
    }
    
    try {
        const result = await PatientAPI.search(query);
        displayPatients(result.patients);
    } catch (error) {
        console.error('Search error:', error);
    }
}

function displayPatients(patients) {
    const listDiv = document.getElementById('patients-list');
    
    if (!patients || patients.length === 0) {
        listDiv.innerHTML = '<p>No patients found.</p>';
        return;
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>Patient ID</th>
                    <th>Name</th>
                    <th>Date of Birth</th>
                    <th>Gender</th>
                    <th>Phone</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    patients.forEach(patient => {
        html += `
            <tr>
                <td>${patient.patient_id || ''}</td>
                <td>${patient.first_name || ''} ${patient.last_name || ''}</td>
                <td>${patient.date_of_birth || ''}</td>
                <td>${patient.gender || ''}</td>
                <td>${patient.phone || ''}</td>
                <td>
                    <button onclick="editPatient('${patient.patient_id}')">Edit</button>
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

function showAddPatientForm() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Add New Patient</h2>
        <form id="patient-form" onsubmit="savePatient(event)">
            <div class="form-group">
                <label>Patient ID *</label>
                <input type="text" id="patient_id" required>
            </div>
            <div class="form-group">
                <label>First Name *</label>
                <input type="text" id="first_name" required>
            </div>
            <div class="form-group">
                <label>Last Name *</label>
                <input type="text" id="last_name" required>
            </div>
            <div class="form-group">
                <label>Date of Birth *</label>
                <input type="date" id="date_of_birth" required>
            </div>
            <div class="form-group">
                <label>Gender *</label>
                <select id="gender" required>
                    <option value="">Select...</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                </select>
            </div>
            <div class="form-group">
                <label>Phone</label>
                <input type="text" id="phone">
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" id="email">
            </div>
            <div class="form-group">
                <label>Address</label>
                <input type="text" id="address">
            </div>
            <button type="submit" class="btn-success">Save Patient</button>
            <button type="button" onclick="showPatients()">Cancel</button>
        </form>
    `;
}

async function savePatient(event) {
    event.preventDefault();
    
    const patientData = {
        patient_id: document.getElementById('patient_id').value,
        first_name: document.getElementById('first_name').value,
        last_name: document.getElementById('last_name').value,
        date_of_birth: document.getElementById('date_of_birth').value,
        gender: document.getElementById('gender').value,
        phone: document.getElementById('phone').value,
        email: document.getElementById('email').value,
        address: document.getElementById('address').value
    };

    try {
        await PatientAPI.create(patientData);
        alert('Patient added successfully!');
        showPatients();
    } catch (error) {
        alert('Error adding patient: ' + error.message);
    }
}

async function editPatient(patientId) {
    try {
        const result = await PatientAPI.getById(patientId);
        const patient = result.patient;
        
        // Similar to showAddPatientForm but pre-fill with patient data
        alert('Edit patient: ' + patient.first_name + ' (Edit form not implemented in this example)');
    } catch (error) {
        alert('Error loading patient: ' + error.message);
    }
}

