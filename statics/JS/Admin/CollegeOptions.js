const API_BASE = 'http://192.168.0.113:8000';

// Elements
const collegeContainer = document.getElementById('collegeContainer');
const departmentContainer = document.getElementById('departmentContainer');
const deptCollegeSelect = document.getElementById('deptCollegeSelect');
const addCollege =document.getElementById('addCollegeBtn')
const collegeNameInput=document.getElementById('collegeNameInput')
const addDepart =document.getElementById('addDeptBtn')
const departInputName =document.getElementById('deptNameInput')

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
            fetchCollegesItems(),
            fetchDepartmentsItems()
        ]);
    } catch (err) {
        console.error("Initialization Error:", err);
    }
}


// --- COLLEGE LOGIC ---
async function fetchCollegesItems() {
    const response = await fetch(`${API_BASE}/get_colleges_admin`);
    const rawColleges = await response.json();
    const colleges = rawColleges.filter(c => c.id !== 1);
    

    if (response.ok) {
        collegeContainer.innerHTML = colleges.map(c => `
        <div class="item-row">
           
            <div class="item-info">
                <div class="info">
                    <label>الكلية</label>
                    <span>${c.college}</span>
                </div>
            </div>
             <div>
                <button class="action-btn btn-rename" onclick="openRenameModal(${c.id})">تغير الاسم</button>
                <button class="action-btn btn-remove" onclick="openDeleteModal(${c.id}, 'college')">حذف</button>
            </div>
        </div>
    `).join('');

        deptCollegeSelect.innerHTML =`<option value=''>غير محدد</option>`   
        colleges.forEach(c => deptCollegeSelect.add(new Option(c.college, c.id)));     
        


    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }

}

addCollege.onclick = async () => {
    const name = collegeNameInput.value;
    if (!name) return alert("Enter college name");

    const response = await fetch(`${API_BASE}/add_college_admin/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });

    if (response.ok) {
        collegeNameInput.value = '';
        await fetchCollegesItems();
    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }
};

// --- DEPARTMENT LOGIC ---
async function fetchDepartmentsItems() {

    const response = await fetch(`${API_BASE}/get_departments_admin${deptCollegeSelect.value ? `?college_id=${deptCollegeSelect.value}` : ''}`);
    const depts = await response.json();

    if (response.ok) {
        departmentContainer.innerHTML = depts.map(d => `
        <div class="item-row">
            <div class="item-info">    
                <div class="info">
                    <label>الكلية</label>
                    <p>${d.college}</p>
                </div>    
                <div class="info">
                    <label>القسم</label>
                    <p>${d.department}</p>
                </div>
            </div>
            <div>
                <button id="toggle-${d.id}" 
                        data-status="${d.enabled === 'yes' ? 'yes' : 'no'}" 
                        class="action-btn ${d.enabled === 'yes' ? 'btn-enable' : 'btn-disable'}" 
                        onclick="toggleDepartmentStatus(${d.id}, 'toggle-${d.id}')">
                        ${d.enabled === 'yes' ? 'O' : 'X'}
                </button>
                <button class="action-btn btn-remove" onclick="openDeleteModal(${d.id}, 'department')">حذف</button>
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

deptCollegeSelect.addEventListener("change",fetchDepartmentsItems)

async function toggleDepartmentStatus(id, btnId) {
    const btn = document.getElementById(btnId);
    const isEnabled = (btn.dataset.status === 'yes');
    // API Call
    const response = await fetch(`${API_BASE}/toggle_department_admin/${id}`, {
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



addDepart.onclick = async () => {
    const coll = deptCollegeSelect.value;
    const name = departInputName.value;

    if (!name || !coll) return alert("Enter department name");

    const response = await fetch(`${API_BASE}/add_department_admin/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, college: coll })
    });

    if (response.ok) {
        departInputName.value = '';
        fetchDepartmentsItems();
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

    if (Type === 'college') {
        route = 'delete_college_admin';
    } else if (Type === 'department') {
        route = 'delete_department_admin';
    }


    if (!pass || pass !== conf) return alert("Passwords must match and cannot be empty.");

    const response = await fetch(`${API_BASE}/${route}/${ItemIdToDelete}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pass })
    });

    if (response.ok) {
        closeModal();
        await fetchDepartmentsItems();
        if (Type === 'college') {
            await fetchCollegesItems();
        }

    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }
};



let activeRenameId = null;
const renameInput=document.getElementById('newNameInput')
const renameModal=document.getElementById('changeNameModal')
const confirmNameChaneBtn= document.getElementById('confirmChangeBtn')

function openRenameModal(id) {
    activeRenameId = id;
    // Reset fields
    renameInput.value = '';
    renameModal.style.display = 'flex';
}

function closePassModal() {
    renameModal.style.display = 'none';
    activeRenameId = null;
}

// Handle the Update Button click
confirmNameChaneBtn.onclick = async () => {
    const newName = renameInput.value;

    if (!newName) {
        return alert("new name cannot be empty.");
    }

    const response = await fetch(`${API_BASE}/rename_college_admin/${activeRenameId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_name: newName })
    });

    if (response.ok) {
        alert("Name Changed successfully!");
        closePassModal();
        fetchCollegesItems()
        fetchDepartmentsItems()
    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Login Failed";

        alert("Error: " + errorMessage);
    }
};

init()