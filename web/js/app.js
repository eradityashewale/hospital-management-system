/**
 * Main Application Logic
 */

// showAppointments() is now defined in appointments.js

// showPrescriptions() is now defined in prescriptions.js

// showBilling() is now defined in billing.js

async function showStatistics() {
    const content = document.getElementById('content');
    content.innerHTML = '<h2>Statistics</h2><div id="stats-content">Loading...</div>';
    
    try {
        const result = await StatisticsAPI.get();
        const stats = result.statistics;
        
        document.getElementById('stats-content').innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px;">
                <div style="padding: 20px; background: #e3f2fd; border-radius: 5px;">
                    <h3>Total Patients</h3>
                    <p style="font-size: 32px; font-weight: bold;">${stats.total_patients || 0}</p>
                </div>
                <div style="padding: 20px; background: #f3e5f5; border-radius: 5px;">
                    <h3>Total Doctors</h3>
                    <p style="font-size: 32px; font-weight: bold;">${stats.total_doctors || 0}</p>
                </div>
                <div style="padding: 20px; background: #e8f5e9; border-radius: 5px;">
                    <h3>Total Revenue</h3>
                    <p style="font-size: 32px; font-weight: bold;">₹${stats.total_revenue || 0}</p>
                </div>
                <div style="padding: 20px; background: #fff3e0; border-radius: 5px;">
                    <h3>Scheduled Appointments</h3>
                    <p style="font-size: 32px; font-weight: bold;">${stats.scheduled_appointments || 0}</p>
                </div>
                <div style="padding: 20px; background: #fce4ec; border-radius: 5px;">
                    <h3>Completed Appointments</h3>
                    <p style="font-size: 32px; font-weight: bold;">${stats.completed_appointments || 0}</p>
                </div>
            </div>
        `;
    } catch (error) {
        document.getElementById('stats-content').innerHTML = 
            '<p style="color: red;">Error loading statistics: ' + error.message + '</p>';
    }
}

// Check API health on load
window.addEventListener('load', async () => {
    try {
        const result = await apiCall('/health');
        console.log('API is healthy:', result);
    } catch (error) {
        alert('Warning: Cannot connect to API server. Make sure Flask is running on http://127.0.0.1:5000');
    }
});

