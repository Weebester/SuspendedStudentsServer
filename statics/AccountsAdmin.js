const API_BASE = 'http://192.168.0.113:8000';
const collegeSelect = document.getElementById('collegeInput');
const container = document.getElementById('accountContainer');
let activeAccountId = null;

// Procedural Start
(async () => {
    try {
        // 1. Populate Colleges (No "Any")
        const colleges = await fetch(`${API_BASE}/get_colleges_list`).then(r => r.json());
        colleges.forEach(c => collegeSelect.add(new Option(c, c)));

        // 2. Fetch Initial Account List
        await fetchAccounts();
    } catch (err) {
        console.error("Init Error:", err);
    }
})();

async function fetchAccounts() {
    const res = await fetch(`${API_BASE}/get_users_list`);
    const accounts = await res.json();

    container.innerHTML = accounts.map(acc => `
            <div class="account-row">
                <div class="account-info">
                    <div class="info-item"><label>Username</label><span>${acc.cred}</span></div>
                    <div class="info-item"><label>College</label><span>${acc.college}</span></div>
                </div>
                <div class="account-actions">
                    <button class="action-btn btn-change-pw" onclick="openPassModal(${acc.id}, '${acc.cred}')">Change Password</button>
                    <button class="action-btn btn-remove" onclick="deleteAccount(${acc.id})">Remove</button>
                </div>
            </div>
        `).join('');
}

// Modal Control
function openPassModal(id, username) {
    activeAccountId = id;
    document.getElementById('modalUserInfo').textContent = `User: ${cred}`;
    document.getElementById('modalNewPass').value = '';
    document.getElementById('passwordModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('passwordModal').style.display = 'none';
    activeAccountId = null;
}

// Password Update Submission
document.getElementById('confirmPassBtn').onclick = async () => {
    const password = document.getElementById('modalNewPass').value;
    if (!password) return alert("Enter a password");

    const res = await fetch(`${API_BASE}/accounts/${activeAccountId}/password`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
    });

    if (res.ok) {
        alert("Updated!");
        closeModal();
    }
};

// Remove Account
async function deleteAccount(id) {
    if (!confirm("Remove this account?")) return;
    await fetch(`${API_BASE}/delete_user/${id}`, { method: 'DELETE' });
    fetchAccounts();
}

// Add Account
document.getElementById('addAccountBtn').onclick = async () => {
    const user = document.getElementById('usernameInput').value;
    const pass = document.getElementById('passwordInput').value;
    const conf = document.getElementById('confirmPasswordInput').value;
    const coll = collegeSelect.value;

    if (!user || !pass || !conf) return alert("Fill all fields");
    if (pass !== conf) return alert("Passwords mismatch");
    const res = await fetch(`${API_BASE}/add_user/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cred: user, password: pass, college: coll })
    });

    if (res.ok) {
        fetchAccounts();
    } else {
        const errorData = await res.json();
        const errorMessage = errorData.detail;

        alert("Error: " + (errorMessage || "Failed to add account"));
    }
};