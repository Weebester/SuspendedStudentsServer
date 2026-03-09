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
    const res = await fetch(`${API_BASE}/get_users_admin`);
    const accounts = await res.json();

    container.innerHTML = accounts.map(acc => `
            <div class="account-row">
                <div class="account-info">
                    <div class="info-item"><label>Username</label><span>${acc.cred}</span></div>
                    <div class="info-item"><label>College</label><span>${acc.college}</span></div>
                    <div class="info-item"><label>Enabled?:</label><span>${acc.enabled}</span></div>
                </div>
                <div class="account-actions">
                    <button class="action-btn btn-enable" onclick="placeholder(${acc.id}, true)">enable</button>
                    <button class="action-btn btn-disable" onclick="placeholder(${acc.id}, false)">disable</button>
                    <button class="action-btn btn-change-pw" onclick="openPassModal(${acc.id})">Change Password</button>
                    <button class="action-btn btn-remove" onclick="deleteAccount(${acc.id})">Remove</button>
                </div>
            </div>
        `).join('');
}

let activePassUpdateId = null;

// Called by the "Change Password" button in your list
function openPassModal(id) {
    activePassUpdateId = id;
    
    // Reset fields
    document.getElementById('newPassInput').value = '';
    document.getElementById('confirmNewPassInput').value = '';
    
    document.getElementById('changePassModal').style.display = 'flex';
}

function closePassModal() {
    document.getElementById('changePassModal').style.display = 'none';
    activePassUpdateId = null;
}

// Handle the Update Button click
document.getElementById('confirmChangeBtn').onclick = async () => {
    const newPass = document.getElementById('newPassInput').value;
    const confirmPass = document.getElementById('confirmNewPassInput').value;

    if (!newPass || newPass !== confirmPass) {
        return alert("Passwords must match and cannot be empty.");
    }

    const res = await fetch(`${API_BASE}/accounts/${activePassUpdateId}/password`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: newPass })
    });

    if (res.ok) {
        alert("Password updated successfully!");
        closePassModal();
    } else {
        alert("Failed to update password.");
    }
};

function closeModal() {
    const modal = document.getElementById('passwordModal');
    if (modal) {
        modal.style.display = 'none'; // Hides the overlay
        
        // Clear the inputs so they are empty next time you open it
        document.getElementById('deleteConfirmPass').value = '';
        document.getElementById('deleteConfirmCheck').value = '';
        activeAccountIdToDelete = null;
        activeCollegeIdToDelete = null;
    }
}

let activeAccountIdToDelete = null;

// Replace your old deleteAccount function with this
function deleteAccount(id) {
    activeAccountIdToDelete = id;
    
    // Reset modal inputs
    document.getElementById('deleteConfirmPass').value = '';
    document.getElementById('deleteConfirmCheck').value = '';
    
    // Update modal text for clarity (Optional)
    document.getElementById('modalUserInfo').textContent = "Confirming account deletion. Please enter your password.";
    
    // Show modal
    document.getElementById('passwordModal').style.display = 'flex';
}

// Update the Modal's "Confirm" button logic for the Accounts page
document.getElementById('confirmDeleteBtn').onclick = async () => {
    const pass = document.getElementById('deleteConfirmPass').value;
    const conf = document.getElementById('deleteConfirmCheck').value;

    if (!pass || pass !== conf) {
        return alert("Passwords must match and cannot be empty.");
    }

    const res = await fetch(`${API_BASE}/delete_user/${activeAccountIdToDelete}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pass })
    });

    if (res.ok) {
        closeModal();
        fetchAccounts();
    } else {
        alert("Delete failed. Please check your password.");
    }
};

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

function toggleOptions() {
    const list = document.getElementById("OptionsList");
    if (list.style.display === "block") {
        list.style.display = "none";
    } else {
        list.style.display = "block";
    }
}