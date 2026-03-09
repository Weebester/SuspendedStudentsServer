const API_BASE = 'http://192.168.0.113:8000';
async function loadStats() {


    const response = await fetch(`${API_BASE}/stats`);
    if (response.ok) {
        const data = await response.json();

        document.getElementById('count-accepted').textContent = data.Accepted;
        document.getElementById('count-denied').textContent = data.Denied;
        document.getElementById('count-pending').textContent = data.Pending;

    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }



}

loadStats();

function toggleOptions() {
    const list = document.getElementById("OptionsList");
    if (list.style.display === "block") {
        list.style.display = "none";
    } else {
        list.style.display = "block";
    }
}