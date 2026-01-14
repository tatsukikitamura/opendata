import"./modulepreload-polyfill-B5Qt9EMX.js";/* empty css              */import{g as x,a as h}from"./api-DS4I12Yo.js";let l=[];const b=new Set(["2025-01-01","2025-01-13","2025-02-11","2025-02-23","2025-02-24","2025-03-20","2025-04-29","2025-05-03","2025-05-04","2025-05-05","2025-05-06","2025-07-21","2025-08-11","2025-09-15","2025-09-23","2025-10-13","2025-11-03","2025-11-23","2025-11-24","2026-01-01","2026-01-12","2026-02-11","2026-02-23","2026-03-20","2026-04-29","2026-05-03","2026-05-04","2026-05-05","2026-05-06","2026-07-20","2026-08-11","2026-09-21","2026-09-22","2026-09-23","2026-10-12","2026-11-03","2026-11-23"]);function p(e){const n=new Date(e).getDay();return b.has(e)||n===0?"Holiday":n===6?"Saturday":"Weekday"}function E(e){switch(e){case"Holiday":return"🎌 祝日・休日ダイヤ";case"Saturday":return"📅 土曜ダイヤ";case"Weekday":return"📊 平日ダイヤ";default:return""}}document.addEventListener("DOMContentLoaded",async()=>{w(),v(),B(),D(),L(),S(),l=await x(),u("from-station"),u("to-station")});function w(){const e=document.getElementById("departure-date");if(e){const t=new Date,n=t.getFullYear(),a=String(t.getMonth()+1).padStart(2,"0"),s=String(t.getDate()).padStart(2,"0");e.value=`${n}-${a}-${s}`,f(e.value)}}function f(e){const t=document.getElementById("day-type-hint");if(t&&e){const n=p(e);t.textContent=E(n)}}function L(){const e=document.getElementById("departure-date");e&&e.addEventListener("change",()=>{f(e.value)})}async function S(){const e=document.getElementById("network-status-container");if(e){e.innerHTML=`
        <div class="bg-slate-50 border border-slate-100 rounded-xl p-4 flex items-center gap-3">
             <div class="w-10 h-10 bg-slate-200 rounded-full animate-pulse"></div>
             <div class="flex-1 space-y-2">
                 <div class="h-4 bg-slate-200 rounded w-1/3 animate-pulse"></div>
                 <div class="h-3 bg-slate-200 rounded w-2/3 animate-pulse"></div>
             </div>
        </div>
    `,e.classList.remove("hidden");try{const{updated_at:t,delays:n}=await h();let a="";if(t)try{const s=new Date(t),o=s.getMonth()+1,d=s.getDate(),r=s.getHours(),y=String(s.getMinutes()).padStart(2,"0");a=`${o}月${d}日 ${r}:${y} 現在`}catch(s){console.error(s)}if(n.length===0)e.innerHTML=`
                <div class="bg-emerald-50 border border-emerald-100 rounded-xl p-4 flex items-center gap-3 animate-fade-in relative">
                    <div class="bg-white p-2 rounded-full shadow-sm">
                        <span class="text-xl">✨</span>
                    </div>
                    <div class="flex-1">
                        <div class="flex justify-between items-start">
                             <p class="font-bold text-emerald-800 text-sm">平常運行中</p>
                             ${a?`<span class="text-[10px] text-emerald-500 font-medium bg-emerald-100/50 px-2 py-0.5 rounded-full">${a}</span>`:""}
                        </div>
                        <p class="text-xs text-emerald-600 mt-0.5">主要路線で大きな遅延は発生していません</p>
                    </div>
                </div>
            `;else{const s=[...new Set(n.map(d=>d.railway_name))],o=s.join("、");e.innerHTML=`
                <div class="bg-red-50 border border-red-100 rounded-xl p-4 animate-fade-in shadow-sm relative">
                    <div class="flex items-center gap-3">
                        <div class="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse shrink-0"></div>
                        <div class="flex-1">
                            <div class="flex justify-between items-start">
                                <p class="font-bold text-red-800 text-sm">
                                    <span class="text-base mr-1">${s.length}</span>路線で遅延が発生しています
                                </p>
                                ${a?`<span class="text-[10px] text-red-500 font-medium bg-red-100/50 px-2 py-0.5 rounded-full">${a}</span>`:""}
                            </div>
                            <p class="text-xs text-red-600 mt-0.5 leading-relaxed">
                                ${o}
                            </p>
                        </div>
                    </div>
                </div>
            `}}catch(t){console.error("Failed to render network status",t),e.innerHTML=`
             <div class="bg-slate-50 border border-slate-200 rounded-xl p-4 text-center text-xs text-slate-400">
                運行情報の取得に失敗しました
             </div>
        `}}}function u(e){const t=document.getElementById(e);if(!t)return;const n=t.parentElement;n.classList.add("relative");const a=document.createElement("ul");a.className="absolute z-50 w-full mt-1 bg-white border border-slate-200 rounded-xl shadow-xl max-h-60 overflow-y-auto hidden",n.appendChild(a),t.addEventListener("input",()=>{const s=t.value.trim();if(!s){a.classList.add("hidden");return}const o=l.filter(d=>d.includes(s));if(o.length===0){a.classList.add("hidden"),c(t),m(t,s);return}a.innerHTML="",o.forEach(d=>{const r=document.createElement("li");r.className="px-4 py-2 hover:bg-slate-50 cursor-pointer text-slate-700 transition-colors border-b border-slate-100 last:border-0",r.textContent=d,r.addEventListener("click",()=>{t.value=d,a.classList.add("hidden"),c(t)}),a.appendChild(r)}),a.classList.remove("hidden"),c(t),m(t,s)}),document.addEventListener("click",s=>{n.contains(s.target)||a.classList.add("hidden")}),t.addEventListener("focus",()=>{t.value.trim()&&t.dispatchEvent(new Event("input"))}),t.addEventListener("blur",()=>{const s=t.value.trim();s&&!l.includes(s)&&g(t,"無効な駅名です")})}let i=new Map;function m(e,t){i.has(e)&&clearTimeout(i.get(e));const n=setTimeout(()=>{t&&!l.includes(t)&&g(e,"無効な駅名です")},1e3);i.set(e,n)}function g(e,t){const n=e.parentElement.parentElement;let a=n.querySelector(".station-error-message");a||(a=document.createElement("p"),a.className="station-error-message text-red-500 text-xs mt-1 ml-1 font-bold flex items-center gap-1",n.appendChild(a)),a.textContent="⚠️ "+t,e.classList.add("border-red-500","focus:ring-red-200"),e.classList.remove("focus:ring-slate-400","border-slate-200")}function c(e){const n=e.parentElement.parentElement.querySelector(".station-error-message");n&&n.remove(),e.classList.remove("border-red-500","focus:ring-red-200"),e.classList.add("border-slate-200","focus:ring-slate-400"),i.has(e)&&(clearTimeout(i.get(e)),i.delete(e))}function v(){const e=new Date,t=String(e.getHours()).padStart(2,"0"),n=String(e.getMinutes()).padStart(2,"0"),a=document.getElementById("departure-time");a&&(a.value=`${t}:${n}`)}function I(e){const t=document.getElementById("departure-time");t&&(t.value=e)}function B(){const e=document.getElementById("btn-current-time");e&&e.addEventListener("click",v),document.querySelectorAll("[data-time]").forEach(n=>{n.addEventListener("click",()=>{I(n.dataset.time)})})}function D(){const e=document.getElementById("search-form");e&&e.addEventListener("submit",t=>{t.preventDefault();const n=document.getElementById("from-station").value,a=document.getElementById("to-station").value,s=document.getElementById("departure-date").value,o=document.getElementById("departure-time").value;if(!n||!a||!s||!o){alert("全ての項目を入力してください");return}if(n===a){alert("出発駅と到着駅が同じです。異なる駅を選択してください。");return}const d=p(s),r=new URLSearchParams;r.append("from",n),r.append("to",a),r.append("time",o),r.append("date",s),r.append("day_type",d),window.location.href=`./detail.html?${r.toString()}`})}
