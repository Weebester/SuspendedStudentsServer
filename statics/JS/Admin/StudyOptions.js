const API_BASE = 'http://192.168.0.113:8000';

// Elements
const studyContainer = document.getElementById('studyContainer');
const subStudyContainer = document.getElementById('subStudyContainer');
const subStudySelect = document.getElementById('subStudySelect');
const addStudyBtn = document.getElementById('addStudyBtn');
const studyNameInput = document.getElementById('studyNameInput');
const addSub=document.getElementById('addSubBtn');
const subNameInput =document.getElementById('subNameInput');

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
            fetchStudiesItems(),
            fetchSubsItems()
        ]);
    } catch (err) {
        console.error("Initialization Error:", err);
    }
})();


// --- COLLEGE LOGIC ---
async function fetchStudiesItems() {
    const response = await fetch(`${API_BASE}/get_study_admin`);
    const studies = await response.json();

    if (response.ok) {
        studyContainer.innerHTML = studies.map(s => `
        <div class="item-row">
           
            <div class="item-info">
                <div class="info">
                    <label>المرحلة</label>
                    <span>${s.study}</span>
                </div>
            </div>
             <div>
                <button id="toggle-${s.id}" 
                        data-status="${s.enabled === 'yes' ? 'yes' : 'no'}" 
                        class="action-btn ${s.enabled === 'yes' ? 'btn-enable' : 'btn-disable'}" 
                        onclick="toggleStudyStatus(${s.id}, 'toggle-${s.id}')">
                        ${s.enabled === 'yes' ? 'O' : 'X'}
                </button>
                <button class="action-btn btn-remove" onclick="openDeleteModal(${s.id}, 'study')">حذف</button>
            </div>
        </div>
    `).join('');

        subStudySelect.innerHTML = `<option value=''>غير محدد</option>`
        studies.forEach(s => subStudySelect.add(new Option(s.study, s.id)));



    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }

}

async function toggleStudyStatus(id, btnId) {
    const btn = document.getElementById(btnId);
    const isEnabled = (btn.dataset.status === 'yes');
    // API Call
    const response = await fetch(`${API_BASE}/toggle_study_admin/${id}`, {
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


addStudyBtn.onclick = async () => {
    const name = studyNameInput.value;
    if (!name) return alert("Enter study name");

    const response = await fetch(`${API_BASE}/add_study_admin/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });

    if (response.ok) {
        studyNameInput.value = '';
        await fetchStudiesItems();
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

    const response = await fetch(`${API_BASE}/get_sub_study_admin${subStudySelect.value ? `?study_id=${subStudySelect.value}` : ''}`);
    const subs = await response.json();

    if (response.ok) {
        subStudyContainer.innerHTML = subs.map(ss => `
        <div class="item-row">
            <div class="item-info">    
                <div class="info">
                    <label>الكلية</label>
                    <p>${ss.study}</p>
                </div>    
                <div class="info">
                    <label>القسم</label>
                    <p>${ss.sub}</p>
                </div>
            </div>
            <div>
                <button id="toggle-S-${ss.id}" 
                        data-status="${ss.enabled === 'yes' ? 'yes' : 'no'}" 
                        class="action-btn ${ss.enabled === 'yes' ? 'btn-enable' : 'btn-disable'}" 
                        onclick="toggleSubStudyStatus(${ss.id}, 'toggle-S-${ss.id}')">
                        ${ss.enabled === 'yes' ? 'O' : 'X'}
                </button>
                <button class="action-btn btn-remove" onclick="openDeleteModal(${ss.id}, 'sub')">حذف</button>
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

subStudySelect.addEventListener("change", fetchSubsItems)

async function toggleSubStudyStatus(id, btnId) {
    const btn = document.getElementById(btnId);
    const isEnabled = (btn.dataset.status === 'yes');
    // API Call
    const response = await fetch(`${API_BASE}/toggle_sub_study_admin/${id}`, {
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


addSub.onclick = async () => {
    const study = subStudySelect.value;
    const name = subNameInput.value;

    if (!name || !study) return alert("Enter sub name");

    const response = await fetch(`${API_BASE}/add_sub_study_admin/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, study: study })
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

    if (Type === 'study') {
        route = 'delete_study_admin';
    } else if (Type === 'sub') {
        route = 'delete_sub_study_admin';
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
        if (Type === 'study') {
            await fetchStudiesItems();
        }

    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }
};
