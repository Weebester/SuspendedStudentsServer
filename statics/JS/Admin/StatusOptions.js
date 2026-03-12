const API_BASE = 'http://192.168.0.113:8000';

const StatusContainer = document.getElementById('statusContainer');
const AddStatusBtn = document.getElementById('addStatusBtn')
const jobStatusNameInput=document.getElementById('statusNameInput');


// --- SIDE MENU TOGGLE ---
function toggleOptions() {
    const list = document.getElementById("OptionsList");
    if (!list) return;
    list.style.display = (list.style.display === "block") ? "none" : "block";
}

// --- INITIALIZATION ---
(async () => {
    try {
        // Fetch dropdown items and both lists independently
        await Promise.all([
            fetchStatusItems(),
        ]);
    } catch (err) {
        console.error("Initialization Error:", err);
    }
})();


// --- COLLEGE LOGIC ---
async function fetchStatusItems() {
    const response = await fetch(`${API_BASE}/get_status_admin`);
    const status = await response.json();

    if (response.ok) {
        StatusContainer.innerHTML = status.map(s => `
        <div class="item-row">
           
            <div class="item-info">
                <div class="info">
                    <label>الحالة</label>
                    <span>${s.status}</span>
                </div>
            </div>
             <div>
                <button id="toggle-${s.id}" 
                        data-status="${s.enabled === 'yes' ? 'yes' : 'no'}" 
                        class="action-btn ${s.enabled === 'yes' ? 'btn-enable' : 'btn-disable'}" 
                        onclick="toggleJobStatus(${s.id}, 'toggle-${s.id}')">
                        ${s.enabled === 'yes' ? 'O' : 'X'}
                </button>
                <button class="action-btn btn-remove" onclick="openDeleteModal(${s.id})">حذف</button>
            </div>
        </div>
    `).join('');

        jobStatusSelect.innerHTML =`<option value=''>غير محدد</option>`   
        status.forEach(s => jobStatusSelect.add(new Option(s.status, s.id)));     
        


    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }

}

async function toggleJobStatus(id, btnId) {
    const btn = document.getElementById(btnId);
    const isEnabled = (btn.dataset.status === 'yes');
    // API Call
    const response = await fetch(`${API_BASE}/toggle_status_admin/${id}`, {
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

AddStatusBtn.onclick = async () => {
    const name = jobStatusNameInput.value;
    if (!name) return alert("Enter name");

    const response = await fetch(`${API_BASE}/add_status_admin/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });

    if (response.ok) {
        jobStatusNameInput.value = '';
        await fetchStatusItems();
    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }
};

// --- DELETE ---
let ItemIdToDelete = null;

const deletePass=document.getElementById('deleteConfirmPass')
const deletePassConfirm= document.getElementById('deleteConfirmCheck')
const passwordModal= document.getElementById('passwordModal')
const confirmDeleteBtn=document.getElementById('confirmDeleteBtn')


function openDeleteModal(id) {
    ItemIdToDelete = id;

    deletePass.value = '';
    deletePassConfirm.value = '';
    passwordModal.style.display = 'flex';
}

function closeModal() {
    passwordModal.style.display = 'none';
    ItemIdToDelete = null;
}

confirmDeleteBtn.onclick = async () => {
    const pass = deletePass.value;
    const conf = deletePassConfirm.value;


    if (!pass || pass !== conf) return alert("Passwords must match and cannot be empty.");

    const response = await fetch(`${API_BASE}/delete_status_admin/${ItemIdToDelete}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pass })
    });

    if (response.ok) {
        closeModal();
        await fetchStatusItems();

    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }
};

