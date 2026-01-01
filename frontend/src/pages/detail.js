import { searchMultiRoute } from '../lib/api.js';
import { showError, formatDuration } from '../lib/utils.js';
import { renderTimeline } from '../components/Timeline.js';

// Store routes globally for tab switching
let allRoutes = [];
let activeRouteIndex = 0;

document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    const fromStation = params.get("from");
    const toStation = params.get("to");
    const time = params.get("time");

    if (!fromStation || !toStation || !time) {
        showError("出発駅、到着駅、時刻を指定してください。");
        return;
    }

    // Update header
    document.getElementById("route-header").textContent = `${fromStation} → ${toStation}`;
    document.getElementById("route-subheader").textContent = `${time} 以降の電車を検索中...`;

    await executeSearch(fromStation, toStation, time);
});

async function executeSearch(from, to, time) {
    try {
        const data = await searchMultiRoute(from, to, time);

        if (!data.routes || data.routes.length === 0) {
            showError("ルートが見つかりませんでした。");
            return;
        }

        allRoutes = data.routes;
        renderRouteTabs();
        renderRoute(0);
        
        document.getElementById("loading-state").classList.add("hidden");
        document.getElementById("result-state").classList.remove("hidden");
    } catch (e) {
        if (e.message) showError(e.message);
    }
}

function renderRouteTabs() {
    const tabsContainer = document.getElementById("route-tabs");
    tabsContainer.innerHTML = "";
    
    allRoutes.forEach((route, index) => {
        const segments = route.segments || [];
        const lastSeg = segments.length > 0 ? segments[segments.length - 1] : null;
        const arrival = lastSeg?.arrival_time || "?";
        const transfers = route.transfers || 0;
        
        const tab = document.createElement("button");
        tab.className = `flex-shrink-0 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            index === activeRouteIndex 
                ? 'bg-rose-500 text-white' 
                : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600/50'
        }`;
        tab.innerHTML = `
            <span class="block text-lg font-bold">${arrival}</span>
            <span class="block text-xs opacity-75">乗換${transfers}回</span>
        `;
        tab.addEventListener("click", () => {
            activeRouteIndex = index;
            renderRouteTabs();
            renderRoute(index);
        });
        tabsContainer.appendChild(tab);
    });
}

function renderRoute(index) {
    const route = allRoutes[index];
    if (!route) return;
    
    const segments = route.segments || [];
    
    // Get times
    const firstDeparture = segments.length > 0 && segments[0].departure_time 
        ? segments[0].departure_time 
        : "--:--";
    const lastSeg = segments.length > 0 ? segments[segments.length - 1] : null;
    const arrivalTime = lastSeg?.arrival_time || "--:--";
    
    // Update summary
    document.getElementById("first-departure").textContent = firstDeparture;
    document.getElementById("arrival-time").textContent = arrivalTime;
    document.getElementById("transfer-count").textContent = `${route.transfers || 0}回`;
    
    // Update header
    document.getElementById("route-subheader").textContent = `${firstDeparture} 発 → ${arrivalTime} 着`;
    
    // Render delay warnings
    renderDelayWarnings(route.delay_warnings || []);
    
    // Render timeline
    renderTimeline(segments);
}

function renderDelayWarnings(warnings) {
    const container = document.getElementById("delay-warnings");
    if (!container) return;
    
    if (warnings.length === 0) {
        container.classList.add("hidden");
        return;
    }
    
    container.innerHTML = "";
    container.classList.remove("hidden");
    
    warnings.forEach(warning => {
        const el = document.createElement("div");
        el.className = "bg-amber-500/20 border border-amber-500/50 rounded-xl p-4 mb-2 flex items-center gap-3";
        el.innerHTML = `
            <span class="text-2xl">⚠️</span>
            <div>
                <p class="text-amber-200 font-medium">${warning.railway}</p>
                <p class="text-amber-100/70 text-sm">現在 約${warning.delay_minutes}分の遅延が発生しています</p>
            </div>
        `;
        container.appendChild(el);
    });
}
