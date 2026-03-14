// --- Constants & Global State ---
const API_BASE = 'http://192.168.0.113:8000';
const form = document.getElementById('student-form');
const isEditable = document.body.getAttribute('admin').toLowerCase() === 'true';
const requestId = document.body.getAttribute('data-request-id');
const collegeId = document.body.getAttribute('college_id');

// Selectors
const selDept = document.getElementById('department');
const selStudy = document.getElementById('study-type');
const selSubStudy = document.getElementById('sub-study');
const selJobType = document.getElementById('job-type');
const selSubJob = document.getElementById('sub-job');
const selAccYear = document.getElementById('acceptance-year');
const selSusYear = document.getElementById('suspension-year');
const selBenefits = document.getElementById('benefits');
const selStatus = document.getElementById('status');


const inputName = document.getElementById('student-name');
const inputBirth = document.getElementById('birth-date');
const inputSpec = document.getElementById('speciality');
const txtReason = document.getElementById('suspension-reason');
const txtMsg = document.getElementById('message');

const FileBox = document.getElementById('filesBox')
const msgBox = document.getElementById('msgBox')

const file1 = document.getElementById('file-1');
const file2 = document.getElementById('file-2');
const file3 = document.getElementById('file-3');

const notesList = document.getElementById('notes-list');

const toggleCont = document.querySelector('.edit-toggle-container');
const submitCont = document.getElementById('submit-container');
const deleteCont = document.getElementById('delete-container')

function toggleOptions() {
    const list = document.getElementById("OptionsList");
    if (!list) return;
    list.style.display = (list.style.display === "block") ? "none" : "block";
}


let formData = {};

// --- Initialization & Main Logic ---
async function init() {
    if (!isEditable) {

        toggleCont.classList.add('hidden');

        submitCont.classList.add('hidden');

        FileBox.classList.add('hidden')

        deleteCont.classList.add('hidden')

        document.querySelectorAll('.field-group').forEach(group => {
            if (group.querySelector('.current-val')) {
                const input = group.querySelector('input, select, textarea');
                if (input) input.classList.add('hidden');
            }
        });


    } else {
        await loadFeedingData();
        document.querySelectorAll('.toggle-item input').forEach(checkbox => {
            checkbox.onchange = (e) => {
                const targetId = e.target.getAttribute('data-target');
                const targetInput = document.getElementById(targetId);
                if (targetInput) targetInput.disabled = !e.target.checked;
            };
        });
    }

    feedStatusSelector();
    fetchNotes();
}

async function feedStatusSelector() {
    try {
        const statusies = await fetch(`${API_BASE}/get_status_admin`).then(s => s.json());
        statusies.forEach(s => selStatus.add(new Option(s.status, s.status)));


    } catch (e) {
        if (notesList) notesList.innerText = "فشل تحميل سجل الملاحظات";
    }
}

async function fetchNotes() {
    try {
        const response = await fetch(`${API_BASE}/get_notes/${requestId}`);

        if (response.ok) {
            const notes = await response.json();

            notesList.innerHTML = notes.length
                ? notes.map(n => `
                    <div class="note-item ${n.state === 'Accepted' ? 'state-yes' : (n.state === 'Denied' ? 'state-no' : 'state-null')}">
                        <span class="note-msg">${n.messege}</span>
                        <span class="note-time">${n.date_time}</span>
                        </div>`).join('')
                : "لا توجد ملاحظات سابقة";

        } else {
            const err = await response.json();
            alert("حدث خطأ: " + (err.detail || "Error"));
        }

    } catch (e) {
        if (notesList) notesList.innerText = "فشل تحميل سجل الملاحظات";
    }
}

async function loadFeedingData() {
    try {
        const res = await fetch(`${API_BASE}/feed_form?college_id=${collegeId}`);
        formData = await res.json();
        formData.departments.forEach(d => selDept.add(new Option(d, d)));
        formData.years.forEach(y => {
            selAccYear.add(new Option(y, y));
            selSusYear.add(new Option(y, y));
        });
        Object.keys(formData.study).forEach(s => selStudy.add(new Option(s, s)));
        Object.keys(formData.job).forEach(j => selJobType.add(new Option(j, j)));

        selStudy.onchange = () => populateSubStudy();
        selJobType.onchange = () => populateSubJob();
    } catch (e) { console.error(e); }
}

