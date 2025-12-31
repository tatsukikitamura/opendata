/**
 * Home page logic
 */
import { formatDuration } from '../lib/utils.js';

document.addEventListener("DOMContentLoaded", () => {
    // Set default time to current time
    setCurrentTime();
    
    setupTimeButtons();
    setupSearchForm();
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
