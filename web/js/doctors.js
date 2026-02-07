/**
 * Doctor Management Module
 */

async function showDoctors() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h2>👨‍⚕️ Doctor Management</h2>
            </div>
            <div class="action-bar">
                <div></div>
                <button onclick="showAddDoctorForm()" class="btn btn-success">+ Add Doctor</button>
            </div>
            <div id="doctors-list">
                <div class="loading">
                    <div class="spinner"></div>
                </div>
            </div>
        </div>
    `;
    loadDoctors();
}

async function loadDoctors() {
    const listDiv = document.getElementById('doctors-list');
    showLoading(listDiv);
    
    try {
        const result = await DoctorAPI.getAll();
        displayDoctors(result.doctors);
    } catch (error) {
        listDiv.innerHTML = 
            `<div class="alert alert-error">❌ Error loading doctors: ${error.message}</div>`;
    }
}

function displayDoctors(doctors) {
    const listDiv = document.getElementById('doctors-list');
    
    if (!doctors || doctors.length === 0) {
        listDiv.innerHTML = '<div class="empty-state">No doctors found. Add your first doctor to get started.</div>';
        return;
    }

    let html = `
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Doctor ID</th>
                        <th>Name</th>
                        <th>Specialization</th>
                        <th>Phone</th>
                        <th>Email</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;

    doctors.forEach(doctor => {
        html += `
            <tr>
                <td><strong>${doctor.doctor_id || ''}</strong></td>
                <td>Dr. ${doctor.first_name || ''} ${doctor.last_name || ''}</td>
                <td><span class="badge badge-primary">${doctor.specialization || '-'}</span></td>
                <td>${doctor.phone || '-'}</td>
                <td>${doctor.email || '-'}</td>
                <td>
                    <button onclick="editDoctor('${doctor.doctor_id}')" class="btn btn-primary" style="padding: 4px 12px; font-size: 12px; margin-right: 4px;">Edit</button>
                    <button onclick="deleteDoctor('${doctor.doctor_id}')" class="btn btn-danger" style="padding: 4px 12px; font-size: 12px;">Delete</button>
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

function showAddDoctorForm() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h2>➕ Add New Doctor</h2>
            </div>
            <form id="doctor-form" onsubmit="saveDoctor(event)">
                <div class="grid grid-2">
                    <div class="form-group">
                        <label>Doctor ID *</label>
                        <input type="text" id="doctor_id" required placeholder="e.g., DOC001">
                        <small>Leave empty to auto-generate</small>
                    </div>
                    <div class="form-group">
                        <label>Specialization *</label>
                        <input type="text" id="specialization" required placeholder="e.g., Cardiology">
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
                        <label>Phone</label>
                        <input type="tel" id="phone" placeholder="Enter phone number">
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="email" placeholder="Enter email address">
                    </div>
                </div>
                <div style="margin-top: var(--spacing-lg); display: flex; gap: var(--spacing-md);">
                    <button type="submit" class="btn btn-success">💾 Save Doctor</button>
                    <button type="button" onclick="showDoctors()" class="btn btn-secondary">Cancel</button>
                </div>
            </form>
        </div>
    `;
}

async function saveDoctor(event) {
    event.preventDefault();
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<div class="spinner" style="width: 16px; height: 16px; border-width: 2px;"></div> Saving...';
    
    const doctorData = {
        doctor_id: document.getElementById('doctor_id').value.trim() || undefined,
        first_name: document.getElementById('first_name').value.trim(),
        last_name: document.getElementById('last_name').value.trim(),
        specialization: document.getElementById('specialization').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        email: document.getElementById('email').value.trim()
    };

    try {
        await DoctorAPI.create(doctorData);
        if (typeof showNotification === 'function') {
            showNotification('✅ Doctor added successfully!', 'success');
        } else {
            alert('Doctor added successfully!');
        }
        showDoctors();
    } catch (error) {
        if (typeof showNotification === 'function') {
            showNotification('❌ Error adding doctor: ' + error.message, 'error');
        } else {
            alert('Error adding doctor: ' + error.message);
        }
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

async function deleteDoctor(doctorId) {
    if (!confirm('Are you sure you want to delete this doctor? This action cannot be undone.')) return;
    
    try {
        await DoctorAPI.delete(doctorId);
        if (typeof showNotification === 'function') {
            showNotification('✅ Doctor deleted successfully!', 'success');
        } else {
            alert('Doctor deleted successfully!');
        }
        loadDoctors();
    } catch (error) {
        if (typeof showNotification === 'function') {
            showNotification('❌ Error deleting doctor: ' + error.message, 'error');
        } else {
            alert('Error deleting doctor: ' + error.message);
        }
    }
}

