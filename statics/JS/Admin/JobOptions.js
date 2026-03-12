const API_BASE = 'http://192.168.0.113:8000';

const jobStatusContainer = document.getElementById('jobStatusContainer');
const subjobStatusContainer = document.getElementById('subJobStatusContainer');
const jobStatusNameInput=document.getElementById('jobStatusNameInput');
const jobStatusSelect = document.getElementById('jobStatusSelect');
const AddStatusBtn = document.getElementById('addJobStatusBtn')
const addSubBtn = document.getElementById('addSubBtn');
const subNameInput = document.getElementById('subNameInput');


// --- SIDE MENU TOGGLE ---
function toggleOptions() {
    const list = document.getElementById("OptionsList");
    if (!list) return;
    list.style.display = (list.style.display === "block") ? "none" : "block";
}

// --- INITIALIZATION ---
const init =async () => {
    try {
        // Fetch dropdown items and both lists independently
        await Promise.all([
            fetchStatusItems(),
            fetchSubsItems()
        ]);
    } catch (err) {
        console.error("Initialization Error:", err);
    }
}


// --- COLLEGE LOGIC ---
async function fetchStatusItems() {
    const response = await fetch(`${API_BASE}/get_job_status_admin`);
    const jobStatusies = await response.json();

    if (response.ok) {
        jobStatusContainer.innerHTML = jobStatusies.map(j => `
        <div class="item-row">
           
            <div class="item-info">
                <div class="info">
                    <label>الحالة الوظيفية</label>
                    <span>${j.status}</span>
                </div>
            </div>
             <div>
                <button id="toggle-${j.id}" 
                        data-status="${j.enabled === 'yes' ? 'yes' : 'no'}" 
                        class="action-btn ${j.enabled === 'yes' ? 'btn-enable' : 'btn-disable'}" 
                        onclick="toggleJobStatus(${j.id}, 'toggle-${j.id}')">
                        ${j.enabled === 'yes' ? 'O' : 'X'}
                </button>
                <button class="action-btn btn-remove" onclick="openDeleteModal(${j.id}, 'job_status')">حذف</button>
            </div>
        </div>
    `).join('');

        jobStatusSelect.innerHTML =`<option value=''>غير محدد</option>`   
        jobStatusies.forEach(s => jobStatusSelect.add(new Option(s.status, s.id)));     
        


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
    const response = await fetch(`${API_BASE}/toggle_job_status_admin/${id}`, {
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

    const response = await fetch(`${API_BASE}/add_job_status_admin/`, {
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

// --- DEPARTMENT LOGIC ---
async function fetchSubsItems() {

    const response = await fetch(`${API_BASE}/get_sub_job_status_admin${jobStatusSelect.value ? `?job_status_id=${jobStatusSelect.value}` : ''}`);
    const subs = await response.json();

    if (response.ok) {
        subjobStatusContainer.innerHTML = subs.map(sj => `
        <div class="item-row">
            <div class="item-info">    
                <div class="info">
                    <label>الكلية</label>
                    <p>${sj.status}</p>
                </div>    
                <div class="info">
                    <label>القسم</label>
                    <p>${sj.sub}</p>
                </div>
            </div>
            <div>
                <button id="toggle-S-${sj.id}" 
                        data-status="${sj.enabled === 'yes' ? 'yes' : 'no'}" 
                        class="action-btn ${sj.enabled === 'yes' ? 'btn-enable' : 'btn-disable'}" 
                        onclick="toggleSubJobStatus(${sj.id}, 'toggle-S-${sj.id}')">
                        ${sj.enabled === 'yes' ? 'O' : 'X'}
                </button>
                <button class="action-btn btn-remove" onclick="openDeleteModal(${sj.id}, 'sub')">حذف</button>
            </div>
        </div>
    `).join('');

    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }
}

jobStatusSelect.addEventListener("change",fetchSubsItems)

async function toggleSubJobStatus(id, btnId) {
    const btn = document.getElementById(btnId);
    const isEnabled = (btn.dataset.status === 'yes');
    // API Call
    const response = await fetch(`${API_BASE}/toggle_sub_job_status_admin/${id}`, {
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

addSubBtn.onclick = async () => {
    const job_status = jobStatusSelect.value;
    const name = subNameInput.value;
    
    if (!name || !job_status) return alert("Enter sub name");

    const response = await fetch(`${API_BASE}/add_sub_job_status_admin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name , job_status:job_status })
    });

    if (response.ok) {
        subNameInput.value = '';
        fetchSubsItems();
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
let Type = null;

const deletePass=document.getElementById('deleteConfirmPass')
const deletePassConfirm= document.getElementById('deleteConfirmCheck')
const passwordModal= document.getElementById('passwordModal')
const confirmDeleteBtn=document.getElementById('confirmDeleteBtn')


function openDeleteModal(id, type) {
    ItemIdToDelete = id;
    Type = type;

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
    let route = null

    if (Type === 'job_status') {
        route = 'delete_job_status_admin';
    } else if (Type === 'sub') {
        route = 'delete_sub_job_status_admin';
    }


    if (!pass || pass !== conf) return alert("Passwords must match and cannot be empty.");

    const response = await fetch(`${API_BASE}/${route}/${ItemIdToDelete}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pass })
    });

    if (response.ok) {
        closeModal();
        await fetchSubsItems();
        if (Type === 'job_status') {
            await fetchStatusItems();
        }

    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }
};

init()