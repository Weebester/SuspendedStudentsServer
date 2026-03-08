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
        const [years, colleges] = await Promise.all([
            fetch(`${API_BASE}/get_years_list`).then(res => res.json()),
            fetch(`${API_BASE}/get_colleges_list`).then(res => res.json())
        ]);

        // 2. Populate Years (Remove "Any", Set Latest)
        if (years.length > 0) {
            yearInput.innerHTML = '';
            latestYear = Math.max(...years);
            years.sort((a, b) => b - a).forEach(y => {
                yearInput.add(new Option(`${y}-${y + 1}`, y));
            });
            yearInput.value = latestYear;
        }

        // 3. Populate Colleges
        colleges.forEach(c => {
            collegeInput.add(new Option(c, c));
        });

        // 4. Initial Data Load
        await fetchData();

    } catch (err) {
        console.error("Initialization failed:", err);
    }
})();

async function fetchData() {
    ticketContainer.innerHTML = '<p style="padding: 20px;">Fetching records...</p>';
    const url = new URL(API_BASE + '/requestsA');
    const params = new URLSearchParams();

    if (currentStatus !== 'All') params.append('status', currentStatus);

    const yearVal = yearInput.value;
    const collegeVal = collegeInput.value;

    // Skip year if matches latestYear
    if (yearVal && parseInt(yearVal) !== latestYear) {
        params.append('year', yearVal);
    }

    // Skip college if "Any" (empty)
    if (collegeVal) {
        params.append('college', collegeVal);
    }

    url.search = params.toString();

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Status: ${response.status}`);
        const apiData = await response.json();
        renderTickets(apiData);
    } catch (err) {
        ticketContainer.innerHTML = `<p style="color: red; padding: 20px;">Error: ${err.message}</p>`;
    }
}

function renderTickets(data) {
    if (!data || data.length === 0) {
        ticketContainer.innerHTML = '<p style="padding: 20px;">No results found.</p>';
        return;
    }

    ticketContainer.innerHTML = data.map(ticket => `
            <div class="ticket-card">
                <div class="card-header">
                    <span class="ticket-id">ID: ${ticket.id}</span>
                    <span class="status-badge status-${ticket.RequestStatus}">${ticket.RequestStatus}</span>
                </div>
                <div class="card-body">
                    <h3 class="student-name">${ticket.StudentName}</h3>
                    <h4 class="student-speciality">Speciality: ${ticket.Speciality}</h4>
                    <div class="details-grid">
                        <div class="detail-item">
                            <p>College</p>
                            <p>${ticket.college}</p>
                        </div>
                        <div class="detail-item">
                            <p>Year</p>
                            <p>${ticket.RequestYear}-${ticket.RequestYear + 1}</p>
                        </div>
                    </div>
                </div>
                <button class="more-btn" onclick="window.location.href='/details/${ticket.id}'">
                    View Full Details →
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

// Event Listeners for Dropdown Changes
yearInput.addEventListener('change', fetchData);
collegeInput.addEventListener('change', fetchData);