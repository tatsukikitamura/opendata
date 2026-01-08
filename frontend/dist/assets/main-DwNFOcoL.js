import{g,a as x}from"./api-BNF2dpJQ.js";/* empty css              */let l=[];document.addEventListener("DOMContentLoaded",async()=>{f(),E(),w(),h(),l=await g(),m("from-station"),m("to-station")});async function h(){const e=document.getElementById("network-status-container");if(e){e.innerHTML=`
        <div class="bg-slate-50 border border-slate-100 rounded-xl p-4 flex items-center gap-3">
             <div class="w-10 h-10 bg-slate-200 rounded-full animate-pulse"></div>
             <div class="flex-1 space-y-2">
                 <div class="h-4 bg-slate-200 rounded w-1/3 animate-pulse"></div>
                 <div class="h-3 bg-slate-200 rounded w-2/3 animate-pulse"></div>
             </div>
        </div>
    `,e.classList.remove("hidden");try{const{updated_at:t,delays:n}=await x();let s="";if(t)try{const a=new Date(t),r=a.getMonth()+1,d=a.getDate(),i=a.getHours(),v=String(a.getMinutes()).padStart(2,"0");s=`${r}月${d}日 ${i}:${v} 現在`}catch(a){console.error(a)}if(n.length===0)e.innerHTML=`
                <div class="bg-emerald-50 border border-emerald-100 rounded-xl p-4 flex items-center gap-3 animate-fade-in relative">
                    <div class="bg-white p-2 rounded-full shadow-sm">
                        <span class="text-xl">✨</span>
                    </div>
                    <div class="flex-1">
                        <div class="flex justify-between items-start">
                             <p class="font-bold text-emerald-800 text-sm">平常運行中</p>
                             ${s?`<span class="text-[10px] text-emerald-500 font-medium bg-emerald-100/50 px-2 py-0.5 rounded-full">${s}</span>`:""}
                        </div>
                        <p class="text-xs text-emerald-600 mt-0.5">主要路線で大きな遅延は発生していません</p>
                    </div>
                </div>
            `;else{const a=[...new Set(n.map(d=>d.railway_name))],r=a.join("、");e.innerHTML=`
                <div class="bg-red-50 border border-red-100 rounded-xl p-4 animate-fade-in shadow-sm relative">
                    <div class="flex items-center gap-3">
                        <div class="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse shrink-0"></div>
                        <div class="flex-1">
                            <div class="flex justify-between items-start">
                                <p class="font-bold text-red-800 text-sm">
                                    <span class="text-base mr-1">${a.length}</span>路線で遅延が発生しています
                                </p>
                                ${s?`<span class="text-[10px] text-red-500 font-medium bg-red-100/50 px-2 py-0.5 rounded-full">${s}</span>`:""}
                            </div>
                            <p class="text-xs text-red-600 mt-0.5 leading-relaxed">
                                ${r}
                            </p>
                        </div>
                    </div>
                </div>
            `}}catch(t){console.error("Failed to render network status",t),e.innerHTML=`
             <div class="bg-slate-50 border border-slate-200 rounded-xl p-4 text-center text-xs text-slate-400">
                運行情報の取得に失敗しました
             </div>
        `}}}function m(e){const t=document.getElementById(e);if(!t)return;const n=t.parentElement;n.classList.add("relative");const s=document.createElement("ul");s.className="absolute z-50 w-full mt-1 bg-white border border-slate-200 rounded-xl shadow-xl max-h-60 overflow-y-auto hidden",n.appendChild(s),t.addEventListener("input",()=>{const a=t.value.trim();if(!a){s.classList.add("hidden");return}const r=l.filter(d=>d.includes(a));if(r.length===0){s.classList.add("hidden"),c(t),u(t,a);return}s.innerHTML="",r.forEach(d=>{const i=document.createElement("li");i.className="px-4 py-2 hover:bg-slate-50 cursor-pointer text-slate-700 transition-colors border-b border-slate-100 last:border-0",i.textContent=d,i.addEventListener("click",()=>{t.value=d,s.classList.add("hidden"),c(t)}),s.appendChild(i)}),s.classList.remove("hidden"),c(t),u(t,a)}),document.addEventListener("click",a=>{n.contains(a.target)||s.classList.add("hidden")}),t.addEventListener("focus",()=>{t.value.trim()&&t.dispatchEvent(new Event("input"))}),t.addEventListener("blur",()=>{const a=t.value.trim();a&&!l.includes(a)&&p(t,"無効な駅名です")})}let o=new Map;function u(e,t){o.has(e)&&clearTimeout(o.get(e));const n=setTimeout(()=>{t&&!l.includes(t)&&p(e,"無効な駅名です")},1e3);o.set(e,n)}function p(e,t){const n=e.parentElement.parentElement;let s=n.querySelector(".station-error-message");s||(s=document.createElement("p"),s.className="station-error-message text-red-500 text-xs mt-1 ml-1 font-bold flex items-center gap-1",n.appendChild(s)),s.textContent="⚠️ "+t,e.classList.add("border-red-500","focus:ring-red-200"),e.classList.remove("focus:ring-slate-400","border-slate-200")}function c(e){const n=e.parentElement.parentElement.querySelector(".station-error-message");n&&n.remove(),e.classList.remove("border-red-500","focus:ring-red-200"),e.classList.add("border-slate-200","focus:ring-slate-400"),o.has(e)&&(clearTimeout(o.get(e)),o.delete(e))}function f(){const e=new Date,t=String(e.getHours()).padStart(2,"0"),n=String(e.getMinutes()).padStart(2,"0"),s=document.getElementById("departure-time");s&&(s.value=`${t}:${n}`)}function b(e){const t=document.getElementById("departure-time");t&&(t.value=e)}function E(){const e=document.getElementById("btn-current-time");e&&e.addEventListener("click",f),document.querySelectorAll("[data-time]").forEach(n=>{n.addEventListener("click",()=>{b(n.dataset.time)})})}function w(){const e=document.getElementById("search-form");e&&e.addEventListener("submit",t=>{t.preventDefault();const n=document.getElementById("from-station").value,s=document.getElementById("to-station").value,a=document.getElementById("departure-time").value;if(!n||!s||!a){alert("全ての項目を入力してください");return}const r=new URLSearchParams;r.append("from",n),r.append("to",s),r.append("time",a),window.location.href=`./detail.html?${r.toString()}`})}
