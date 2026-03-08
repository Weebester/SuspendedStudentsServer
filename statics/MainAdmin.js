const API_BASE = 'http://192.168.0.113:8000';
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/Stats`);
        if (!response.ok) throw new Error('Network error');

        const data = await response.json();
        // Tip: Use optional chaining or check if elements exist to prevent errors
        document.getElementById('count-accepted').textContent = data.Accepted;
        document.getElementById('count-denied').textContent = data.Denied;
        document.getElementById('count-pending').textContent = data.Pending;

    } catch (error) {
        console.error("Failed to load stats:", error);
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