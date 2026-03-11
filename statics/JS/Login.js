const API_BASE = 'http://192.168.0.113:8000';

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const payload = {
        cred: document.getElementById('username').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {

            const data = await response.json();
            
            if (data.college_id  < 2) {
                window.location.href = "/Admin/Main";
            } else {
                window.location.href = "/User/Main";
            }
        } else {
            const errorData = await response.json();

            const errorMessage = errorData.detail || "Login Failed";

            alert("Error: " + errorMessage);
        }
    } catch (error) {
        alert("Error:", error);
    }
});