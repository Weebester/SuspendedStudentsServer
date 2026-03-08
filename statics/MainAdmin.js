const API_BASE = 'http://192.168.0.113:8000';
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/Stats`);
        if (!response.ok) throw new Error('Network error');

        const data = await response.json();
        document.getElementById('count-accepted').textContent = data.Accepted;
        document.getElementById('count-denied').textContent = data.Denied;
        document.getElementById('count-pending').textContent = data.Pending;

    } catch (error) {
        console.error("Failed to load stats:", error);
    }
}

document.addEventListener('DOMContentLoaded', loadStats);