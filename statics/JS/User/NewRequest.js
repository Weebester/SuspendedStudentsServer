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

// Text Inputs
const inputName = document.getElementById('student-name');
const inputBirth = document.getElementById('birth-date');
const inputSpec = document.getElementById('speciality');
const txtReason = document.getElementById('suspension-reason');
const txtMsg = document.getElementById('message');

// Files (Corrected ID duplicate from file-1/file-1 to file-1/file-2)
const file1 = document.getElementById('file-1');
const file2 = document.getElementById('file-2');

// Buttons
const btnSubmit = document.getElementById('btn-submit');

// --- Initialization ---
function init() {
    console.log("Initializing Arabic Student Form components...");
    // Your logic for years/departments goes here
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
        study_type: selStudy.value,
        study_phase: selSubStudy.value,
        job_status: selJobType.value,
        is_university_service: selSubJob.value,
        acceptance_year: selAccYear.value,
        suspension_year: selSusYear.value,
        suspension_reason: txtReason.value,
        previous_benefits: selBenefits.value,
        notes: txtMsg.value,
        file_academic: file1.files[0] || null,
        file_pledge: file2.files[0] || null
    };

    console.log("Payload Prepared:", payload);
    // Add your Fetch/API logic here
});

// --- Run ---
init();