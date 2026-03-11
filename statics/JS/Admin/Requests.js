// Configuration
const API_BASE = 'http://192.168.0.113:8000';
let currentStatus = 'All';
let latestYear = null;

// Elements
const ticketContainer = document.getElementById('ticketContainer');
const yearInput = document.getElementById('yearInput');
const collegeInput = document.getElementById('collegeInput');
const statusButtons = document.querySelectorAll('.status-btn');

// Procedural execution wrapper
(async () => {
    try {
        // 1. Fetch Dropdown Data
        const response = await fetch(`${API_BASE}/get_years_admin`);
        const years = await response.json();

        years.forEach(y => {
            const label = `${y.start_year}-${y.start_year + 1}`;
            const option = new Option(label, y.start_year);
            yearInput.add(option);
        });

        const response2 = await fetch(`${API_BASE}/get_colleges_admin`);
        const rawColleges = await response2.json();
        const colleges = rawColleges.filter(c => c.id > 1);
        colleges.forEach(c => {
            collegeInput.add(new Option(c.college, c.id));
        });

        // 4. Initial Data Load
        await fetchData();

    } catch (err) {
        console.error("Initialization failed:", err);
    }
})();

async function fetchData() {
    ticketContainer.innerHTML = '<p style="padding: 20px;">Fetching records...</p>';
    const url = new URL(API_BASE + '/get_requests');
    const params = new URLSearchParams();

    if (currentStatus !== 'All') params.append('status', currentStatus);

    const yearVal = yearInput.value;
    const collegeVal = collegeInput.value;

    // Skip year if matches latestYear
    if (yearVal) {
        params.append('year', yearVal);
    }

    // Skip college if "Any" (empty)
    if (collegeVal) {
        params.append('college', collegeVal);
    }

    url.search = params.toString();


    const response = await fetch(url);
    if (response.ok) {
        const apiData = await response.json();
        renderTickets(apiData);
    } else if (response.status === 401) {
        window.location.href = `${API_BASE}/`
    } else {

        const errorData = await response.json();

        const errorMessage = errorData.detail || "Failed";

        alert("Error: " + errorMessage);
    }

}


const statusTranslations = {
    "Pending": "قيد الانتظار",
    "Accepted": "مقبول",
    "Denied": "مرفوض"
};

function renderTickets(data) {
    /*
    if (!data || data.length === 0) {
        ticketContainer.innerHTML = '<p style="padding: 20px;">No results found.</p>';
        return;
    }*/

    ticketContainer.innerHTML = data.map(ticket => `
            <div class="ticket-card">
                <div class="card-header">
                <span class="status-badge status-${ticket.request_status}">
                    ${statusTranslations[ticket.request_status] || ticket.request_status}
                    </span>
                    <span class="ticket-id">ID: ${ticket.id}</span>    
                </div>
                <div class="card-body">
                    <h3 class="student-name">${ticket.student_name}</h3>
                    <h4 class="student-speciality">التخصص: ${ticket.speciality}</h4>
                    <h4 class="student-speciality">موقف الطلب:${ticket.status}</h4>
                    <div class="details-grid">
                        <div class="detail-item">
                            <p>الكلية</p>
                            <p>${ticket.college}</p>
                        </div>
                        <div class="detail-item">
                            <p>العام الدراسي للطلب</p>
                            <p>${ticket.request_year}-${ticket.request_year + 1}</p>
                        </div>
                    </div>
                </div>
                <button class="more-btn" onclick="window.location.href='/details/${ticket.id}'">
                    عرض التفاصيل الشاملة
                </button>
            </div>
        `).join('');
}

// Event Listeners for Status Buttons
statusButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        statusButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentStatus = btn.getAttribute('data-status');
        fetchData();
    });
});

function toggleOptions() {
    const list = document.getElementById("OptionsList");
    if (list.style.display === "block") {
        list.style.display = "none";
    } else {
        list.style.display = "block";
    }
}

function downloadExcel() {
    const year = document.getElementById('yearInput').value;
    const college = document.getElementById('collegeInput').value;

    const params = new URLSearchParams();

    // Only add if the value is not empty
    if (year) params.append('year', year);
    if (college) params.append('college', college);
    if (currentStatus !== 'All') params.append('status', currentStatus);

    // Redirect to the URL with only the active params
    window.location.href = `/download_excel?${params.toString()}`;
}

yearInput.addEventListener('change', fetchData);
collegeInput.addEventListener('change', fetchData);