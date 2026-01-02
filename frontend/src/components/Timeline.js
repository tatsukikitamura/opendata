import { getLineColor } from '../lib/utils.js';

export function renderTimeline(segments) {
    const timeline = document.getElementById("route-timeline");
    if (!timeline) return;
    
    timeline.innerHTML = "";

    segments.forEach((segment, index) => {
        const isLastSegment = index === segments.length - 1;
        const lineColor = getLineColor(segment.railway || "");
        
        // --- 1. Station Row (Start or Transfer) ---
        const stationRow = document.createElement("div");
        stationRow.className = "flex";
        
        // Left: Time
        let timeHTML = "";
        if (index === 0) {
            // Start Station
            timeHTML = `<div class="text-xl font-bold text-white">${segment.departure_time}</div>`;
        } else {
            // Transfer Station (Arrival of prev, Departure of curr)
            const prevSeg = segments[index - 1];
            timeHTML = `
                <div class="text-sm text-slate-400 leading-tight">${prevSeg.arrival_time}着</div>
                <div class="text-base font-bold text-white leading-tight">${segment.departure_time}発</div>
            `;
        }

        // Center: Icon (Start Badge or Circle)
        let iconHTML = "";
        if (index === 0) {
            // Start "発" badge
             iconHTML = `<div class="w-6 h-6 bg-slate-200 text-slate-900 rounded-sm font-bold text-xs flex items-center justify-center z-10">発</div>`;
        } else {
            // Transfer Circle
            iconHTML = `<div class="w-4 h-4 bg-white border-2 border-slate-600 rounded-full z-10"></div>`;
        }

        stationRow.innerHTML = `
            <div class="w-20 text-right pr-4 flex flex-col justify-center gap-0.5">
                ${timeHTML}
            </div>
            <div class="w-8 flex flex-col items-center relative">
                 ${iconHTML}
                 <div class="w-1.5 ${lineColor} h-full absolute top-4 z-0"></div>
            </div>
            <div class="flex-1 pl-2 py-1 items-center flex">
                <span class="text-lg font-bold text-white border-b border-slate-700/50 pb-1 w-full">${segment.from}</span>
            </div>
        `;
        timeline.appendChild(stationRow);

        // --- 2. Travel Path Row ---
        // Train Info
        const trainInfo = segment.train_number 
            ? `<span class="text-slate-400 text-sm ml-2">${segment.train_type} ${segment.train_number}</span>` 
            : (segment.train_type ? `<span class="text-slate-400 text-sm ml-2">${segment.train_type}</span>` : "");
            
        const pathRow = document.createElement("div");
        pathRow.className = "flex min-h-[4rem]";
        
        pathRow.innerHTML = `
            <div class="w-20"></div> <!-- Time Spacer -->
            <div class="w-8 flex flex-col items-center relative">
                 <div class="w-1.5 ${lineColor} h-full absolute top-0 bottom-0 z-0"></div>
            </div>
            <div class="flex-1 pl-2 py-3 flex flex-col justify-center">
                 <div class="flex items-center">
                    <span class="text-2xl mr-2">🚃</span>
                    <div>
                        <div class="font-bold text-slate-200 text-sm">${segment.railway}</div>
                        ${trainInfo}
                    </div>
                 </div>
                 ${segment.note ? `<div class="text-xs text-amber-400 mt-1 ml-8">⚠️ ${segment.note}</div>` : ''}
            </div>
        `;
        timeline.appendChild(pathRow);

        // --- 3. Final Destination Row (Only for last segment) ---
        if (isLastSegment) {
            const endRow = document.createElement("div");
            endRow.className = "flex";
            
            endRow.innerHTML = `
                 <div class="w-20 text-right pr-4 flex flex-col justify-center">
                    <div class="text-xl font-bold text-white">${segment.arrival_time}</div>
                </div>
                <div class="w-8 flex flex-col items-center relative">
                     <div class="w-1.5 ${lineColor} h-3 absolute top-0 z-0"></div> <!-- Connect from above -->
                     <div class="w-6 h-6 bg-slate-600 text-white rounded-sm font-bold text-xs flex items-center justify-center z-10 mt-2">着</div>
                </div>
                <div class="flex-1 pl-2 py-2 items-center flex">
                    <span class="text-lg font-bold text-white border-b border-slate-700/50 pb-1 w-full">${segment.to}</span>
                </div>
            `;
            timeline.appendChild(endRow);
        }
    });
}
