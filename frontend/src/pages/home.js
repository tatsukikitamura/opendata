/**
 * Home page logic
 */
import { formatDuration } from '../lib/utils.js';
import { getStations } from '../lib/api.js';

let allStations = [];

document.addEventListener("DOMContentLoaded", async () => {
    // Set default time to current time
    setCurrentTime();
    
    setupTimeButtons();
    setupSearchForm();

    // Fetch stations and setup autocomplete
    allStations = await getStations();
    setupAutocomplete("from-station");
    setupAutocomplete("to-station");
});

function setupAutocomplete(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;

    // Ensure parent is relative for absolute positioning of dropdown
    const parent = input.parentElement;
    parent.classList.add("relative");

    // Create dropdown element
    const list = document.createElement("ul");
    list.className = "absolute z-50 w-full mt-1 bg-slate-800 border border-slate-700 rounded-xl shadow-xl max-h-60 overflow-y-auto hidden";
    parent.appendChild(list);

    // Filter and show list on input
    input.addEventListener("input", () => {
        const val = input.value.trim();
        if (!val) {
            list.classList.add("hidden");
            return;
        }

        const matches = allStations.filter(s => s.includes(val));
        
        // If exact match is the only one, maybe hide? But user might want to confirm. 
        // Showing it is fine.
        
        if (matches.length === 0) {
            list.classList.add("hidden");
            return;
        }

        list.innerHTML = "";
        matches.forEach(station => {
            const li = document.createElement("li");
            li.className = "px-4 py-2 hover:bg-slate-700 cursor-pointer text-slate-200 transition-colors";
            li.textContent = station;
            li.addEventListener("click", () => {
                input.value = station;
                list.classList.add("hidden");
            });
            list.appendChild(li);
        });

        list.classList.remove("hidden");
    });

    // Hide on click outside
    document.addEventListener("click", (e) => {
        if (!parent.contains(e.target)) {
            list.classList.add("hidden");
        }
    });

    // Show list on focus if value exists?
    input.addEventListener("focus", () => {
         // Trigger input event logic if value exists
         if (input.value.trim()) {
             input.dispatchEvent(new Event('input'));
         }
    });
}


function setCurrentTime() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const timeInput = document.getElementById("departure-time");
    if (timeInput) {
        timeInput.value = `${hours}:${minutes}`;
    }
}

function setTime(time) {
    const timeInput = document.getElementById("departure-time");
    if (timeInput) {
        timeInput.value = time;
    }
}

function setupTimeButtons() {
    // Current time button
    const currentBtn = document.getElementById("btn-current-time");
    if (currentBtn) {
        currentBtn.addEventListener("click", setCurrentTime);
    }

    // Preset time buttons (need to add IDs or select by class/attribute in HTML)
    // For now, let's assume we update HTML to use data-time attribute
    const timeButtons = document.querySelectorAll("[data-time]");
    timeButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            setTime(btn.dataset.time);
        });
    });
}

function setupSearchForm() {
    const form = document.getElementById("search-form");
    if (!form) return;

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        // Get values
        const fromStation = document.getElementById("from-station").value;
        const toStation = document.getElementById("to-station").value;
        const time = document.getElementById("departure-time").value;

        if (!fromStation || !toStation || !time) {
            alert("全ての項目を入力してください");
            return;
        }

        // Build URL params
        const params = new URLSearchParams();
        params.append("from", fromStation);
        params.append("to", toStation);
        params.append("time", time);
        
        // Add transfer buffer if set
        const transferBuffer = document.getElementById("transfer-buffer")?.value || "0";
        if (transferBuffer !== "0") {
            params.append("transfer_buffer", transferBuffer);
        }

        // Navigate to results page
        window.location.href = `/detail.html?${params.toString()}`;
    });
}
