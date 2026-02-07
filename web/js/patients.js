/**
 * Patient Management Module
 * Handles patient list, add, edit operations
 */

async function showPatients() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h2>👥 Patient Management</h2>
            </div>
            <div class="action-bar">
                <input type="text" id="patient-search" class="search-input" 
                       placeholder="🔍 Search patients by name, ID, or phone..." 
                       onkeyup="searchPatients()">
                <button onclick="showAddPatientForm()" class="btn btn-success">+ Add Patient</button>
            </div>
            <div id="patients-list">
                <div class="loading">
                    <div class="spinner"></div>
                </div>
            </div>
        </div>
    `;
    loadPatients();
}

async function loadPatients() {
    const listDiv = document.getElementById('patients-list');
    showLoading(listDiv);
    
    try {
        const result = await PatientAPI.getAll();
        displayPatients(result.patients);
    } catch (error) {
        listDiv.innerHTML = 
            `<div class="alert alert-error">❌ Error loading patients: ${error.message}</div>`;
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
        listDiv.innerHTML = '<div class="empty-state">No patients found. Add your first patient to get started.</div>';
        return;
    }

    let html = `
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Patient ID</th>
                        <th>Name</th>
                        <th>Date of Birth</th>
                        <th>Gender</th>
                        <th>Phone</th>
                        <th>Email</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;

    patients.forEach(patient => {
        html += `
            <tr>
                <td><strong>${patient.patient_id || ''}</strong></td>
                <td>${patient.first_name || ''} ${patient.last_name || ''}</td>
                <td>${patient.date_of_birth || '-'}</td>
                <td><span class="badge badge-primary">${patient.gender || '-'}</span></td>
                <td>${patient.phone || '-'}</td>
                <td>${patient.email || '-'}</td>
                <td>
                    <button onclick="editPatient('${patient.patient_id}')" class="btn btn-primary" style="padding: 4px 12px; font-size: 12px;">Edit</button>
                </td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    listDiv.innerHTML = html;
}

function showAddPatientForm() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h2>➕ Add New Patient</h2>
            </div>
            <form id="patient-form" onsubmit="savePatient(event)">
                <div class="grid grid-2">
                    <div class="form-group">
                        <label>Patient ID *</label>
                        <input type="text" id="patient_id" required placeholder="e.g., PAT001">
                        <small>Leave empty to auto-generate</small>
                    </div>
                    <div class="form-group">
                        <label>Date of Birth *</label>
                        <input type="date" id="date_of_birth" required>
                    </div>
                    <div class="form-group">
                        <label>First Name *</label>
                        <input type="text" id="first_name" required placeholder="Enter first name">
                    </div>
                    <div class="form-group">
                        <label>Last Name *</label>
                        <input type="text" id="last_name" required placeholder="Enter last name">
                    </div>
                    <div class="form-group">
                        <label>Gender *</label>
                        <select id="gender" required>
                            <option value="">Select Gender...</option>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="tel" id="phone" placeholder="Enter phone number">
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="email" placeholder="Enter email address">
                    </div>
                    <div class="form-group">
                        <label>Address</label>
                        <input type="text" id="address" placeholder="Enter address">
                    </div>
                </div>
                <div style="margin-top: var(--spacing-lg); display: flex; gap: var(--spacing-md);">
                    <button type="submit" class="btn btn-success">💾 Save Patient</button>
                    <button type="button" onclick="showPatients()" class="btn btn-secondary">Cancel</button>
                </div>
            </form>
        </div>
    `;
}

async function savePatient(event) {
    event.preventDefault();
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<div class="spinner" style="width: 16px; height: 16px; border-width: 2px;"></div> Saving...';
    
    const patientData = {
        patient_id: document.getElementById('patient_id').value.trim() || undefined,
        first_name: document.getElementById('first_name').value.trim(),
        last_name: document.getElementById('last_name').value.trim(),
        date_of_birth: document.getElementById('date_of_birth').value,
        gender: document.getElementById('gender').value,
        phone: document.getElementById('phone').value.trim(),
        email: document.getElementById('email').value.trim(),
        address: document.getElementById('address').value.trim()
    };

    try {
        await PatientAPI.create(patientData);
        if (typeof showNotification === 'function') {
            showNotification('✅ Patient added successfully!', 'success');
        } else {
            alert('Patient added successfully!');
        }
        showPatients();
    } catch (error) {
        if (typeof showNotification === 'function') {
            showNotification('❌ Error adding patient: ' + error.message, 'error');
        } else {
            alert('Error adding patient: ' + error.message);
        }
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

async function editPatient(patientId) {
    try {
        const result = await PatientAPI.getById(patientId);
        const patient = result.patient;
        
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h2>✏️ Edit Patient</h2>
                </div>
                <form id="patient-form" onsubmit="updatePatient(event, '${patientId}')">
                    <div class="grid grid-2">
                        <div class="form-group">
                            <label>Patient ID</label>
                            <input type="text" id="patient_id" value="${patient.patient_id || ''}" readonly style="background: var(--gray-100);">
                        </div>
                        <div class="form-group">
                            <label>Date of Birth *</label>
                            <input type="date" id="date_of_birth" value="${patient.date_of_birth || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>First Name *</label>
                            <input type="text" id="first_name" value="${patient.first_name || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>Last Name *</label>
                            <input type="text" id="last_name" value="${patient.last_name || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>Gender *</label>
                            <select id="gender" required>
                                <option value="">Select Gender...</option>
                                <option value="Male" ${patient.gender === 'Male' ? 'selected' : ''}>Male</option>
                                <option value="Female" ${patient.gender === 'Female' ? 'selected' : ''}>Female</option>
                                <option value="Other" ${patient.gender === 'Other' ? 'selected' : ''}>Other</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Phone</label>
                            <input type="tel" id="phone" value="${patient.phone || ''}">
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" id="email" value="${patient.email || ''}">
                        </div>
                        <div class="form-group">
                            <label>Address</label>
                            <input type="text" id="address" value="${patient.address || ''}">
                        </div>
                    </div>
                    <div style="margin-top: var(--spacing-lg); display: flex; gap: var(--spacing-md);">
                        <button type="submit" class="btn btn-success">💾 Update Patient</button>
                        <button type="button" onclick="showPatients()" class="btn btn-secondary">Cancel</button>
                    </div>
                </form>
            </div>
        `;
    } catch (error) {
        if (typeof showNotification === 'function') {
            showNotification('❌ Error loading patient: ' + error.message, 'error');
        } else {
            alert('Error loading patient: ' + error.message);
        }
    }
}

async function updatePatient(event, patientId) {
    event.preventDefault();
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<div class="spinner" style="width: 16px; height: 16px; border-width: 2px;"></div> Updating...';
    
    const patientData = {
        first_name: document.getElementById('first_name').value.trim(),
        last_name: document.getElementById('last_name').value.trim(),
        date_of_birth: document.getElementById('date_of_birth').value,
        gender: document.getElementById('gender').value,
        phone: document.getElementById('phone').value.trim(),
        email: document.getElementById('email').value.trim(),
        address: document.getElementById('address').value.trim()
    };

    try {
        await PatientAPI.update(patientId, patientData);
        if (typeof showNotification === 'function') {
            showNotification('✅ Patient updated successfully!', 'success');
        } else {
            alert('Patient updated successfully!');
        }
        showPatients();
    } catch (error) {
        if (typeof showNotification === 'function') {
            showNotification('❌ Error updating patient: ' + error.message, 'error');
        } else {
            alert('Error updating patient: ' + error.message);
        }
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

