const API_BASE = 'http://192.168.0.113:8000';

const YearContainer = document.getElementById('YearsContainer');
const AddYearBtn = document.getElementById('addYearBtn')
const YearSelector=document.getElementById('yearSelector');


// --- SIDE MENU TOGGLE ---
function toggleOptions() {
    const list = document.getElementById("OptionsList");
    if (!list) return;
    list.style.display = (list.style.display === "block") ? "none" : "block";
}

// --- INITIALIZATION ---
const init = async () => {
    try {
        // Fetch dropdown items and both lists independently
        await Promise.all([
            fetchYearsItems()
        ]);

        YearSelector.value = new Date().getFullYear();
    } catch (err) {
        console.error("Initialization Error:", err);
    }
}

// --- COLLEGE LOGIC ---
async function fetchYearsItems() {
    const response = await fetch(`${API_BASE}/get_edu_years_admin`);
    const years = await response.json();

    if (response.ok) {
        YearContainer.innerHTML = years.map(y => `
        <div class="item-row">
           
            <div class="item-info">
                <div class="info">
                    <label>السنة</label>
                    <span>${y.start_year}-${y.start_year + 1}</span>
                </div>
            </div>
             <div>
                <button id="toggle-${y.id}" 
                        data-status="${y.enabled === 'yes' ? 'yes' : 'no'}" 
                        class="action-btn ${y.enabled === 'yes' ? 'btn-enable' : 'btn-disable'}" 
                        onclick="toggleYear(${y.id}, 'toggle-${y.id}')">
                        ${y.enabled === 'yes' ? 'O' : 'X'}
                </button>
                <button class="action-btn btn-remove" onclick="openDeleteModal(${y.id})">حذف</button>
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

async function toggleYear(id, btnId) {
    const btn = document.getElementById(btnId);
    const isEnabled = (btn.dataset.status === 'yes');
    // API Call
    const response = await fetch(`${API_BASE}/toggle_edu_year_admin/${id}`, {
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

AddYearBtn.onclick = async () => {
    const year = YearSelector.value;
    if (!year) return alert("Enter Year");

    const response = await fetch(`${API_BASE}/add_edu_year_admin/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ year: year })
    });

    if (response.ok) {
        YearSelector.value = '';
        await fetchYearsItems();
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

    const response = await fetch(`${API_BASE}/delete_edu_year_admin/${ItemIdToDelete}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pass })
    });

    if (response.ok) {
        closeModal();
        await fetchYearsItems();

    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }
};

init();
