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
    
    // Back to list button handler
    document.getElementById("back-to-list").addEventListener("click", () => {
        showListView();
    });
});

async function executeSearch(from, to, time) {
    try {
        const data = await searchMultiRoute(from, to, time);

        if (!data.routes || data.routes.length === 0) {
            showError("ルートが見つかりませんでした。");
            return;
        }

        allRoutes = data.routes;
        
        // Initial render: show list
        renderRouteList();
        
        document.getElementById("loading-state").classList.add("hidden");
        document.getElementById("result-state").classList.remove("hidden");
        showListView();
        
    } catch (e) {
        if (e.message) showError(e.message);
    }
}

function showListView() {
    document.getElementById("route-list-view").classList.remove("hidden");
    document.getElementById("route-detail-view").classList.add("hidden");
    document.getElementById("route-header").textContent = "検索結果";
}

function showDetailView(index) {
    document.getElementById("route-list-view").classList.add("hidden");
    document.getElementById("route-detail-view").classList.remove("hidden");
    renderRouteDetail(index);
}

function renderRouteList() {
    const container = document.getElementById("route-list-container");
    container.innerHTML = "";
    
    allRoutes.forEach((route, index) => {
        const segments = route.segments || [];
        const firstDeparture = segments.length > 0 ? segments[0].departure_time : "--:--";
        const lastSeg = segments.length > 0 ? segments[segments.length - 1] : null;
        const arrival = lastSeg?.arrival_time || "--:--";
        const transfers = route.transfers || 0;
        const risk = route.risk || { level: 'LOW' };
        const crowd = route.crowd || { level: 'LOW', score: 0 };
        
        const card = document.createElement("div");
        
        // Card styling based on Risk
        let bgClass = "bg-slate-800/60 hover:bg-slate-700/60 border-slate-700";
        if (risk.level === 'HIGH') {
            bgClass = "bg-red-900/20 hover:bg-red-900/30 border-red-500/50";
        } else if (risk.level === 'MEDIUM') {
            bgClass = "bg-amber-900/20 hover:bg-amber-900/30 border-amber-500/50";
        }
        
        card.className = `p-4 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${bgClass}`;
        
        let riskLabel = "";
        if (risk.level === 'HIGH') {
            riskLabel = `<span class="px-2 py-1 rounded text-xs font-bold bg-red-500/20 text-red-200 border border-red-500/50">遅延リスク高</span>`;
        } else if (risk.level === 'MEDIUM') {
            riskLabel = `<span class="px-2 py-1 rounded text-xs font-bold bg-amber-500/20 text-amber-200 border border-amber-500/50">遅延注意</span>`;
        } else {
            riskLabel = `<span class="px-2 py-1 rounded text-xs font-bold bg-emerald-500/20 text-emerald-200 border border-emerald-500/50">平常運行</span>`;
        }
        
        // Crowd Label
        let crowdIcon = "👤";
        if (crowd.level === 'HIGH') crowdIcon = "👥👥 混雑";
        else if (crowd.level === 'MEDIUM') crowdIcon = "👥 普通";
        else crowdIcon = "👤 空き";
        
        card.innerHTML = `
            <div>
                <div class="flex items-center gap-3 mb-1">
                    <span class="text-2xl font-bold text-white">${arrival} 着</span>
                    <span class="text-sm text-slate-400">(${firstDeparture} 発)</span>
                </div>
                <div class="flex items-center gap-4 text-sm text-slate-400 mt-2">
                    <span>乗換 ${transfers}回</span>
                    <span class="text-xs border border-slate-600 px-2 py-0.5 rounded-full">${crowdIcon}</span>
                </div>
            </div>
            <div class="text-right">
                ${riskLabel}
                <div class="text-xs text-slate-500 mt-2">詳細を見る &gt;</div>
            </div>
        `;
        
        card.addEventListener("click", () => {
            showDetailView(index);
        });
        
        container.appendChild(card);
    });
}

function renderRouteDetail(index) {
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
    document.getElementById("route-header").textContent = `${firstDeparture} 発 → ${arrivalTime} 着`;
    
    // Render delay warnings including Risk
    renderDelayWarnings(route);
    
    // Render timeline
    renderTimeline(segments);
}

