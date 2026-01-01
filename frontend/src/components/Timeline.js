/**
 * Timeline component for rendering route segments
 */
import { getLineColor } from '../lib/utils.js';

export function renderTimeline(segments) {
    const timeline = document.getElementById("route-timeline");
    if (!timeline) return;
    
    timeline.innerHTML = "";

    segments.forEach((segment, index) => {
        const isLast = index === segments.length - 1;
        const lineColor = getLineColor(segment.railway || "");
        
        const segmentEl = document.createElement("div");
        segmentEl.className = "relative";
        
        const departureTime = segment.departure_time || "--:--";
        const trainInfo = segment.train_number 
            ? `${segment.train_type} ${segment.train_number}` 
            : segment.train_type || "";
        
        segmentEl.innerHTML = `
            <div class="flex items-start gap-4">
                <!-- Timeline dot and line -->
                <div class="flex flex-col items-center">
                    <div class="w-4 h-4 rounded-full ${lineColor} border-2 border-slate-800 shadow-lg z-10"></div>
                    ${!isLast ? `<div class="w-0.5 h-20 bg-slate-600"></div>` : ''}
                </div>
                
                <!-- Content -->
                <div class="flex-1 pb-4">
                    <div class="flex items-center gap-3 mb-2">
                        <span class="text-2xl font-bold text-white">${departureTime}</span>
                        <span class="text-lg text-slate-300">${segment.from}</span>
                    </div>
                    <div class="flex items-center gap-2 mb-2">
                        <span class="text-sm px-2 py-1 rounded-lg ${lineColor} text-white font-medium">
                            ${segment.railway}
                        </span>
                        ${trainInfo ? `<span class="text-xs text-slate-500">${trainInfo}</span>` : ''}
                    </div>
                    ${segment.note ? `
                    <div class="text-sm text-amber-400 bg-amber-500/10 border border-amber-500/30 rounded-lg px-3 py-2 mt-2">
                        ⚠️ ${segment.note}
                    </div>
                    ` : ''}
                    ${segment.arrival_time ? `
                    <div class="text-sm text-slate-400 flex items-center gap-1 mt-1">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                        </svg>
                        ${segment.arrival_time}着 ${segment.to}
                    </div>
                    ` : `
                    <div class="text-sm text-slate-400 flex items-center gap-1">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                        </svg>
                        ${segment.to} 方面
                    </div>
                    `}
                </div>
            </div>
        `;
        
        timeline.appendChild(segmentEl);
    });

    // Add final destination marker with arrival time
    if (segments.length > 0) {
        const lastSegment = segments[segments.length - 1];
        const finalTime = lastSegment.arrival_time || "";
        
        const finalEl = document.createElement("div");
        finalEl.className = "flex items-center gap-4";
        finalEl.innerHTML = `
            <div class="w-4 h-4 rounded-full bg-rose-500 border-2 border-slate-800 shadow-lg"></div>
            <div>
                <div class="flex items-center gap-2">
                    <span class="text-lg font-bold text-white">${lastSegment.to}</span>
                    <span class="text-sm text-slate-400">到着</span>
                </div>
                ${finalTime ? `<div class="text-2xl font-bold text-white mt-1">${finalTime}</div>` : ''}
            </div>
        `;
        timeline.appendChild(finalEl);
    }
}