function populateSubStudy() {
    const opts = formData.study[selStudy.value] || [];
    selSubStudy.innerHTML = '<option value="">-</option>';
    selSubStudy.disabled = !opts.length || selStudy.disabled;
    opts.forEach(o => selSubStudy.add(new Option(o, o)));
}

function populateSubJob() {
    const opts = formData.job[selJobType.value] || [];
    selSubJob.innerHTML = '<option value="">-</option>';
    selSubJob.disabled = !opts.length || selJobType.disabled;
    opts.forEach(o => selSubJob.add(new Option(o, o)));
}


form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!form.reportValidity()) return;

    const fData = new FormData();

    const fields = [
        { el: inputName, key: "student_name" },
        { el: inputBirth, key: "birth_date" },
        { el: selDept, key: "department" },
        { el: inputSpec, key: "speciality" },
        { el: selAccYear, key: "acception_year" },
        { el: selSusYear, key: "suspension_year" },
        { el: txtReason, key: "suspension_reason" },
        { el: selBenefits, key: "benefactor" }
    ];

    fields.forEach(f => {
        if (f.el && !f.el.disabled) fData.append(f.key, f.el.value);
    });

    if (!selStudy.disabled) fData.append("study", `${selStudy.value}-${selSubStudy.value}`);
    if (!selJobType.disabled) fData.append("job_status", `${selJobType.value}-${selSubJob.value}`);

    if (!file1.disabled && file1.files[0]) fData.append("file_academic", file1.files[0]);
    if (!file2.disabled && file2.files[0]) fData.append("file_pledge", file2.files[0]);
    if (!file3.disabled && file3.files[0]) fData.append("file_non_objection", file3.files[0]);

    try {
        const response = await fetch(`${API_BASE}/update_request/${requestId}`, {
            method: "POST",
            body: fData,
        });
        if (response.ok) window.location.replace("/Admin/Requests");
    } catch (err) { alert("فشل الاتصال"); }
});


async function acceptDenyRequest(state) {
    try {

        if (txtMsg.value === '')
            alert("enter a note")
        else {
            const response = await fetch(`${API_BASE}/accept_deny/${requestId}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    state: state,
                    note: txtMsg.value
                })
            });

            if (response.ok) {
                location.reload();
            } else {
                const error = await response.json();
                alert(error.detail || "Error occurred");
            }
        }
    } catch (e) {
        console.error("Request failed", e);
    }
}

async function updateStatus() {
    try {

        if (txtMsg.value === '')
            alert("enter a note")

        else {
            const response = await fetch(`${API_BASE}/change_status/${requestId}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    new_status: selStatus.value,
                    note: txtMsg.value
                })
            });

            if (response.ok) {
                location.reload();
            } else {
                const error = await response.json();
                alert(error.detail || "Error occurred");
            }
        }
    } catch (e) {
        console.error("Request failed", e);
    }
}


// --- DELETE ---


const deletePass = document.getElementById('deleteConfirmPass')
const deletePassConfirm = document.getElementById('deleteConfirmCheck')
const passwordModal = document.getElementById('passwordModal')
const confirmDeleteBtn = document.getElementById('confirmDeleteBtn')


function openDeleteModal() {


    deletePass.value = '';
    deletePassConfirm.value = '';
    passwordModal.style.display = 'flex';
}

function closeModal() {
    passwordModal.style.display = 'none';
}

confirmDeleteBtn.onclick = async () => {
    const pass = deletePass.value;
    const conf = deletePassConfirm.value;


    if (!pass || pass !== conf) return alert("Passwords must match and cannot be empty.");

    const response = await fetch(`${API_BASE}/delete_request/${requestId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pass })
    });

    if (response.ok) {
        closeModal();
        window.location.replace("/Admin/Requests");

    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }
};


init();