const API_BASE = 'http://192.168.0.113:8000';

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const payload = {
        cred: document.getElementById('username').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await fetch(`${API_BASE}/Login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {

            const data = await response.json();
            //alert(data.college);
            if (data.college === 1) {
                window.location.href = "/MainAdmin";
            } else {
                window.location.href = "/MainUser";
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