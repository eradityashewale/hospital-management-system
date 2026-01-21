/**
 * Doctor Management Module
 */

async function showDoctors() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Doctor Management</h2>
        <div style="margin: 20px 0;">
            <button onclick="showAddDoctorForm()" class="btn-success">+ Add Doctor</button>
        </div>
        <div id="doctors-list">Loading...</div>
    `;
    loadDoctors();
}

async function loadDoctors() {
    try {
        const result = await DoctorAPI.getAll();
        displayDoctors(result.doctors);
    } catch (error) {
        document.getElementById('doctors-list').innerHTML = 
            '<p style="color: red;">Error loading doctors: ' + error.message + '</p>';
    }
}

function displayDoctors(doctors) {
    const listDiv = document.getElementById('doctors-list');
    
    if (!doctors || doctors.length === 0) {
        listDiv.innerHTML = '<p>No doctors found.</p>';
        return;
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>Doctor ID</th>
                    <th>Name</th>
                    <th>Specialization</th>
                    <th>Phone</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    doctors.forEach(doctor => {
        html += `
            <tr>
                <td>${doctor.doctor_id || ''}</td>
                <td>${doctor.first_name || ''} ${doctor.last_name || ''}</td>
                <td>${doctor.specialization || ''}</td>
                <td>${doctor.phone || ''}</td>
                <td>
                    <button onclick="editDoctor('${doctor.doctor_id}')">Edit</button>
                    <button onclick="deleteDoctor('${doctor.doctor_id}')" class="btn-danger">Delete</button>
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

function showAddDoctorForm() {
    alert('Add doctor form (similar to patient form - not fully implemented in this example)');
}

async function deleteDoctor(doctorId) {
    if (!confirm('Are you sure you want to delete this doctor?')) return;
    
    try {
        await DoctorAPI.delete(doctorId);
        alert('Doctor deleted successfully!');
        loadDoctors();
    } catch (error) {
        alert('Error deleting doctor: ' + error.message);
    }
}

