const API_BASE = 'http://192.168.0.113:8000';

// Elements
const collegeContainer = document.getElementById('collegeContainer');
const departmentContainer = document.getElementById('departmentContainer');
const deptCollegeSelect = document.getElementById('deptCollegeSelect');

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
            fetchCollegesItems(),
            fetchDepartmentsItems()
        ]);
    } catch (err) {
        console.error("Initialization Error:", err);
    }
})();


// --- COLLEGE LOGIC ---
async function fetchCollegesItems() {
    const response = await fetch(`${API_BASE}/get_colleges_admin`);
    const colleges = await response.json();

    if (response.ok) {
        collegeContainer.innerHTML = colleges.map(c => `
        <div class="item-row">
            <div class="item-info">
                <div class="info">
                    <label>College</label>
                    <span>${c.college}</span>
                </div>
            </div>
            <button class="action-btn btn-remove" onclick="openDeleteModal(${c.id}, 'college')">Delete</button>
        </div>
    `).join('');

        deptCollegeSelect.innerHTML = colleges.map(c =>
            `<option value="${c.id}">${c.college}</option>`
        ).join('');
    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }

}

document.getElementById('addCollegeBtn').onclick = async () => {
    const name = document.getElementById('collegeNameInput').value;
    if (!name) return alert("Enter college name");

    const response = await fetch(`${API_BASE}/add_college_admin/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });

    if (response.ok) {
        document.getElementById('collegeNameInput').value = '';
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
    const response = await fetch(`${API_BASE}/get_departments_admin`);
    const depts = await response.json();

    if (response.ok) {
        departmentContainer.innerHTML = depts.map(d => `
        <div class="item-row">
            <div class="item-info">
                <div class="info">
                    <label>College</label>
                    <span>${d.college}</span>
                </div>
                <div class="info">
                    <label>Department</label>
                    <span>${d.department}</span>
                </div>
            </div>
            <button class="action-btn btn-remove" onclick="openDeleteModal(${d.id}, 'department')">Delete</button>
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

document.getElementById('addDeptBtn').onclick = async () => {
    const college = deptCollegeSelect.value;
    const name = document.getElementById('deptNameInput').value;

    if (!name) return alert("Enter department name");

    const response = await fetch(`${API_BASE}/add_department_admin/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, college })
    });

    if (response.ok) {
        document.getElementById('deptNameInput').value = '';
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

function openDeleteModal(id, type) {
    ItemIdToDelete = id;
    Type = type;

    alert(type)

    document.getElementById('deleteConfirmPass').value = '';
    document.getElementById('deleteConfirmCheck').value = '';
    document.getElementById('passwordModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('passwordModal').style.display = 'none';
    ItemIdToDelete = null;
}

document.getElementById('confirmDeleteBtn').onclick = async () => {
    const pass = document.getElementById('deleteConfirmPass').value;
    const conf = document.getElementById('deleteConfirmCheck').value;
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
