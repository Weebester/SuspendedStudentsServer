const API_BASE = 'http://192.168.0.113:8000';

// Global State
let activeCollegeIdToDelete = null;

// Elements
const collegeContainer = document.getElementById('collegeContainer');
const departmentContainer = document.getElementById('departmentContainer');
const deptCollegeSelect = document.getElementById('deptCollegeSelect');

// --- INITIALIZATION ---
(async () => {
    try {
        // Fetch dropdown items and both lists independently
        await Promise.all([
            fetchCollegesList(),
            fetchCollegesItems(),
            fetchDepartmentsItems()
        ]);
    } catch (err) {
        console.error("Initialization Error:", err);
    }
})();

// --- SIDE MENU TOGGLE ---
function toggleOptions() {
    const list = document.getElementById("OptionsList");
    if (!list) return;
    list.style.display = (list.style.display === "block") ? "none" : "block";
}

// --- SELECTOR LOGIC (Separate Path) ---
async function fetchCollegesList() {
    try {
        const res = await fetch(`${API_BASE}/get_colleges_list`); // Separate path
        const items = await res.json();
        deptCollegeSelect.innerHTML = items.map(name => 
            `<option value="${name}">${name}</option>`
        ).join('');
    } catch (err) {
        console.error("Selector Fetch Error:", err);
    }
}

// --- COLLEGE LOGIC ---
async function fetchCollegesItems() {
    const res = await fetch(`${API_BASE}/get_colleges_list`);
    const colleges = await res.json();

    collegeContainer.innerHTML = colleges.map(c => `
        <div class="account-row">
            <div class="account-info">
                <div class="info-item">
                    <label>College</label>
                    <span>${c.name}</span>
                </div>
            </div>
            <button class="action-btn btn-remove" onclick="openDeleteModal(${c.id})">Delete</button>
        </div>
    `).join('');
}

document.getElementById('addCollegeBtn').onclick = async () => {
    const name = document.getElementById('collegeNameInput').value;
    if (!name) return alert("Enter college name");

    const res = await fetch(`${API_BASE}/add_college/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });

    if (res.ok) {
        document.getElementById('collegeNameInput').value = '';
        await fetchCollegesItems();
        await fetchCollegesList(); // Refresh selector in case names changed
    }
};

// --- DEPARTMENT LOGIC ---
async function fetchDepartmentsItems() {
    const res = await fetch(`${API_BASE}/get_departments_list`);
    const depts = await res.json();

    departmentContainer.innerHTML = depts.map(d => `
        <div class="account-row">
            <div class="account-info">
                <div class="info-item">
                    <label>College</label>
                    <span>${d.college}</span>
                </div>
                <div class="info-item">
                    <label>Department</label>
                    <span>${d.name}</span>
                </div>
            </div>
            <button class="action-btn btn-remove" onclick="deleteDepartment(${d.id})">Delete</button>
        </div>
    `).join('');
}

document.getElementById('addDeptBtn').onclick = async () => {
    const college = deptCollegeSelect.value;
    const name = document.getElementById('deptNameInput').value;

    if (!name) return alert("Enter department name");

    const res = await fetch(`${API_BASE}/add_department/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, college })
    });

    if (res.ok) {
        document.getElementById('deptNameInput').value = '';
        fetchDepartmentsItems();
    }
};

// --- DELETE & MODAL LOGIC ---
function openDeleteModal(id) {
    activeCollegeIdToDelete = id;
    document.getElementById('deleteConfirmPass').value = '';
    document.getElementById('deleteConfirmCheck').value = '';
    document.getElementById('passwordModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('passwordModal').style.display = 'none';
    activeCollegeIdToDelete = null;
}

document.getElementById('confirmDeleteBtn').onclick = async () => {
    const pass = document.getElementById('deleteConfirmPass').value;
    const conf = document.getElementById('deleteConfirmCheck').value;

    if (!pass || pass !== conf) return alert("Passwords must match and cannot be empty.");

    const res = await fetch(`${API_BASE}/delete_college/${activeCollegeIdToDelete}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pass }) // Sending password for verification
    });

    if (res.ok) {
        closeModal();
        await fetchCollegesItems();
        await fetchCollegesList();
    } else {
        alert("Delete failed. Check password or permissions.");
    }
};

async function deleteDepartment(id) {
    if (!confirm("Delete this department?")) return;
    const res = await fetch(`${API_BASE}/delete_department/${id}`, { method: 'DELETE' });
    if (res.ok) fetchDepartmentsItems();
}