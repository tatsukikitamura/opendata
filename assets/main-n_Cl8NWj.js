import{g as v,a as g}from"./api-CUlB5ugs.js";let l=[];document.addEventListener("DOMContentLoaded",async()=>{p(),x(),b(),h(),l=await v(),m("from-station"),m("to-station")});async function h(){const t=document.getElementById("network-status-container");if(t)try{const e=await g();if(e.length===0)t.innerHTML=`
                <div class="bg-emerald-50 border border-emerald-100 rounded-xl p-4 flex items-center gap-3 animate-fade-in">
                    <div class="bg-white p-2 rounded-full shadow-sm">
                        <span class="text-xl">✨</span>
                    </div>
                    <div>
                        <p class="font-bold text-emerald-800 text-sm">平常運行中</p>
                        <p class="text-xs text-emerald-600">現在、主要路線で大きな遅延は発生していません。</p>
                    </div>
                </div>
            `;else{const s=[...new Set(e.map(r=>r.railway_name))],n=s.join("、");t.innerHTML=`
                <div class="bg-red-50 border border-red-100 rounded-xl p-4 animate-fade-in shadow-sm">
                    <div class="flex items-center gap-3">
                        <div class="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse flex-shrink-0"></div>
                        <div>
                            <p class="font-bold text-red-800 text-sm">
                                <span class="text-base mr-1">${s.length}</span>路線で遅延が発生しています
                            </p>
                            <p class="text-xs text-red-600 mt-0.5 leading-relaxed">
                                ${n}
                            </p>
                        </div>
                    </div>
                </div>
            `}t.classList.remove("hidden")}catch(e){console.error("Failed to render network status",e)}}function m(t){const e=document.getElementById(t);if(!e)return;const s=e.parentElement;s.classList.add("relative");const n=document.createElement("ul");n.className="absolute z-50 w-full mt-1 bg-white border border-slate-200 rounded-xl shadow-xl max-h-60 overflow-y-auto hidden",s.appendChild(n),e.addEventListener("input",()=>{const r=e.value.trim();if(!r){n.classList.add("hidden");return}const a=l.filter(d=>d.includes(r));if(a.length===0){n.classList.add("hidden"),c(e),u(e,r);return}n.innerHTML="",a.forEach(d=>{const i=document.createElement("li");i.className="px-4 py-2 hover:bg-slate-50 cursor-pointer text-slate-700 transition-colors border-b border-slate-100 last:border-0",i.textContent=d,i.addEventListener("click",()=>{e.value=d,n.classList.add("hidden"),c(e)}),n.appendChild(i)}),n.classList.remove("hidden"),c(e),u(e,r)}),document.addEventListener("click",r=>{s.contains(r.target)||n.classList.add("hidden")}),e.addEventListener("focus",()=>{e.value.trim()&&e.dispatchEvent(new Event("input"))}),e.addEventListener("blur",()=>{const r=e.value.trim();r&&!l.includes(r)&&f(e,"無効な駅名です")})}let o=new Map;function u(t,e){o.has(t)&&clearTimeout(o.get(t));const s=setTimeout(()=>{e&&!l.includes(e)&&f(t,"無効な駅名です")},1e3);o.set(t,s)}function f(t,e){const s=t.parentElement.parentElement;let n=s.querySelector(".station-error-message");n||(n=document.createElement("p"),n.className="station-error-message text-red-500 text-xs mt-1 ml-1 font-bold flex items-center gap-1",s.appendChild(n)),n.textContent="⚠️ "+e,t.classList.add("border-red-500","focus:ring-red-200"),t.classList.remove("focus:ring-slate-400","border-slate-200")}function c(t){const s=t.parentElement.parentElement.querySelector(".station-error-message");s&&s.remove(),t.classList.remove("border-red-500","focus:ring-red-200"),t.classList.add("border-slate-200","focus:ring-slate-400"),o.has(t)&&(clearTimeout(o.get(t)),o.delete(t))}function p(){const t=new Date,e=String(t.getHours()).padStart(2,"0"),s=String(t.getMinutes()).padStart(2,"0"),n=document.getElementById("departure-time");n&&(n.value=`${e}:${s}`)}function E(t){const e=document.getElementById("departure-time");e&&(e.value=t)}function x(){const t=document.getElementById("btn-current-time");t&&t.addEventListener("click",p),document.querySelectorAll("[data-time]").forEach(s=>{s.addEventListener("click",()=>{E(s.dataset.time)})})}function b(){const t=document.getElementById("search-form");t&&t.addEventListener("submit",e=>{e.preventDefault();const s=document.getElementById("from-station").value,n=document.getElementById("to-station").value,r=document.getElementById("departure-time").value;if(!s||!n||!r){alert("全ての項目を入力してください");return}const a=new URLSearchParams;a.append("from",s),a.append("to",n),a.append("time",r),window.location.href=`./detail.html?${a.toString()}`})}
