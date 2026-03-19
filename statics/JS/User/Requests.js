// Configuration
const API_BASE = 'http://192.168.0.113:8000';
let currentStatus = 'All';

// Elements
const ticketContainer = document.getElementById('ticketContainer');
const statusButtons = document.querySelectorAll('.status-btn');


const init =async () => {
    try {

        // 4. Initial Data Load
        await fetchData();

    } catch (err) {
        console.error("Initialization failed:", err);
    }
}

async function fetchData() {
    ticketContainer.innerHTML = '<p style="padding: 20px;">Fetching records...</p>';
    const url = new URL(API_BASE + '/get_requests');
    const params = new URLSearchParams();

    if (currentStatus !== 'All') params.append('status', currentStatus);

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

const genderTranslations = {
    "male": "ذكر",
    "female": "انثى",
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
                    <h4 class="student-speciality">الجنس: ${genderTranslations[ticket.gender]||ticket.gender}</h4>
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
                <button 
                    class="more-btn" 
                    onclick="window.location.href='/User/reivew_request/${ticket.id}'">                       
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


function downloadExcel() {

    const params = new URLSearchParams();

    if (currentStatus !== 'All') params.append('status', currentStatus);

    window.location.href = `/download_excel?${params.toString()}`;
}

init();