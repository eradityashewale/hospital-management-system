/**
 * API Helper Functions
 * Simple wrapper around Fetch API for calling Flask backend
 */

const API_URL = 'http://127.0.0.1:5000/api';

/**
 * Generic API call function
 */
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_URL}${endpoint}`, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'API request failed');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        alert('Error: ' + error.message);
        throw error;
    }
}

/**
 * Patient API functions
 */
const PatientAPI = {
    getAll: () => apiCall('/patients'),
    search: (query) => apiCall(`/patients?search=${encodeURIComponent(query)}`),
    getById: (id) => apiCall(`/patients/${id}`),
    create: (data) => apiCall('/patients', 'POST', data),
    update: (id, data) => apiCall(`/patients/${id}`, 'PUT', data)
};

/**
 * Doctor API functions
 */
const DoctorAPI = {
    getAll: () => apiCall('/doctors'),
    getById: (id) => apiCall(`/doctors/${id}`),
    create: (data) => apiCall('/doctors', 'POST', data),
    update: (id, data) => apiCall(`/doctors/${id}`, 'PUT', data),
    delete: (id) => apiCall(`/doctors/${id}`, 'DELETE')
};

/**
 * Appointment API functions
 */
const AppointmentAPI = {
    getAll: () => apiCall('/appointments'),
    getByDate: (date) => apiCall(`/appointments?date=${date}`),
    getById: (id) => apiCall(`/appointments/${id}`),
    create: (data) => apiCall('/appointments', 'POST', data),
    update: (id, data) => apiCall(`/appointments/${id}`, 'PUT', data)
};

/**
 * Prescription API functions
 */
const PrescriptionAPI = {
    getAll: () => apiCall('/prescriptions'),
    getById: (id) => apiCall(`/prescriptions/${id}`),
    create: (data) => apiCall('/prescriptions', 'POST', data),
    update: (id, data) => apiCall(`/prescriptions/${id}`, 'PUT', data)
};

/**
 * Bill API functions
 */
const BillAPI = {
    getAll: () => apiCall('/bills'),
    getById: (id) => apiCall(`/bills/${id}`),
    create: (data) => apiCall('/bills', 'POST', data),
    update: (id, data) => apiCall(`/bills/${id}`, 'PUT', data),
    delete: (id) => apiCall(`/bills/${id}`, 'DELETE')
};

/**
 * Statistics API functions
 */
const StatisticsAPI = {
    get: (filterType = 'all', filterDate = null) => {
        let url = `/statistics?filter_type=${filterType}`;
        if (filterDate) url += `&filter_date=${filterDate}`;
        return apiCall(url);
    },
    getTodayAppointments: () => apiCall('/appointments/today')
};

/**
 * Medicine API functions
 */
const MedicineAPI = {
    getAll: (page = 1, limit = 50) => apiCall(`/medicines?page=${page}&limit=${limit}`),
    search: (query) => apiCall(`/medicines?search=${encodeURIComponent(query)}`),
    getAutocomplete: () => apiCall('/medicines/autocomplete')
};

