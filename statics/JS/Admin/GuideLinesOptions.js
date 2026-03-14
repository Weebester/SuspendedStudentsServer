const API_BASE = 'http://192.168.0.113:8000';

const Container = document.getElementById('Container');
const AddBtn = document.getElementById('addBtn')
const NameInput=document.getElementById('NameInput');
const fileInput=document.getElementById('file')


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
            fetchFilesNames(),
        ]);
    } catch (err) {
        console.error("Initialization Error:", err);
    }
}


async function fetchFilesNames() {
    const response = await fetch(`${API_BASE}/get_guidlines`);
    const filesNames = await response.json();

    if (response.ok) {
        Container.innerHTML = filesNames.map(f => `
        <div class="item-row">
           
            <div class="item-info">
                <div class="info">
                    <label>اسم الملف</label>
                    <span>${f}</span>
                </div>
            </div>
             <div>
                <button class="action-btn btn-enable" 
                    onclick="window.location.href='/static/rules/${f}.pdf' ">
                    اطلاع
                </button>
                <button class="action-btn btn-remove" onclick="openDeleteModal('${f}')">حذف</button>
            </div>
        </div>
    `).join('');


    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }

}


AddBtn.onclick = async () => {
    const name = NameInput.value;
    if (!name) return alert("Enter name");

    if (!fileInput.files[0]) {
        alert("يرجى اختيار ملف أولاً");
        return;
    }

    const fData = new FormData();
    fData.append("file_pdf", fileInput.files[0]);

    
    const response = await fetch(`${API_BASE}/upload_pdf/${name}`, {
        method: "POST",
        body: fData
    });

    if (response.ok) {
        NameInput.value = '';
        await fetchFilesNames();
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }

    
  
};

// --- DELETE ---
let FileToDelete = null;

const deletePass=document.getElementById('deleteConfirmPass')
const deletePassConfirm= document.getElementById('deleteConfirmCheck')
const passwordModal= document.getElementById('passwordModal')
const confirmDeleteBtn=document.getElementById('confirmDeleteBtn')


function openDeleteModal(Name) {
    FileToDelete = Name;

    deletePass.value = '';
    deletePassConfirm.value = '';
    passwordModal.style.display = 'flex';
}

function closeModal() {
    passwordModal.style.display = 'none';
    FileToDelete = null;
}

confirmDeleteBtn.onclick = async () => {
    const pass = deletePass.value;
    const conf = deletePassConfirm.value;


    if (!pass || pass !== conf) return alert("Passwords must match and cannot be empty.");

    const response = await fetch(`${API_BASE}/delete_pdf/${FileToDelete}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pass })
    });

    if (response.ok) {
        closeModal();
        await fetchFilesNames();

    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }
};

init();