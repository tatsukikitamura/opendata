/**
 * Home page logic
 */
import { formatDuration } from '../lib/utils.js';

document.addEventListener("DOMContentLoaded", async () => {
    // Set default time to current time
    setCurrentTime();
    
    setupTimeButtons();
    setupSearchForm();

    // Setup autocomplete
    try {
        const stations = await fetchStations();
        setupAutocomplete("from-station", stations);
        setupAutocomplete("to-station", stations);
    } catch (e) {
        console.error("Failed to setup autocomplete:", e);
    }
});

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

        // Navigate to results page
        window.location.href = `/detail.html?${params.toString()}`;
    });
}

async function fetchStations() {
    try {
        const res = await fetch("http://localhost:8000/stations");
        if (!res.ok) throw new Error("API Error");
        return await res.json();
    } catch (e) {
        console.error(e);
        return [];
    }
}

function setupAutocomplete(inputId, stations) {
    const input = document.getElementById(inputId);
    if (!input) return;

    // Create wrapper for positioning if not exists
    let wrapper = input.parentElement;
    if (!wrapper.classList.contains("relative")) {
        wrapper.classList.add("relative");
    }

    // Create dropdown element
    const dropdown = document.createElement("div");
    dropdown.className = "autocomplete-dropdown hidden";
    wrapper.appendChild(dropdown);

    // Event listeners
    input.addEventListener("input", () => {
        const val = input.value.trim();
        if (!val) {
            dropdown.innerHTML = "";
            dropdown.classList.add("hidden");
            return;
        }

        // Filter stations
        const matches = stations.filter(s => s.includes(val));
        
        if (matches.length > 0) {
            renderDropdown(dropdown, matches, input);
            dropdown.classList.remove("hidden");
        } else {
            dropdown.classList.add("hidden");
        }
    });

    // Hide when clicking outside
    document.addEventListener("click", (e) => {
        if (!wrapper.contains(e.target)) {
            dropdown.classList.add("hidden");
        }
    });
    
    // Focus support
    input.addEventListener("focus", () => {
         const val = input.value.trim();
         if (val) {
             input.dispatchEvent(new Event('input'));
         }
    });
}

function renderDropdown(dropdown, matches, input) {
    dropdown.innerHTML = "";
    matches.forEach(station => {
        const item = document.createElement("div");
        item.className = "autocomplete-item";
        item.textContent = station;
        item.addEventListener("click", () => {
            input.value = station;
            dropdown.innerHTML = "";
            dropdown.classList.add("hidden");
        });
        dropdown.appendChild(item);
    });
}
