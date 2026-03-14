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
            </div>
        </div>
    `).join('');


    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }

}


init();