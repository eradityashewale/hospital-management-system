/**
 * Billing Management Module
 * Handles bill list, add, edit, delete, and filter operations
 */

async function showBilling() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h2>💰 Billing Management</h2>
            </div>
            <div class="search-bar">
                <input type="text" id="bill-search" class="search-input" 
                       placeholder="🔍 Search by patient name..." 
                       onkeyup="searchBills()">
                <input type="date" id="bill-date-filter" class="search-input" 
                       style="width: auto; min-width: 180px;"
                       onchange="filterBillsByDate()">
                <select id="bill-status-filter" class="search-input" 
                        style="width: auto; min-width: 150px;"
                        onchange="filterBillsByStatus()">
                    <option value="">All Status</option>
                    <option value="Pending">Pending</option>
                    <option value="Paid">Paid</option>
                    <option value="Cancelled">Cancelled</option>
                </select>
                <button onclick="loadBills()" class="btn btn-secondary">Reset Filters</button>
                <button onclick="showAddBillForm()" class="btn btn-success">+ New Bill</button>
            </div>
            <div id="bills-list">
                <div class="loading">
                    <div class="spinner"></div>
                </div>
            </div>
        </div>
    `;
    await loadBills();
}

async function loadBills() {
    const listDiv = document.getElementById('bills-list');
    showLoading(listDiv);
    
    try {
        const result = await BillAPI.getAll();
        displayBills(result.bills);
    } catch (error) {
        listDiv.innerHTML = 
            `<div class="alert alert-error">❌ Error loading bills: ${error.message}</div>`;
    }
}

async function searchBills() {
    const query = document.getElementById('bill-search').value;
    const date = document.getElementById('bill-date-filter').value;
    const status = document.getElementById('bill-status-filter').value;
    
    try {
        let url = '/bills?';
        const params = [];
        
        if (query) params.push(`patient_name=${encodeURIComponent(query)}`);
        if (date) params.push(`date=${date}`);
        if (status) params.push(`status=${status}`);
        
        if (params.length > 0) {
            url += params.join('&');
        } else {
            url = '/bills';
        }
        
        const result = await apiCall(url);
        displayBills(result.bills);
    } catch (error) {
        console.error('Search error:', error);
        document.getElementById('bills-list').innerHTML = 
            '<p style="color: red;">Error searching bills: ' + error.message + '</p>';
    }
}

async function filterBillsByDate() {
    searchBills();
}

async function filterBillsByStatus() {
    searchBills();
}

function displayBills(bills) {
    const listDiv = document.getElementById('bills-list');
    
    if (!bills || bills.length === 0) {
        listDiv.innerHTML = '<div class="empty-state">No bills found. Create your first bill to get started.</div>';
        return;
    }

    // Calculate totals
    const totalAmount = bills.reduce((sum, bill) => sum + (parseFloat(bill.total_amount) || 0), 0);
    const paidAmount = bills
        .filter(b => b.payment_status === 'Paid')
        .reduce((sum, bill) => sum + (parseFloat(bill.total_amount) || 0), 0);
    const pendingAmount = bills
        .filter(b => b.payment_status === 'Pending')
        .reduce((sum, bill) => sum + (parseFloat(bill.total_amount) || 0), 0);

    let html = `
        <div class="stats-grid" style="margin-bottom: var(--spacing-lg);">
            <div class="stat-card">
                <h3>Total Amount</h3>
                <div class="value">₹${totalAmount.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
            </div>
            <div class="stat-card">
                <h3>Paid</h3>
                <div class="value">₹${paidAmount.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
            </div>
            <div class="stat-card">
                <h3>Pending</h3>
                <div class="value">₹${pendingAmount.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
            </div>
        </div>
        <div class="table-container">
            <table>
            <thead>
                <tr>
                    <th>Bill ID</th>
                    <th>Patient Name</th>
                    <th>Bill Date</th>
                    <th>Consultation Fee</th>
                    <th>Medicine Cost</th>
                    <th>Other Charges</th>
                    <th>Total Amount</th>
                    <th>Payment Status</th>
                    <th>Payment Method</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    bills.forEach(bill => {
        const statusClass = bill.payment_status === 'Paid' ? 'badge-success' : 
                           bill.payment_status === 'Cancelled' ? 'badge-cancelled' : 'badge-pending';
        
        html += `
            <tr>
                <td><strong>${bill.bill_id || ''}</strong></td>
                <td>${bill.patient_name || 'N/A'}</td>
                <td>${bill.bill_date || ''}</td>
                <td>₹${parseFloat(bill.consultation_fee || 0).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                <td>₹${parseFloat(bill.medicine_cost || 0).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                <td>₹${parseFloat(bill.other_charges || 0).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                <td><strong>₹${parseFloat(bill.total_amount || 0).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</strong></td>
                <td>
                    <span class="badge ${statusClass}">
                        ${bill.payment_status || 'Pending'}
                    </span>
                </td>
                <td>${bill.payment_method || '-'}</td>
                <td>
                    <button onclick="viewBillDetails('${bill.bill_id}')" class="btn btn-primary" style="padding: 4px 12px; font-size: 12px; margin-right: 4px;">View</button>
                    <button onclick="editBill('${bill.bill_id}')" class="btn btn-secondary" style="padding: 4px 12px; font-size: 12px; margin-right: 4px;">Edit</button>
                    <button onclick="deleteBill('${bill.bill_id}')" class="btn btn-danger" style="padding: 4px 12px; font-size: 12px;">Delete</button>
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

async function showAddBillForm() {
    // Load patients and appointments
    let patients = [];
    let appointments = [];
    
    try {
        const patientsResult = await PatientAPI.getAll();
        patients = patientsResult.patients || [];
        
        const appointmentsResult = await AppointmentAPI.getAll();
        appointments = appointmentsResult.appointments || [];
    } catch (error) {
        alert('Error loading data: ' + error.message);
        return;
    }

    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Create New Bill</h2>
        <form id="bill-form" onsubmit="saveBill(event)">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <div class="form-group">
                        <label>Bill ID *</label>
                        <input type="text" id="bill_id" placeholder="Auto-generated if empty">
                        <small style="color: #666;">Leave empty to auto-generate</small>
                    </div>
                    
                    <div class="form-group">
                        <label>Patient *</label>
                        <select id="patient_id" required onchange="loadPatientAppointmentsForBill()">
                            <option value="">Select Patient...</option>
                            ${patients.map(p => `<option value="${p.patient_id}">${p.patient_id} - ${p.first_name} ${p.last_name}</option>`).join('')}
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Appointment (Optional)</label>
                        <select id="appointment_id">
                            <option value="">No Appointment</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Bill Date *</label>
                        <input type="date" id="bill_date" required>
                    </div>
                </div>
                
                <div>
                    <h3>Charges</h3>
                    
                    <div class="form-group">
                        <label>Consultation Fee (₹)</label>
                        <input type="number" id="consultation_fee" step="0.01" min="0" value="0" 
                               onchange="calculateTotal()">
                    </div>
                    
                    <div class="form-group">
                        <label>Medicine Cost (₹)</label>
                        <input type="number" id="medicine_cost" step="0.01" min="0" value="0" 
                               onchange="calculateTotal()">
                    </div>
                    
                    <div class="form-group">
                        <label>Other Charges (₹)</label>
                        <input type="number" id="other_charges" step="0.01" min="0" value="0" 
                               onchange="calculateTotal()">
                    </div>
                    
                    <div class="form-group">
                        <label>Total Amount (₹) *</label>
                        <input type="number" id="total_amount" step="0.01" min="0" required readonly 
                               style="background: #f5f5f5; font-weight: bold; font-size: 16px;">
                    </div>
                    
                    <div class="form-group">
                        <label>Payment Status *</label>
                        <select id="payment_status" required>
                            <option value="Pending" selected>Pending</option>
                            <option value="Paid">Paid</option>
                            <option value="Cancelled">Cancelled</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Payment Method</label>
                        <select id="payment_method">
                            <option value="">Select Method...</option>
                            <option value="Cash">Cash</option>
                            <option value="Card">Card</option>
                            <option value="UPI">UPI</option>
                            <option value="Net Banking">Net Banking</option>
                            <option value="Cheque">Cheque</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label>Notes</label>
                <textarea id="notes" rows="3" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;"></textarea>
            </div>
            
            <button type="submit" class="btn-success">Create Bill</button>
            <button type="button" onclick="showBilling()">Cancel</button>
        </form>
    `;
    
    // Set today's date as default
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('bill_date').value = today;
    
    // Calculate initial total
    calculateTotal();
}

function calculateTotal() {
    const consultationFee = parseFloat(document.getElementById('consultation_fee').value) || 0;
    const medicineCost = parseFloat(document.getElementById('medicine_cost').value) || 0;
    const otherCharges = parseFloat(document.getElementById('other_charges').value) || 0;
    const total = consultationFee + medicineCost + otherCharges;
    document.getElementById('total_amount').value = total.toFixed(2);
}

async function loadPatientAppointmentsForBill() {
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

async function saveBill(event) {
    event.preventDefault();
    
    let billId = document.getElementById('bill_id').value.trim();
    if (!billId) {
        billId = 'BILL' + Date.now().toString().slice(-8);
    }
    
    const billData = {
        bill_id: billId,
        patient_id: document.getElementById('patient_id').value,
        appointment_id: document.getElementById('appointment_id').value || null,
        bill_date: document.getElementById('bill_date').value,
        consultation_fee: parseFloat(document.getElementById('consultation_fee').value) || 0,
        medicine_cost: parseFloat(document.getElementById('medicine_cost').value) || 0,
        other_charges: parseFloat(document.getElementById('other_charges').value) || 0,
        total_amount: parseFloat(document.getElementById('total_amount').value) || 0,
        payment_status: document.getElementById('payment_status').value,
        payment_method: document.getElementById('payment_method').value || '',
        notes: document.getElementById('notes').value || ''
    };

    try {
        await BillAPI.create(billData);
        if (typeof showNotification === 'function') {
            showNotification('✅ Bill created successfully!', 'success');
        } else {
            alert('Bill created successfully!');
        }
        showBilling();
    } catch (error) {
        if (typeof showNotification === 'function') {
            showNotification('❌ Error creating bill: ' + error.message, 'error');
        } else {
            alert('Error creating bill: ' + error.message);
        }
    }
}

async function viewBillDetails(billId) {
    try {
        const result = await BillAPI.getById(billId);
        const bill = result.bill;
        
        const content = document.getElementById('content');
        content.innerHTML = `
            <h2>Bill Details</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                <div style="background: #f9f9f9; padding: 20px; border-radius: 5px;">
                    <h3>Bill Information</h3>
                    <p><strong>Bill ID:</strong> ${bill.bill_id || 'N/A'}</p>
                    <p><strong>Patient:</strong> ${bill.patient_name || 'N/A'}</p>
                    <p><strong>Bill Date:</strong> ${bill.bill_date || 'N/A'}</p>
                    <p><strong>Payment Status:</strong> ${bill.payment_status || 'N/A'}</p>
                    <p><strong>Payment Method:</strong> ${bill.payment_method || 'N/A'}</p>
                    <p><strong>Notes:</strong> ${bill.notes || 'N/A'}</p>
                </div>
                
                <div style="background: #f9f9f9; padding: 20px; border-radius: 5px;">
                    <h3>Charges Breakdown</h3>
                    <p><strong>Consultation Fee:</strong> ₹${parseFloat(bill.consultation_fee || 0).toFixed(2)}</p>
                    <p><strong>Medicine Cost:</strong> ₹${parseFloat(bill.medicine_cost || 0).toFixed(2)}</p>
                    <p><strong>Other Charges:</strong> ₹${parseFloat(bill.other_charges || 0).toFixed(2)}</p>
                    <hr style="margin: 15px 0;">
                    <p style="font-size: 20px; font-weight: bold;">
                        <strong>Total Amount:</strong> ₹${parseFloat(bill.total_amount || 0).toFixed(2)}
                    </p>
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <button onclick="editBill('${billId}')">Edit Bill</button>
                <button onclick="showBilling()">Back to List</button>
            </div>
        `;
    } catch (error) {
        alert('Error loading bill details: ' + error.message);
    }
}

async function editBill(billId) {
    try {
        const result = await BillAPI.getById(billId);
        const bill = result.bill;
        
        // Load patients and appointments
        const patientsResult = await PatientAPI.getAll();
        const patients = patientsResult.patients || [];
        
        const appointmentsResult = await AppointmentAPI.getAll();
        const appointments = appointmentsResult.appointments || [];
        const patientAppointments = appointments.filter(a => a.patient_id === bill.patient_id);
        
        const content = document.getElementById('content');
        content.innerHTML = `
            <h2>Edit Bill</h2>
            <form id="bill-form" onsubmit="updateBill(event, '${billId}')">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <div class="form-group">
                            <label>Bill ID</label>
                            <input type="text" id="bill_id" value="${bill.bill_id || ''}" readonly 
                                   style="background: #f5f5f5;">
                        </div>
                        
                        <div class="form-group">
                            <label>Patient *</label>
                            <select id="patient_id" required onchange="loadPatientAppointmentsForBill()">
                                ${patients.map(p => 
                                    `<option value="${p.patient_id}" ${p.patient_id === bill.patient_id ? 'selected' : ''}>
                                        ${p.patient_id} - ${p.first_name} ${p.last_name}
                                    </option>`
                                ).join('')}
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Appointment (Optional)</label>
                            <select id="appointment_id">
                                <option value="">No Appointment</option>
                                ${patientAppointments.map(a => 
                                    `<option value="${a.appointment_id}" ${a.appointment_id === bill.appointment_id ? 'selected' : ''}>
                                        ${a.appointment_id} - ${a.appointment_date} ${a.appointment_time}
                                    </option>`
                                ).join('')}
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Bill Date *</label>
                            <input type="date" id="bill_date" value="${bill.bill_date || ''}" required>
                        </div>
                    </div>
                    
                    <div>
                        <h3>Charges</h3>
                        
                        <div class="form-group">
                            <label>Consultation Fee (₹)</label>
                            <input type="number" id="consultation_fee" step="0.01" min="0" 
                                   value="${bill.consultation_fee || 0}" onchange="calculateTotal()">
                        </div>
                        
                        <div class="form-group">
                            <label>Medicine Cost (₹)</label>
                            <input type="number" id="medicine_cost" step="0.01" min="0" 
                                   value="${bill.medicine_cost || 0}" onchange="calculateTotal()">
                        </div>
                        
                        <div class="form-group">
                            <label>Other Charges (₹)</label>
                            <input type="number" id="other_charges" step="0.01" min="0" 
                                   value="${bill.other_charges || 0}" onchange="calculateTotal()">
                        </div>
                        
                        <div class="form-group">
                            <label>Total Amount (₹) *</label>
                            <input type="number" id="total_amount" step="0.01" min="0" 
                                   value="${bill.total_amount || 0}" required 
                                   style="background: #f5f5f5; font-weight: bold; font-size: 16px;">
                        </div>
                        
                        <div class="form-group">
                            <label>Payment Status *</label>
                            <select id="payment_status" required>
                                <option value="Pending" ${bill.payment_status === 'Pending' ? 'selected' : ''}>Pending</option>
                                <option value="Paid" ${bill.payment_status === 'Paid' ? 'selected' : ''}>Paid</option>
                                <option value="Cancelled" ${bill.payment_status === 'Cancelled' ? 'selected' : ''}>Cancelled</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Payment Method</label>
                            <select id="payment_method">
                                <option value="">Select Method...</option>
                                <option value="Cash" ${bill.payment_method === 'Cash' ? 'selected' : ''}>Cash</option>
                                <option value="Card" ${bill.payment_method === 'Card' ? 'selected' : ''}>Card</option>
                                <option value="UPI" ${bill.payment_method === 'UPI' ? 'selected' : ''}>UPI</option>
                                <option value="Net Banking" ${bill.payment_method === 'Net Banking' ? 'selected' : ''}>Net Banking</option>
                                <option value="Cheque" ${bill.payment_method === 'Cheque' ? 'selected' : ''}>Cheque</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Notes</label>
                    <textarea id="notes" rows="3" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">${bill.notes || ''}</textarea>
                </div>
                
                <button type="submit" class="btn-success">Update Bill</button>
                <button type="button" onclick="showBilling()">Cancel</button>
            </form>
        `;
        
        // Calculate initial total
        calculateTotal();
    } catch (error) {
        alert('Error loading bill: ' + error.message);
    }
}

async function updateBill(event, billId) {
    event.preventDefault();
    
    const billData = {
        patient_id: document.getElementById('patient_id').value,
        appointment_id: document.getElementById('appointment_id').value || null,
        bill_date: document.getElementById('bill_date').value,
        consultation_fee: parseFloat(document.getElementById('consultation_fee').value) || 0,
        medicine_cost: parseFloat(document.getElementById('medicine_cost').value) || 0,
        other_charges: parseFloat(document.getElementById('other_charges').value) || 0,
        total_amount: parseFloat(document.getElementById('total_amount').value) || 0,
        payment_status: document.getElementById('payment_status').value,
        payment_method: document.getElementById('payment_method').value || '',
        notes: document.getElementById('notes').value || ''
    };

    try {
        await BillAPI.update(billId, billData);
        if (typeof showNotification === 'function') {
            showNotification('✅ Bill updated successfully!', 'success');
        } else {
            alert('Bill updated successfully!');
        }
        showBilling();
    } catch (error) {
        if (typeof showNotification === 'function') {
            showNotification('❌ Error updating bill: ' + error.message, 'error');
        } else {
            alert('Error updating bill: ' + error.message);
        }
    }
}

async function deleteBill(billId) {
    if (!confirm('Are you sure you want to delete this bill? This action cannot be undone.')) {
        return;
    }
    
    try {
        await BillAPI.delete(billId);
        if (typeof showNotification === 'function') {
            showNotification('✅ Bill deleted successfully!', 'success');
        } else {
            alert('Bill deleted successfully!');
        }
        loadBills();
    } catch (error) {
        if (typeof showNotification === 'function') {
            showNotification('❌ Error deleting bill: ' + error.message, 'error');
        } else {
            alert('Error deleting bill: ' + error.message);
        }
    }
}



