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
const inputName = document.getElementById('student-name');
const inputBirth = document.getElementById('birth-date');
const inputSpec = document.getElementById('speciality');
const txtReason = document.getElementById('suspension-reason');
const txtMsg = document.getElementById('message');

const file1 = document.getElementById('file-1');
const file2 = document.getElementById('file-2');
const btnSubmit = document.getElementById('btn-submit');

let formData = {}; // Global store for fetch data

async function init() {
    // Default state
    selSubStudy.disabled = selSubJob.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/test`);
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
form.addEventListener('submit', (e) => {
    e.preventDefault();

    // Mapping current form state to payload
    const payload = {
        student_name: inputName.value,
        birth_date: inputBirth.value,
        department: selDept.value,
        speciality: inputSpec.value,
        study: `${selStudy.value}-${selSubStudy.value}`,
        job_status: `${selJobType.value}-${selSubJob.value}`,
        acceptance_year: selAccYear.value,
        suspension_year: selSusYear.value,
        suspension_reason: txtReason.value,
        previous_benefits: selBenefits.value,
        notes: txtMsg.value,
        file_academic: file1.files[0] || null,
        file_pledge: file2.files[0] || null
    };

    try {
        window.location.replace("/User/Requests");
        
    } catch (err) {
        console.error("Submission failed", err);
    }
});

// --- Run ---
init();