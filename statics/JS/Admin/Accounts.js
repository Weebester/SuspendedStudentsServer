const API_BASE = 'http://192.168.0.113:8000';
const collegeSelect = document.getElementById('collegeInput');
const container = document.getElementById('accountContainer');
const addAccountBtn= document.getElementById('addAccountBtn');
const userNameInput= document.getElementById('usernameInput');
const userPasswordInput= document.getElementById('passwordInput');
const userConfirmPass= document.getElementById('confirmPasswordInput');

let activeAccountId = null;

// Procedural Start
const init =async () => {
    try {
        // 1. Populate Colleges (No "Any")
        const colleges = await fetch(`${API_BASE}/get_colleges_admin`).then(r => r.json());
        colleges.forEach(c => collegeSelect.add(new Option(c.college, c.id)));

        // 2. Fetch Initial Account List
        await fetchAccounts();
    } catch (err) {
        console.error("Init Error:", err);
    }
}

async function fetchAccounts() {
    const res = await fetch(`${API_BASE}/get_users${collegeSelect.value ? `?college_id=${collegeSelect.value}` : ''}`);
    const accounts = await res.json();

    container.innerHTML = accounts.map(acc => `
            <div class="account-row">
                
                <div class="account-info">
                    <div class="info-item"><label>اسم المستخدم</label><p>${acc.cred}</p></div>
                    <div class="info-item"><label>الكلية</label><p>${acc.college}</p></div>
                </div>
                <div class="account-actions">
                    <button id="toggle-${acc.id}" 
                        data-status="${acc.enabled === 'yes' ? 'yes' : 'no'}" 
                        class="action-btn ${acc.enabled === 'yes' ? 'btn-enable' : 'btn-disable'}" 
                        onclick="toggleUserStatus(${acc.id}, 'toggle-${acc.id}')">
                        ${acc.enabled === 'yes' ? 'O' : 'X'}
                    </button>
                    <button class="action-btn btn-change-pw" onclick="openPassModal(${acc.id})">تغير الرمز</button>  
                    <button class="action-btn btn-remove" onclick="deleteAccount(${acc.id})">حذف</button>
                </div>
            </div>
        `).join('');
}

collegeSelect.addEventListener('change', fetchAccounts);


async function toggleUserStatus(id, btnId) {
    const btn = document.getElementById(btnId);
    const isEnabled = (btn.dataset.status === 'yes');
    // API Call
    const response = await fetch(`${API_BASE}/toggle_user/${id}`, {
        method: 'PATCH'
    });

    if (response.ok) {
        const nextStatus = isEnabled ? 'no' : 'yes';
        // Update Data Source
        btn.dataset.status = nextStatus;
        btn.textContent = (nextStatus === 'yes') ? 'O' : 'X';
        btn.className = (nextStatus === 'yes') ? 'action-btn btn-enable' : 'action-btn btn-disable';
    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Login Failed";

        alert("Error: " + errorMessage);
    }

}

async function toggleAllUsers(bool) {

    const response = await fetch(`${API_BASE}/toggle_all_users?enable=${bool}`, {
        method: 'PATCH'
    });

    if (response.ok) {
        fetchAccounts();
    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Login Failed";

        alert("Error: " + errorMessage);
    }

}

let activePassUpdateId = null;

const newPassInput=document.getElementById('newPassInput');
const comfirmNewPassInput=document.getElementById('confirmNewPassInput');
const changePassModal=document.getElementById('changePassModal');
const confirmChange=document.getElementById('confirmChangeBtn');

function openPassModal(id) {
    activePassUpdateId = id;

    // Reset fields
    newPassInput.value = '';
    comfirmNewPassInput.value = '';

    changePassModal.style.display = 'flex';
}

function closePassModal() {
    changePassModal.style.display = 'none';
    activePassUpdateId = null;
}

// Handle the Update Button click
confirmChange.onclick = async () => {
    const newPass = newPassInput.value;
    const confirmPass = comfirmNewPassInput.value;

    if (!newPass || newPass !== confirmPass) {
        return alert("Passwords must match and cannot be empty.");
    }

    const response = await fetch(`${API_BASE}/change_pass_user/${activePassUpdateId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: newPass })
    });

    if (response.ok) {
        alert("Password updated successfully!");
        closePassModal();
    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Login Failed";

        alert("Error: " + errorMessage);
    }
};

function closeModal() {
    const modal = passModal;
    if (modal) {
        modal.style.display = 'none'; // Hides the overlay

        // Clear the inputs so they are empty next time you open it
        deletePass.value = '';
        confirmSeletePass.value = '';
        activeAccountIdToDelete = null;
        activeCollegeIdToDelete = null;
    }
}

let activeAccountIdToDelete = null;

const deletePass=document.getElementById('deleteConfirmPass');
const confirmSeletePass=document.getElementById('deleteConfirmCheck');
const passModal=document.getElementById('passwordModal');
const confirmDeleteBtn=document.getElementById('confirmDeleteBtn');


function deleteAccount(id) {
    activeAccountIdToDelete = id;

    // Reset modal inputs
    deletePass.value = '';
    confirmSeletePass.value = '';

    // Show modal
    passModal.style.display = 'flex';
}

// Update the Modal's "Confirm" button logic for the Accounts page
confirmDeleteBtn.onclick = async () => {
    const pass = deletePass.value;
    const conf = confirmSeletePass.value;

    if (!pass || pass !== conf) {
        return alert("Passwords must match and cannot be empty.");
    }

    const response = await fetch(`${API_BASE}/delete_user/${activeAccountIdToDelete}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pass })
    });

    if (response.ok) {
        closeModal();
        fetchAccounts();
    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }
};

addAccountBtn.onclick = async () => {
    const user = userNameInput.value;
    const pass = userPasswordInput.value;
    const conf = userConfirmPass.value;
    const coll = collegeSelect.value;

    if (!user || !pass || !conf || !coll) return alert("Fill all fields");
    if (pass !== conf) return alert("Passwords mismatch");
    const response = await fetch(`${API_BASE}/add_user/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cred: user, password: pass, college_id: coll })
    });

    if (response.ok) {
        fetchAccounts();
    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
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

init();