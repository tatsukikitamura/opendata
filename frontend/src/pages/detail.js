import { searchRouteWithTimes } from '../lib/api.js';
import { showError, formatDuration } from '../lib/utils.js';
import { renderTimeline } from '../components/Timeline.js';

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
        const data = await searchRouteWithTimes(from, to, time);

        if (data.error) {
            showError(data.error);
            return;
        }

        renderResult(data, time);
    } catch (e) {
        if (e.message) showError(e.message);
    }
}

function renderResult(data, requestedTime) {
    document.getElementById("loading-state").classList.add("hidden");
    document.getElementById("error-state").classList.add("hidden");
    document.getElementById("result-state").classList.remove("hidden");

    const segments = data.segments || [];
    
    // Get first departure time
    const firstDeparture = segments.length > 0 && segments[0].departure_time 
        ? segments[0].departure_time 
        : requestedTime;
    
    document.getElementById("first-departure").textContent = firstDeparture;
    
    // Total time
    const totalTime = data.theoretical_time || 0;
    document.getElementById("total-time").textContent = formatDuration(totalTime);
    
    // Transfer count
    const transfers = data.transfers || 0;
    document.getElementById("transfer-count").textContent = `${transfers}回`;

    // Update header
    document.getElementById("route-subheader").textContent = `${firstDeparture} 発`;

    // Build timeline using component
    renderTimeline(segments);
}
