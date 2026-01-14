import{b as i}from"./api-BA95tgqH.js";document.addEventListener("DOMContentLoaded",async()=>{const t=new URLSearchParams(window.location.search).get("line");if(document.getElementById("back-button").addEventListener("click",()=>{window.history.back()}),!t){document.getElementById("history-list").innerHTML=`
                    <div class="p-4 bg-red-50 text-red-600 rounded-xl border border-red-100 text-center">
                        路線が指定されていません。
                    </div>
                `;return}document.getElementById("line-name").textContent=t;try{const n=await i(t);m(n)}catch(n){console.error(n),document.getElementById("history-list").innerHTML=`
                    <div class="p-4 bg-red-50 text-red-600 rounded-xl border border-red-100 text-center">
                        データの取得に失敗しました。<br>
                        <span class="text-sm opacity-75">${n.message}</span>
                    </div>
                `}});function m(e){const t=document.getElementById("history-list"),n=document.getElementById("empty-state"),o=document.getElementById("line-name");if(t.innerHTML="",!e||e.length===0){t.classList.add("hidden"),n.classList.remove("hidden");return}e[0].railway_name&&(o.textContent=e[0].railway_name,document.getElementById("header-title").textContent=e[0].railway_name+" 遅延履歴"),e.forEach(d=>{const a=new Date(d.timestamp),r=`${a.getMonth()+1}/${a.getDate()} ${a.getHours().toString().padStart(2,"0")}:${a.getMinutes().toString().padStart(2,"0")}`,s=document.createElement("div");s.className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm hover:shadow-md transition-shadow",s.innerHTML=`
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-sm font-mono text-slate-500 bg-slate-100 px-2 py-1 rounded">${r}</span>
                        <span class="px-2 py-1 text-xs font-bold bg-amber-100 text-amber-700 rounded border border-amber-200">遅延</span>
                    </div>
                    <p class="text-slate-800 font-medium">${d.status_text||"遅延が発生しました"}</p>
                `,t.appendChild(s)})}
