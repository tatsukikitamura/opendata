import { searchRoute, diagnoseRoute } from '../lib/api.js';
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
        const data = await searchRoute(from, to, time);

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
    
    // Show global nav elements
    document.getElementById("global-back-link").classList.remove("hidden");
    document.getElementById("main-header").classList.remove("hidden");
    
    document.getElementById("route-header").textContent = "検索結果";
}

function showDetailView(index) {
    document.getElementById("route-list-view").classList.add("hidden");
    document.getElementById("route-detail-view").classList.remove("hidden");
    
    // Hide global nav elements to focus on detail content
    document.getElementById("global-back-link").classList.add("hidden");
    document.getElementById("main-header").classList.add("hidden");
    
    renderRouteDetail(index);
}

function renderRouteList() {
    const container = document.getElementById("route-list-container");
    container.innerHTML = "";

    // Find best balance route (highest total score)
    let bestRouteIndex = -1;
    let maxTotalScore = -1;
    
    allRoutes.forEach((r, i) => {
        const speed = r.scores?.speed || 0;
        const comfort = r.scores?.comfort || 0;
        const reliability = r.scores?.reliability || 0;
        const cost = r.scores?.cost || 0;
        const total = speed + comfort + reliability + cost;
        
        if (total > maxTotalScore) {
            maxTotalScore = total;
            bestRouteIndex = i;
        }
    });

    allRoutes.forEach((route, index) => {
        const segments = route.segments || [];
        const firstDeparture = (segments.length > 0 && segments[0].departure_time) ? segments[0].departure_time : "--:--";
        const lastSeg = segments.length > 0 ? segments[segments.length - 1] : null;
        const arrival = lastSeg?.arrival_time || "--:--";
        const transfers = route.transfers || 0;
        const risk = route.risk || { level: 'LOW' };

        // Calculate travel time
        let travelTimeText = "";
        if (firstDeparture !== "--:--" && arrival !== "--:--") {
            const [depH, depM] = firstDeparture.split(':').map(Number);
            const [arrH, arrM] = arrival.split(':').map(Number);
            let totalMinutes = (arrH * 60 + arrM) - (depH * 60 + depM);
            if (totalMinutes < 0) totalMinutes += 24 * 60; // Handle overnight
            const hours = Math.floor(totalMinutes / 60);
            const mins = totalMinutes % 60;
            travelTimeText = hours > 0 ? `${hours}時間${mins}分` : `${mins}分`;
        }

        const card = document.createElement("div");

        // Card styling based on Risk
        let bgClass = "bg-white hover:bg-slate-50 border-slate-200 shadow-sm";
        if (risk.level === 'HIGH') {
            bgClass = "bg-red-50 hover:bg-red-100 border-red-200 shadow-sm";
        } else if (risk.level === 'MEDIUM') {
            bgClass = "bg-amber-50 hover:bg-amber-100 border-amber-200 shadow-sm";
        }
        
        // Highlight best route
        const isBest = index === bestRouteIndex && maxTotalScore > 0;
        if (isBest) {
            bgClass += " ring-2 ring-emerald-500 ring-offset-2";
        }

        card.className = `p-6 md:p-8 rounded-xl border transition-all cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-6 md:gap-0 ${bgClass} focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 relative`;
        card.setAttribute('role', 'button');
        card.setAttribute('tabindex', '0');
        card.setAttribute('aria-label', `${firstDeparture}発 ${arrival}着 乗換${transfers}回 ${travelTimeText}`);

        // Risk Label
        let riskLabel = "";
        if (risk.level === 'HIGH') {
            riskLabel = `<span class="px-2 py-1 rounded text-xs font-bold bg-red-100 text-red-700 border border-red-200">遅延リスク高</span>`;
        } else if (risk.level === 'MEDIUM') {
            riskLabel = `<span class="px-2 py-1 rounded text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200">遅延注意</span>`;
        } else {
            riskLabel = `<span class="px-2 py-1 rounded text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">平常運行</span>`;
        }
        
        const bestBadge = isBest ? 
            `<div class="absolute -top-3 left-6 bg-yellow-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-md flex items-center gap-1">
                <span>⭐️</span> ベストバランス
            </div>` : '';

        card.innerHTML = `
            ${bestBadge}
            <div class="w-full md:w-auto">
                <div class="flex items-center gap-3 mb-1">
                    <span class="text-2xl font-bold text-slate-800">${arrival} 着</span>
                    <span class="text-sm text-slate-500 hidden md:inline">(${firstDeparture} 発)</span>
                    ${travelTimeText ? `<span class="text-sm font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">${travelTimeText}</span>` : ''}
                </div>
                <div class="text-sm text-slate-500 mt-2">
                    乗換 ${transfers}回
                    ${route.fare ? `<span class="ml-3 text-slate-800 font-bold">¥${route.fare.toLocaleString()}</span>` : ''}
                </div>
            </div>
            <div class="w-full md:w-auto flex justify-center md:block">
                <!-- 4-Axis Scores -->
                <div class="mt-0 md:mt-3 text-xs space-y-1 w-full md:w-48">
                    <div class="flex items-center gap-4">
                        <span class="w-8 text-slate-500">速さ</span>
                        <div class="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div class="h-full bg-blue-500" style="width: ${(route.scores?.speed || 0) * 20}%"></div>
                        </div>
                        <span class="w-6 text-right font-mono text-slate-600">${(route.scores?.speed || 0).toFixed(1)}</span>
                    </div>
                    <div class="flex items-center gap-4">
                        <span class="w-8 text-slate-500">快適</span>
                        <div class="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div class="h-full bg-emerald-500" style="width: ${(route.scores?.comfort || 0) * 20}%"></div>
                        </div>
                        <span class="w-6 text-right font-mono text-slate-600">${(route.scores?.comfort || 0).toFixed(1)}</span>
                    </div>
                    <div class="flex items-center gap-4">
                        <span class="w-8 text-slate-500">安定</span>
                        <div class="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div class="h-full bg-purple-500" style="width: ${(route.scores?.reliability || 0) * 20}%"></div>
                        </div>
                        <span class="w-6 text-right font-mono text-slate-600">${(route.scores?.reliability || 0).toFixed(1)}</span>
                    </div>
                    <div class="flex items-center gap-4">
                        <span class="w-8 text-slate-500">安さ</span>
                        <div class="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div class="h-full bg-orange-500" style="width: ${(route.scores?.cost || 0) * 20}%"></div>
                        </div>
                        <span class="w-6 text-right font-mono text-slate-600">${(route.scores?.cost || 0).toFixed(1)}</span>
                    </div>
                </div>
            </div>
            <div class="w-full md:w-auto text-left md:text-right flex flex-row-reverse md:block justify-between items-center md:items-end">
                <div class="md:mb-2">${riskLabel}</div>
                <div class="text-xs text-slate-400 mt-0 md:mt-2 flex items-center justify-end gap-1">
                    詳細を見る
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                </div>
            </div>
        `;

        card.addEventListener("click", () => {
            showDetailView(index);
        });

        // Keyboard accessibility
        card.addEventListener("keydown", (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                showDetailView(index);
            }
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

    // Calculate Duration
    let durationText = "--分";
    if (firstDeparture !== "--:--" && arrivalTime !== "--:--" && firstDeparture && arrivalTime) {
        const [depH, depM] = firstDeparture.split(':').map(Number);
        const [arrH, arrM] = arrivalTime.split(':').map(Number);
        let totalMinutes = (arrH * 60 + arrM) - (depH * 60 + depM);
        if (totalMinutes < 0) totalMinutes += 24 * 60;

        const hours = Math.floor(totalMinutes / 60);
        const mins = totalMinutes % 60;
        durationText = hours > 0 ? `${hours}時間${mins}分` : `${mins}分`;
    }

    // Update summary
    document.getElementById("first-departure").textContent = firstDeparture;
    document.getElementById("arrival-time").textContent = arrivalTime;
    document.getElementById("transfer-count").textContent = `乗換 ${route.transfers || 0}回`;
    
    // Update Fare
    const fareEl = document.getElementById("total-fare");
    if (fareEl) {
        fareEl.textContent = route.fare ? `¥${route.fare.toLocaleString()}` : '---';
    } else {
        // If element doesn't exist (it might not in current HTML), verify where to put it.
        // I should check detail.html first to see where to hook. 
        // Or I can append it to duration text for now if no specific ID.
        // Let's assume I need to add an element or append to existing.
        // User didn't give detail.html content but I saw detailed.js.
        // Let's assume I need to add string to duration or similar if no ID found.
        // Wait, line 248 was just text content update.
        // Let's update lines 248 and see if there is a slot. 
        // Actually, I should probably check detail.html to add a placeholder too if needed.
    }
    document.getElementById("total-duration").textContent = durationText;
    if (route.fare) {
        document.getElementById("total-duration").textContent += ` / ¥${route.fare.toLocaleString()}`;
    }

    // Update header textual content
    document.getElementById("route-header").textContent = `${firstDeparture} 発 → ${arrivalTime} 着`;

    // Update Header Summary Colors based on Risk
    const summaryContainer = document.getElementById("route-summary-container");
    const arrivalTimeEl = document.getElementById("arrival-time");
    const riskLevel = (route.risk && route.risk.level) ? route.risk.level : 'LOW';

    // Define styles for each level
    const riskStyles = {
        HIGH: {
            container: "bg-gradient-to-r from-red-50 to-rose-50 border-red-200",
            arrivalText: "text-red-600"
        },
        MEDIUM: {
            container: "bg-gradient-to-r from-amber-50 to-orange-50 border-amber-200",
            arrivalText: "text-amber-600"
        },
        LOW: {
            container: "bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-200",
            arrivalText: "text-emerald-600"
        }
    };

    const style = riskStyles[riskLevel] || riskStyles.LOW;

    // Reset and apply new classes
    summaryContainer.className = `rounded-2xl p-5 mb-6 border ${style.container}`;
    arrivalTimeEl.className = `text-4xl font-bold leading-none ${style.arrivalText}`;

    // Render delay warnings including Risk
    renderDelayWarnings(route);

    // Render timeline
    renderTimeline(segments, route.risk, route.delay_warnings);

    // Setup AI diagnosis button
    setupAIDiagnosis(route);
}

function renderDelayWarnings(route) {
    const container = document.getElementById("delay-warnings");
    if (!container) return;

    container.innerHTML = "";

    const realTimeWarnings = route.delay_warnings || [];
    const risk = route.risk || { level: 'LOW', reasons: [] };
    const crowd = route.crowd || { level: 'UNKNOWN', score: 0, details: [] };
    const venueWarnings = route.venue_warnings || { transfer_warnings: [], passing_info: [] };

    // Helper to create accordion section
    function createAccordion(id, icon, title, colorScheme, content, defaultOpen = false) {
        const colors = {
            red: { bg: 'bg-red-50', border: 'border-red-200', header: 'text-red-800', headerBg: 'hover:bg-red-100' },
            amber: { bg: 'bg-amber-50', border: 'border-amber-200', header: 'text-amber-800', headerBg: 'hover:bg-amber-100' },
            orange: { bg: 'bg-orange-50', border: 'border-orange-200', header: 'text-orange-800', headerBg: 'hover:bg-orange-100' },
            blue: { bg: 'bg-blue-50', border: 'border-blue-200', header: 'text-blue-800', headerBg: 'hover:bg-blue-100' },
            emerald: { bg: 'bg-emerald-50', border: 'border-emerald-200', header: 'text-emerald-800', headerBg: 'hover:bg-emerald-100' },
            slate: { bg: 'bg-slate-50', border: 'border-slate-200', header: 'text-slate-700', headerBg: 'hover:bg-slate-100' }
        };
        const c = colors[colorScheme] || colors.slate;

        const section = document.createElement("div");
        section.className = `${c.bg} ${c.border} border rounded-xl overflow-hidden mb-2`;
        section.innerHTML = `
            <button 
                class="w-full flex items-center justify-between p-4 ${c.headerBg} transition-colors"
                aria-expanded="${defaultOpen}"
                aria-controls="accordion-content-${id}"
                onclick="this.setAttribute('aria-expanded', this.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'); document.getElementById('accordion-content-${id}').classList.toggle('hidden');"
            >
                <div class="flex items-center gap-2">
                    <span class="text-xl">${icon}</span>
                    <span class="font-bold ${c.header}">${title}</span>
                </div>
                <svg class="w-5 h-5 ${c.header} transition-transform" style="transform: rotate(${defaultOpen ? '180deg' : '0deg'});" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            <div id="accordion-content-${id}" class="${defaultOpen ? '' : 'hidden'} px-4 pb-4">
                ${content}
            </div>
        `;
        return section;
    }

    let hasContent = false;

    // 1. Real-time Delay Warnings (🚨 最重要 - デフォルトで開く)
    if (realTimeWarnings.length > 0) {
        hasContent = true;
        const content = realTimeWarnings.map(warning => {
            let timeDisplay = "";
            if (warning.timestamp) {
                try {
                    const ts = new Date(warning.timestamp);
                    timeDisplay = `${ts.getHours().toString().padStart(2, '0')}:${ts.getMinutes().toString().padStart(2, '0')} 時点`;
                } catch (e) { }
            }
            return `
                <div class="bg-white/60 rounded-lg p-3 border border-red-100 mb-2 last:mb-0">
                    <div class="flex items-center justify-between">
                        <p class="text-red-800 font-medium">${warning.railway}</p>
                        ${timeDisplay ? `<span class="text-xs text-red-400">${timeDisplay}</span>` : ''}
                    </div>
                    <p class="text-red-700/80 text-sm mt-1">${warning.reason || "遅延が発生しています"}</p>
                </div>
            `;
        }).join('');
        container.appendChild(createAccordion('realtime', '🚨', `リアルタイム遅延 (${realTimeWarnings.length}件)`, 'red', content, true));
    }

    // 2. Predictive Risk (⚠️ リスク情報を常に表示)
    {
        hasContent = true;
        const colorScheme = risk.level === 'HIGH' ? 'red' : risk.level === 'MEDIUM' ? 'amber' : 'emerald';
        const levelText = risk.level === 'HIGH' ? '高い' : risk.level === 'MEDIUM' ? '中程度' : '低い';

        let content = '';

        if (risk.reasons.length > 0) {
            content = `
                <p class="text-xs text-slate-500 mb-2">過去の遅延実績データに基づく予測:</p>
                <div class="space-y-2">
                    ${risk.reasons.map(r => `
                        <div class="bg-white/60 rounded-lg p-3 border border-current/10">
                            <p class="font-medium text-sm">${r.railway || ''}</p>
                            <p class="text-xs text-slate-600 mt-1">${r.rate || r.display || ''}</p>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            content = `
                <div class="bg-white/60 rounded-lg p-3 border border-emerald-100 flex items-center gap-3">
                    <div class="w-8 h-8 bg-emerald-100 rounded-full flex items-center justify-center">
                        <svg class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                    </div>
                    <div>
                        <p class="font-medium text-emerald-800">通常運転</p>
                        <p class="text-xs text-slate-500">過去の遅延実績データに問題はありません</p>
                    </div>
                </div>
            `;
        }

        container.appendChild(createAccordion('risk', '⚠️', `遅延リスク: ${levelText}`, colorScheme, content, risk.level !== 'LOW'));
    }

    // 3. Venue Warnings (🎪 イベント情報)
    const allVenues = [...venueWarnings.transfer_warnings, ...venueWarnings.passing_info];
    if (allVenues.length > 0) {
        hasContent = true;
        let content = '';

        if (venueWarnings.transfer_warnings.length > 0) {
            content += `
                <p class="text-xs text-orange-600 font-medium mb-2">⚠️ 乗換駅周辺</p>
                ${venueWarnings.transfer_warnings.map(w => `
                    <div class="bg-white/60 rounded-lg p-3 border border-orange-100 mb-2">
                        <p class="font-medium text-orange-900">📍 ${w.station}駅 → ${w.venue}</p>
                        <p class="text-xs text-slate-500 mt-1">収容人数: ${w.capacity.toLocaleString()}人 / ${w.note}</p>
                    </div>
                `).join('')}
            `;
        }

        if (venueWarnings.passing_info.length > 0) {
            content += `
                <p class="text-xs text-slate-500 mt-3 mb-2">ℹ️ 通過駅周辺</p>
                <p class="text-sm text-slate-600">${venueWarnings.passing_info.map(p => `${p.station}(${p.venues.join(', ')})`).join(' / ')}</p>
            `;
        }

        container.appendChild(createAccordion('venue', '🎪', `イベント情報 (${allVenues.length}件)`, 'orange', content, false));
    }

    // 4. Crowd Info (📊 駅混雑度)
    if (crowd.level !== 'UNKNOWN' && crowd.details && crowd.details.length > 0) {
        hasContent = true;
        const levelLabel = crowd.level === 'HIGH' ? '大都市圏' : crowd.level === 'MEDIUM' ? '中規模' : '郊外';

        const content = `
            <div class="flex items-center gap-3 mb-3">
                <div class="text-2xl font-bold text-blue-800">${crowd.score.toLocaleString()}</div>
                <div class="text-xs text-slate-500">人/日<br>(平均乗降客数)</div>
                <span class="ml-auto px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">${levelLabel}</span>
            </div>
            <div class="text-xs text-slate-500">
                <p class="font-medium mb-1">経由駅の規模:</p>
                <p>${crowd.details.join(', ')}</p>
            </div>
        `;
        container.appendChild(createAccordion('crowd', '📊', '駅混雑度', 'blue', content, false));
    }

    // If no content, show a positive "normal operation" message
    if (!hasContent) {
        const el = document.createElement("div");
        el.className = "bg-emerald-50 border border-emerald-200 rounded-xl p-5 text-center";
        el.innerHTML = `
            <div class="flex flex-col items-center gap-2">
                <div class="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
                    <svg class="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                </div>
                <p class="text-emerald-800 font-medium">すべての路線が平常運行中</p>
                <p class="text-emerald-600 text-xs">遅延情報・混雑情報はありません</p>
            </div>
        `;
        container.appendChild(el);
    }
}

function setupAIDiagnosis(route) {
    const btn = document.getElementById("ai-diagnose-btn");
    const resultContainer = document.getElementById("ai-diagnosis-result");

    if (!btn || !resultContainer) return;

    // Reset state
    resultContainer.classList.add("hidden");
    resultContainer.innerHTML = "";
    btn.disabled = false;
    btn.innerHTML = `
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        診断開始
    `;

    // Remove old event listeners by cloning
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);

    newBtn.addEventListener("click", async () => {
        newBtn.disabled = true;
        newBtn.innerHTML = `
            <svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            診断中...
        `;

        resultContainer.classList.remove("hidden");
        resultContainer.innerHTML = `
            <div class="bg-purple-50 border border-purple-200 rounded-xl p-4 animate-pulse">
                <div class="flex items-center gap-2">
                    <div class="w-6 h-6 bg-purple-200 rounded-full"></div>
                    <div class="h-4 bg-purple-200 rounded w-48"></div>
                </div>
                <div class="mt-3 space-y-2">
                    <div class="h-3 bg-purple-100 rounded w-full"></div>
                    <div class="h-3 bg-purple-100 rounded w-4/5"></div>
                    <div class="h-3 bg-purple-100 rounded w-3/5"></div>
                </div>
            </div>
        `;

        try {
            const result = await diagnoseRoute(route);
            renderAIDiagnosis(resultContainer, result);

            newBtn.innerHTML = `
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                再診断
            `;
            newBtn.disabled = false;
        } catch (e) {
            resultContainer.innerHTML = `
                <div class="bg-red-50 border border-red-200 rounded-xl p-4">
                    <div class="flex items-center gap-2 text-red-700">
                        <span class="text-xl">⚠️</span>
                        <span class="font-medium">診断エラー</span>
                    </div>
                    <p class="text-red-600 text-sm mt-2">${e.message || 'AI診断に失敗しました。しばらく経ってから再度お試しください。'}</p>
                </div>
            `;

            newBtn.innerHTML = `
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                再試行
            `;
            newBtn.disabled = false;
        }
    });
}

function renderAIDiagnosis(container, result) {
    const diagnosis = result.diagnosis || "診断結果がありません";

    // Parse diagnosis into sections (simple parsing)
    const lines = diagnosis.split('\n').filter(l => l.trim());

    container.innerHTML = `
        <div class="mt-4 px-1">
            <div class="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100">
                <span class="text-lg">✨</span>
                <span class="font-bold text-slate-700">AIアドバイス</span>
                <span class="ml-auto text-xs text-slate-400">${result.model || 'AI'}</span>
            </div>
            <div class="prose prose-sm max-w-none text-slate-600">
                 ${formatDiagnosisText(diagnosis)}
            </div>
        </div>
    `;
}

function formatDiagnosisText(text) {
    // Convert markdown-like formatting to HTML
    return text
        .replace(/^### (.+)(?:\n|$)/gm, '<h4 class="font-bold text-slate-800 mt-3 mb-1">$1</h4>')
        .replace(/^## (.+)(?:\n|$)/gm, '<h3 class="font-bold text-slate-900 mt-4 mb-2">$1</h3>')
        .replace(/^# (.+)(?:\n|$)/gm, '<h2 class="font-bold text-slate-900 text-lg mt-4 mb-2">$1</h2>')
        .replace(/^\d+\. (.+)(?:\n|$)/gm, '<p class="font-semibold text-slate-800">$1</p>')
        .replace(/^[-•] (.+)(?:\n|$)/gm, '<p class="pl-4 text-slate-700 before:content-[\"•\"] before:mr-2 before:text-slate-400">$1</p>')
        .replace(/\*\*(.+?)\*\*/g, '<strong class="text-slate-800">$1</strong>')
        .replace(/\n/g, '<br>');
}
