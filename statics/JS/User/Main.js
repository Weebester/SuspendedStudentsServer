const API_BASE = 'http://192.168.0.113:8000';

const Accepted =document.getElementById('count-accepted');
const Denied = document.getElementById('count-denied');
const Pending = document.getElementById('count-pending');

const init =async () => {

    const response = await fetch(`${API_BASE}/stats`);
    if (response.ok) {
        const data = await response.json();

        Accepted.textContent = data.Accepted;
        Denied.textContent = data.Denied;
        Pending.textContent = data.Pending;

    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }



}

init();

