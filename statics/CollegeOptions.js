const API_BASE = 'http://192.168.0.113:8000';


function toggleOptions() {
    const list = document.getElementById("OptionsList");
    if (list.style.display === "block") {
        list.style.display = "none";
    } else {
        list.style.display = "block";
    }
}