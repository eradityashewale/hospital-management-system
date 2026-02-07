/**
 * Appointment Management Module
 * Handles appointment list, add, edit, and filter operations
 */

async function showAppointments() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h2>📅 Appointment Management</h2>
            </div>
            <div class="search-bar">
                <input type="text" id="appointment-search" class="search-input" 
                       placeholder="🔍 Search by patient name..." 
                       onkeyup="searchAppointments()">
                <input type="date" id="appointment-date-filter" class="search-input" 
                       style="width: auto; min-width: 180px;"
                       onchange="filterAppointmentsByDate()">
                <select id="appointment-status-filter" class="search-input" 
                        style="width: auto; min-width: 150px;"
                        onchange="filterAppointmentsByStatus()">
                    <option value="">All Status</option>
                    <option value="Scheduled">Scheduled</option>
                    <option value="Completed">Completed</option>
                    <option value="Cancelled">Cancelled</option>
                </select>
                <button onclick="loadAppointments()" class="btn btn-secondary">Reset Filters</button>
                <button onclick="showAddAppointmentForm()" class="btn btn-success">+ New Appointment</button>
            </div>
            <div id="appointments-list">
                <div class="loading">
                    <div class="spinner"></div>
                </div>
            </div>
        </div>
    `;
    await loadAppointments();
}

async function loadAppointments() {
    const listDiv = document.getElementById('appointments-list');
    showLoading(listDiv);
    
    try {
        const result = await AppointmentAPI.getAll();
        displayAppointments(result.appointments);
    } catch (error) {
        listDiv.innerHTML = 
            `<div class="alert alert-error">❌ Error loading appointments: ${error.message}</div>`;
    }
}

async function searchAppointments() {
    const query = document.getElementById('appointment-search').value;
    const date = document.getElementById('appointment-date-filter').value;
    const status = document.getElementById('appointment-status-filter').value;
    
    try {
        let url = '/appointments?';
        const params = [];
        
        if (query) params.push(`patient_name=${encodeURIComponent(query)}`);
        if (date) params.push(`date=${date}`);
        if (status) params.push(`status=${status}`);
        
        if (params.length > 0) {
            url += params.join('&');
        } else {
            url = '/appointments';
        }
        
        const result = await apiCall(url);
        displayAppointments(result.appointments);
    } catch (error) {
        console.error('Search error:', error);
        document.getElementById('appointments-list').innerHTML = 
            '<p style="color: red;">Error searching appointments: ' + error.message + '</p>';
    }
}

async function filterAppointmentsByDate() {
    searchAppointments();
}

async function filterAppointmentsByStatus() {
    searchAppointments();
}

function displayAppointments(appointments) {
    const listDiv = document.getElementById('appointments-list');
    
    if (!appointments || appointments.length === 0) {
        listDiv.innerHTML = '<div class="empty-state">No appointments found. Schedule your first appointment to get started.</div>';
        return;
    }

    let html = `
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Appointment ID</th>
                        <th>Patient Name</th>
                        <th>Doctor Name</th>
                        <th>Date</th>
                        <th>Time</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;

    appointments.forEach(appointment => {
        const statusClass = appointment.status === 'Completed' ? 'badge-success' : 
                           appointment.status === 'Cancelled' ? 'badge-cancelled' : 'badge-pending';
        
        html += `
            <tr>
                <td><strong>${appointment.appointment_id || ''}</strong></td>
                <td>${appointment.patient_name || 'N/A'}</td>
                <td>${appointment.doctor_name || 'N/A'}</td>
                <td>${appointment.appointment_date || ''}</td>
                <td>${appointment.appointment_time || ''}</td>
                <td>
                    <span class="badge ${statusClass}">
                        ${appointment.status || 'Scheduled'}
                    </span>
                </td>
                <td>
                    <button onclick="editAppointment('${appointment.appointment_id}')" class="btn btn-primary" style="padding: 4px 12px; font-size: 12px; margin-right: 4px;">Edit</button>
                    <button onclick="viewAppointmentDetails('${appointment.appointment_id}')" class="btn btn-secondary" style="padding: 4px 12px; font-size: 12px;">View</button>
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

async function showAddAppointmentForm() {
    // First load patients and doctors for dropdowns
    let patients = [];
    let doctors = [];
    
    try {
        const patientsResult = await PatientAPI.getAll();
        patients = patientsResult.patients || [];
        
        const doctorsResult = await DoctorAPI.getAll();
        doctors = doctorsResult.doctors || [];
    } catch (error) {
        alert('Error loading patients/doctors: ' + error.message);
        return;
    }

    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Schedule New Appointment</h2>
        <form id="appointment-form" onsubmit="saveAppointment(event)">
            <div class="form-group">
                <label>Appointment ID *</label>
                <input type="text" id="appointment_id" required placeholder="Auto-generated if empty">
                <small style="color: #666;">Leave empty to auto-generate</small>
            </div>
            
            <div class="form-group">
                <label>Patient *</label>
                <select id="patient_id" required>
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
                <label>Appointment Date *</label>
                <input type="date" id="appointment_date" required>
            </div>
            
            <div class="form-group">
                <label>Appointment Time *</label>
                <input type="time" id="appointment_time" required>
            </div>
            
            <div class="form-group">
                <label>Status</label>
                <select id="status">
                    <option value="Scheduled" selected>Scheduled</option>
                    <option value="Completed">Completed</option>
                    <option value="Cancelled">Cancelled</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Notes</label>
                <textarea id="notes" rows="3" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;"></textarea>
            </div>
            
            <button type="submit" class="btn-success">Schedule Appointment</button>
            <button type="button" onclick="showAppointments()">Cancel</button>
        </form>
    `;
    
    // Set today's date as default
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('appointment_date').value = today;
}

async function saveAppointment(event) {
    event.preventDefault();
    
    let appointmentId = document.getElementById('appointment_id').value.trim();
    if (!appointmentId) {
        // Generate appointment ID if not provided
        appointmentId = 'APT' + Date.now().toString().slice(-8);
    }
    
    const appointmentData = {
        appointment_id: appointmentId,
        patient_id: document.getElementById('patient_id').value,
        doctor_id: document.getElementById('doctor_id').value,
        appointment_date: document.getElementById('appointment_date').value,
        appointment_time: document.getElementById('appointment_time').value,
        status: document.getElementById('status').value,
        notes: document.getElementById('notes').value || ''
    };

    try {
        await AppointmentAPI.create(appointmentData);
        if (typeof showNotification === 'function') {
            showNotification('✅ Appointment scheduled successfully!', 'success');
        } else {
            alert('Appointment scheduled successfully!');
        }
        showAppointments();
    } catch (error) {
        if (typeof showNotification === 'function') {
            showNotification('❌ Error scheduling appointment: ' + error.message, 'error');
        } else {
            alert('Error scheduling appointment: ' + error.message);
        }
    }
}

async function editAppointment(appointmentId) {
    try {
        const result = await AppointmentAPI.getById(appointmentId);
        const appointment = result.appointment;
        
        // Load patients and doctors
        const patientsResult = await PatientAPI.getAll();
        const patients = patientsResult.patients || [];
        
        const doctorsResult = await DoctorAPI.getAll();
        const doctors = doctorsResult.doctors || [];
        
        const content = document.getElementById('content');
        content.innerHTML = `
            <h2>Edit Appointment</h2>
            <form id="appointment-form" onsubmit="updateAppointment(event, '${appointmentId}')">
                <div class="form-group">
                    <label>Appointment ID</label>
                    <input type="text" id="appointment_id" value="${appointment.appointment_id || ''}" readonly style="background: #f5f5f5;">
                </div>
                
                <div class="form-group">
                    <label>Patient *</label>
                    <select id="patient_id" required>
                        ${patients.map(p => 
                            `<option value="${p.patient_id}" ${p.patient_id === appointment.patient_id ? 'selected' : ''}>
                                ${p.patient_id} - ${p.first_name} ${p.last_name}
                            </option>`
                        ).join('')}
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Doctor *</label>
                    <select id="doctor_id" required>
                        ${doctors.map(d => 
                            `<option value="${d.doctor_id}" ${d.doctor_id === appointment.doctor_id ? 'selected' : ''}>
                                ${d.doctor_id} - ${d.first_name} ${d.last_name} (${d.specialization})
                            </option>`
                        ).join('')}
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Appointment Date *</label>
                    <input type="date" id="appointment_date" value="${appointment.appointment_date || ''}" required>
                </div>
                
                <div class="form-group">
                    <label>Appointment Time *</label>
                    <input type="time" id="appointment_time" value="${appointment.appointment_time || ''}" required>
                </div>
                
                <div class="form-group">
                    <label>Status</label>
                    <select id="status">
                        <option value="Scheduled" ${appointment.status === 'Scheduled' ? 'selected' : ''}>Scheduled</option>
                        <option value="Completed" ${appointment.status === 'Completed' ? 'selected' : ''}>Completed</option>
                        <option value="Cancelled" ${appointment.status === 'Cancelled' ? 'selected' : ''}>Cancelled</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Notes</label>
                    <textarea id="notes" rows="3" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">${appointment.notes || ''}</textarea>
                </div>
                
                <button type="submit" class="btn-success">Update Appointment</button>
                <button type="button" onclick="showAppointments()">Cancel</button>
            </form>
        `;
    } catch (error) {
        alert('Error loading appointment: ' + error.message);
    }
}

async function updateAppointment(event, appointmentId) {
    event.preventDefault();
    
    const appointmentData = {
        patient_id: document.getElementById('patient_id').value,
        doctor_id: document.getElementById('doctor_id').value,
        appointment_date: document.getElementById('appointment_date').value,
        appointment_time: document.getElementById('appointment_time').value,
        status: document.getElementById('status').value,
        notes: document.getElementById('notes').value || ''
    };

    try {
        await AppointmentAPI.update(appointmentId, appointmentData);
        if (typeof showNotification === 'function') {
            showNotification('✅ Appointment updated successfully!', 'success');
        } else {
            alert('Appointment updated successfully!');
        }
        showAppointments();
    } catch (error) {
        if (typeof showNotification === 'function') {
            showNotification('❌ Error updating appointment: ' + error.message, 'error');
        } else {
            alert('Error updating appointment: ' + error.message);
        }
    }
}

async function viewAppointmentDetails(appointmentId) {
    try {
        const result = await AppointmentAPI.getById(appointmentId);
        const appointment = result.appointment;
        
        const statusClass = appointment.status === 'Completed' ? 'badge-success' : 
                           appointment.status === 'Cancelled' ? 'badge-cancelled' : 'badge-pending';
        
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h2>📋 Appointment Details</h2>
                </div>
                <div class="grid grid-2" style="margin-bottom: var(--spacing-lg);">
                    <div class="card">
                        <h3 style="margin-bottom: var(--spacing-md);">Appointment Information</h3>
                        <p style="margin-bottom: var(--spacing-sm);"><strong>Appointment ID:</strong> ${appointment.appointment_id || 'N/A'}</p>
                        <p style="margin-bottom: var(--spacing-sm);"><strong>Patient:</strong> ${appointment.patient_name || 'N/A'}</p>
                        <p style="margin-bottom: var(--spacing-sm);"><strong>Doctor:</strong> ${appointment.doctor_name || 'N/A'}</p>
                        <p style="margin-bottom: var(--spacing-sm);"><strong>Date:</strong> ${appointment.appointment_date || 'N/A'}</p>
                        <p style="margin-bottom: var(--spacing-sm);"><strong>Time:</strong> ${appointment.appointment_time || 'N/A'}</p>
                        <p style="margin-bottom: var(--spacing-sm);"><strong>Status:</strong> <span class="badge ${statusClass}">${appointment.status || 'N/A'}</span></p>
                        <p><strong>Notes:</strong> ${appointment.notes || 'No notes'}</p>
                    </div>
                </div>
                <div style="display: flex; gap: var(--spacing-md);">
                    <button onclick="editAppointment('${appointmentId}')" class="btn btn-primary">✏️ Edit Appointment</button>
                    <button onclick="showAppointments()" class="btn btn-secondary">← Back to List</button>
                </div>
            </div>
        `;
    } catch (error) {
        alert('Error loading appointment details: ' + error.message);
    }
}



