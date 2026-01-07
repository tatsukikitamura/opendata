/**
 * Home page logic
 */
import { formatDuration } from '../lib/utils.js';
import { getStations, getCurrentDelays } from '../lib/api.js';

let allStations = [];

document.addEventListener("DOMContentLoaded", async () => {
    // Set default time to current time
    setCurrentTime();
    
    setupTimeButtons();
    setupSearchForm();
    
    // Render network status immediately
    renderNetworkStatus();

    // Fetch stations and setup autocomplete
    allStations = await getStations();
    setupAutocomplete("from-station");
    setupAutocomplete("to-station");
});

async function renderNetworkStatus() {
    const container = document.getElementById("network-status-container");
    if (!container) return;

    try {
        const delays = await getCurrentDelays();
        
        if (delays.length === 0) {
            container.innerHTML = `
                <div class="bg-emerald-50 border border-emerald-100 rounded-xl p-4 flex items-center gap-3 animate-fade-in">
                    <div class="bg-white p-2 rounded-full shadow-sm">
                        <span class="text-xl">✨</span>
                    </div>
                    <div>
                        <p class="font-bold text-emerald-800 text-sm">平常運行中</p>
                        <p class="text-xs text-emerald-600">現在、主要路線で大きな遅延は発生していません。</p>
                    </div>
                </div>
            `;
        } else {
            // Group by railway name to avoid duplicates
            const uniqueRailways = [...new Set(delays.map(d => d.railway_name))];
            
            // Generate list of names
            const namesList = uniqueRailways.join('、');

            container.innerHTML = `
                <div class="bg-red-50 border border-red-100 rounded-xl p-4 animate-fade-in shadow-sm">
                    <div class="flex items-center gap-3">
                        <div class="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse flex-shrink-0"></div>
                        <div>
                            <p class="font-bold text-red-800 text-sm">
                                <span class="text-base mr-1">${uniqueRailways.length}</span>路線で遅延が発生しています
                            </p>
                            <p class="text-xs text-red-600 mt-0.5 leading-relaxed">
                                ${namesList}
                            </p>
                        </div>
                    </div>
                </div>
            `;
        }
        
        container.classList.remove("hidden");
    } catch (e) {
        console.error("Failed to render network status", e);
    }
}

function setupAutocomplete(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;

    // Ensure parent is relative for absolute positioning of dropdown
    const parent = input.parentElement;
    parent.classList.add("relative");

    // Create dropdown element
    const list = document.createElement("ul");
    list.className = "absolute z-50 w-full mt-1 bg-white border border-slate-200 rounded-xl shadow-xl max-h-60 overflow-y-auto hidden";
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
            // バリデーションタイマーをセット (入力中はエラーを消す)
            clearError(input);
            scheduleValidation(input, val);
            return;
        }

        list.innerHTML = "";
        matches.forEach(station => {
            const li = document.createElement("li");
            li.className = "px-4 py-2 hover:bg-slate-50 cursor-pointer text-slate-700 transition-colors border-b border-slate-100 last:border-0";
            li.textContent = station;
            li.addEventListener("click", () => {
                input.value = station;
                list.classList.add("hidden");
                clearError(input); // 選択したらエラーを消す
            });
            list.appendChild(li);
        });

        list.classList.remove("hidden");
        
        // 入力中もバリデーションをスケジュール
        clearError(input);
        scheduleValidation(input, val);
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
    
    // Blur時にエラーチェック（即時）
    input.addEventListener("blur", () => {
         const val = input.value.trim();
         if (val && !allStations.includes(val)) {
             showError(input, "無効な駅名です");
         }
    });
}

let validationTimers = new Map();

function scheduleValidation(input, value) {
    if (validationTimers.has(input)) {
        clearTimeout(validationTimers.get(input));
    }

    const timer = setTimeout(() => {
        if (value && !allStations.includes(value)) {
            showError(input, "無効な駅名です");
        }
    }, 1000);

    validationTimers.set(input, timer);
}

function showError(input, message) {
    // 既にエラーが表示されているか確認
    const parent = input.parentElement.parentElement; // div.relative > div.relative > input なので
    let errorMsg = parent.querySelector(".station-error-message");
    
    if (!errorMsg) {
        errorMsg = document.createElement("p");
        errorMsg.className = "station-error-message text-red-500 text-xs mt-1 ml-1 font-bold flex items-center gap-1";
        // errorMsg.innerHTML = `<span>⚠️</span> ${message}`; 
        // アイコンはCSSで装飾もできるがシンプルに
        parent.appendChild(errorMsg);
    }
    errorMsg.textContent = "⚠️ " + message;
    
    input.classList.add("border-red-500", "focus:ring-red-200");
    input.classList.remove("focus:ring-slate-400", "border-slate-200");
}

function clearError(input) {
    const parent = input.parentElement.parentElement;
    const errorMsg = parent.querySelector(".station-error-message");
    if (errorMsg) {
        errorMsg.remove();
    }
    
    input.classList.remove("border-red-500", "focus:ring-red-200");
    input.classList.add("border-slate-200", "focus:ring-slate-400");
    
    if (validationTimers.has(input)) {
        clearTimeout(validationTimers.get(input));
        validationTimers.delete(input);
    }
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

        // Navigate to results page
        window.location.href = `./detail.html?${params.toString()}`;
    });
}
