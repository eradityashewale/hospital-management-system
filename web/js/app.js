/**
 * Main Application Logic
 */

// showAppointments() is now defined in appointments.js

// showPrescriptions() is now defined in prescriptions.js

// showBilling() is now defined in billing.js

async function showStatistics() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>📊 Statistics Dashboard</h2>
        <div id="stats-content">
            <div class="loading">
                <div class="spinner"></div>
            </div>
        </div>
    `;
    
    try {
        const result = await StatisticsAPI.get();
        const stats = result.statistics;
        
        document.getElementById('stats-content').innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Patients</h3>
                    <div class="value">${stats.total_patients || 0}</div>
                </div>
                <div class="stat-card">
                    <h3>Total Doctors</h3>
                    <div class="value">${stats.total_doctors || 0}</div>
                </div>
                <div class="stat-card">
                    <h3>Total Revenue</h3>
                    <div class="value">₹${(stats.total_revenue || 0).toLocaleString('en-IN')}</div>
                </div>
                <div class="stat-card">
                    <h3>Scheduled Appointments</h3>
                    <div class="value">${stats.scheduled_appointments || 0}</div>
                </div>
                <div class="stat-card">
                    <h3>Completed Appointments</h3>
                    <div class="value">${stats.completed_appointments || 0}</div>
                </div>
            </div>
        `;
    } catch (error) {
        document.getElementById('stats-content').innerHTML = 
            `<div class="alert alert-error">❌ Error loading statistics: ${error.message}</div>`;
    }
}

// Utility function to show notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.style.maxWidth = '400px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Utility function to show loading state
function showLoading(element) {
    element.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
}

// Check API health on load
window.addEventListener('load', async () => {
    try {
        const result = await apiCall('/health');
        console.log('API is healthy:', result);
    } catch (error) {
        showNotification('⚠️ Cannot connect to API server. Make sure Flask is running on http://127.0.0.1:5000', 'error');
    }
});