function renderDelayWarnings(route) {
    const container = document.getElementById("delay-warnings");
    if (!container) return;
    
    container.innerHTML = "";
    
    const realTimeWarnings = route.delay_warnings || [];
    const risk = route.risk || { level: 'LOW', reasons: [] };
    const crowd = route.crowd || { level: 'UNKNOWN', score: 0, details: [] };
    const venueWarnings = route.venue_warnings || { transfer_warnings: [], passing_info: [] };
    
    let hasContent = false;

    // 0. Venue Transfer Warnings (⚠️ 目立つ)
    if (venueWarnings.transfer_warnings.length > 0) {
        hasContent = true;
        const el = document.createElement("div");
        el.className = "bg-orange-500/20 border border-orange-500/50 rounded-xl p-4 mb-2";
        el.innerHTML = `
            <div class="flex items-center gap-2 mb-3">
                <span class="text-2xl">🎪</span>
                <span class="font-bold text-orange-200">イベント会場の最寄り駅を通ります</span>
            </div>
            <div class="space-y-2">
                ${venueWarnings.transfer_warnings.map(w => `
                    <div class="bg-black/20 rounded-lg p-3">
                        <p class="font-medium text-orange-100">📍 ${w.station}駅 → ${w.venue}</p>
                        <p class="text-xs text-slate-400 mt-1">収容人数: ${w.capacity.toLocaleString()}人 / ${w.note}</p>
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(el);
    }

    // 0.5 Venue Passing Info (ℹ️ 控えめ)
    if (venueWarnings.passing_info.length > 0) {
        hasContent = true;
        const el = document.createElement("div");
        el.className = "bg-slate-700/30 border border-slate-600/50 rounded-xl p-3 mb-2";
        el.innerHTML = `
            <div class="flex items-center gap-2">
                <span class="text-lg">ℹ️</span>
                <span class="text-sm text-slate-300">通過駅周辺の会場: ${venueWarnings.passing_info.map(p => `${p.station}(${p.venues.join(', ')})`).join(' / ')}</span>
            </div>
        `;
        container.appendChild(el);
    }

    // 1. Crowd Info
    if (crowd.level !== 'UNKNOWN') {
        hasContent = true;
        const crowdEl = document.createElement("div");
        crowdEl.className = "bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 mb-2";
        crowdEl.innerHTML = `
            <div class="flex items-center gap-2 mb-2">
                <span class="text-xl">📊</span>
                <span class="font-bold text-blue-200">平均駅規模: ${crowd.score.toLocaleString()}人/日 (${crowd.level === 'HIGH' ? '大都市圏' : crowd.level === 'MEDIUM' ? '中規模' : '郊外'})</span>
            </div>
             <div class="text-xs text-slate-400 pl-1">
                経由駅の規模: ${crowd.details.join(', ')}
            </div>
        `;
        container.appendChild(crowdEl);
    }

    // 2. Predictive Risk
    if (risk.reasons.length > 0) {
        hasContent = true;
        
        let colorClass = "bg-emerald-500/10 border-emerald-500/50 text-emerald-100";
        let icon = "✅";
        let levelText = "低い";
        
        if (risk.level === 'HIGH') {
            colorClass = "bg-red-500/10 border-red-500/50 text-red-100";
            icon = "⚠️";
            levelText = "高い";
        } else if (risk.level === 'MEDIUM') {
            colorClass = "bg-amber-500/10 border-amber-500/50 text-amber-100";
            icon = "⚠️";
            levelText = "中程度";
        }
            
        const el = document.createElement("div");
        el.className = `${colorClass} border rounded-xl p-4 mb-2`;
        el.innerHTML = `
            <div class="flex items-center gap-2 mb-3">
                <span class="text-2xl">${icon}</span>
                <span class="font-bold text-lg">遅延リスク: ${levelText}</span>
            </div>
            <div class="bg-black/20 rounded-lg p-3">
                <p class="text-xs opacity-70 mb-2">過去の遅延実績データ:</p>
                <ul class="list-disc list-inside text-sm space-y-1">
                    ${risk.reasons.map(r => `<li>${r}</li>`).join('')}
                </ul>
            </div>
        `;
        container.appendChild(el);
    }

    // 3. Real-time Warnings
    realTimeWarnings.forEach(warning => {
        hasContent = true;
        const el = document.createElement("div");
        el.className = "bg-amber-500/20 border border-amber-500/50 rounded-xl p-4 mb-2 flex items-center gap-3";
        el.innerHTML = `
            <span class="text-2xl">⚡️</span>
            <div>
                <p class="text-amber-200 font-medium">${warning.railway}</p>
                <p class="text-amber-100/70 text-sm">現在 約${warning.delay_minutes}分の遅延が発生しています</p>
            </div>
        `;
        container.appendChild(el);
    });
    
    if (hasContent) {
        container.classList.remove("hidden");
    } else {
        container.classList.add("hidden");
    }
}
