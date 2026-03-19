// --- Element Constants ---
const API_BASE = 'http://192.168.0.113:8000';
// --- Element Constants ---
const form = document.getElementById('student-form');
const collegeLabel = document.getElementById('college-label');

// Selectors
const selDept = document.getElementById('department');
const selStudy = document.getElementById('study-type');
const selSubStudy = document.getElementById('sub-study');
const selJobType = document.getElementById('job-type');
const selSubJob = document.getElementById('sub-job');
const selAccYear = document.getElementById('acceptance-year');
const selSusYear = document.getElementById('suspension-year');
const selBenefits = document.getElementById('benefits');
const selGender = document.getElementById('gender');
const inputName = document.getElementById('student-name');
const inputBirth = document.getElementById('birth-date');
const inputSpec = document.getElementById('speciality');
const txtReason = document.getElementById('suspension-reason');
const txtMsg = document.getElementById('message');

const file1 = document.getElementById('file-1');
const file2 = document.getElementById('file-2');
const file3 = document.getElementById('file-3');
const btnSubmit = document.getElementById('btn-submit');

let formData = {}; 

async function init() {
    // Default state
    selSubStudy.disabled = selSubJob.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/feed_form`);
        formData = await res.json();

        // Populate Statics
        formData.departments.forEach(d => selDept.add(new Option(d, d)));
        formData.years.forEach(y => {
            selAccYear.add(new Option(y, y));
            selSusYear.add(new Option(y, y));
        });

        // Populate Main Selectors
        Object.keys(formData.study).forEach(s => selStudy.add(new Option(s, s)));
        Object.keys(formData.job).forEach(j => selJobType.add(new Option(j, j)));

        // Attach Listeners
        selStudy.onchange = () => populateSubStudy();
        selJobType.onchange = () => populateSubJob();

    } catch (e) { console.error("Init failed", e); }
}

function populateSubStudy() {
    const opts = formData.study[selStudy.value] || [];
    selSubStudy.innerHTML = '<option value="">-</option>';
    selSubStudy.disabled = !opts.length;
    opts.forEach(o => selSubStudy.add(new Option(o, o)));
}

function populateSubJob() {
    const opts = formData.job[selJobType.value] || [];
    selSubJob.innerHTML = '<option value="">-</option>';
    selSubJob.disabled = !opts.length;
    opts.forEach(o => selSubJob.add(new Option(o, o)));
}

// --- Submit Logic ---
form.addEventListener('submit', async (e) => {
    e.preventDefault();


    if (!form.reportValidity()) return;

    const formData = new FormData();
    formData.append("student_name", inputName.value);
    formData.append("birth_date", inputBirth.value);
    formData.append("department", selDept.value);
    formData.append("speciality", inputSpec.value);
    formData.append("study", `${selStudy.value}-${selSubStudy.value}`);
    formData.append("job_status", `${selJobType.value}-${selSubJob.value}`);
    formData.append("acception_year", selAccYear.value);
    formData.append("suspension_year", selSusYear.value);
    formData.append("suspension_reason", txtReason.value);
    formData.append("benefactor", selBenefits.value);
    formData.append("gender", selGender.value);
    formData.append("notes", txtMsg.value);
    
    // Append the files
    if (file1.files[0]) formData.append("file_academic", file1.files[0]);
    if (file2.files[0]) formData.append("file_pledge", file2.files[0]);
    if (file3.files[0]) formData.append("file_non_objection", file3.files[0]);

    try {

        const response = await fetch(`${API_BASE}/submit_request`, {
            method: "POST",
            body: formData, 
        });

        if (response.ok) {

            window.location.replace("/User/Requests");
        } else {
            const err = await response.json();
            alert("حدث خطأ: " + (err.detail || "Error"));
        }
        
    } catch (err) {
        console.error("Submission failed", err);
        alert("فشل الاتصال بالسيرفر");
    }
});

// --- Run ---
init();