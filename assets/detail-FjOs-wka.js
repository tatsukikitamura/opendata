import{s as H,d as C}from"./api-DfL2DRXj.js";/* empty css              */function T(a){const e=a.toLowerCase();return e.includes("山手")?"bg-green-500":e.includes("中央")&&e.includes("快速")?"bg-orange-500":e.includes("中央")&&e.includes("総武")?"bg-yellow-500":e.includes("京浜東北")?"bg-sky-500":e.includes("埼京")?"bg-emerald-600":e.includes("湘南新宿")?"bg-orange-600":e.includes("総武快速")||e.includes("総武線快速")?"bg-blue-600":e.includes("常磐")?"bg-cyan-500":e.includes("東海道")?"bg-orange-400":e.includes("横須賀")?"bg-blue-500":e.includes("武蔵野")?"bg-orange-600":e.includes("京葉")?"bg-red-500":e.includes("銀座")?"bg-orange-400":e.includes("丸ノ内")?"bg-red-500":e.includes("日比谷")?"bg-gray-400":e.includes("東西")?"bg-sky-400":e.includes("千代田")?"bg-green-600":e.includes("有楽町")?"bg-yellow-600":e.includes("半蔵門")?"bg-purple-500":e.includes("南北")?"bg-emerald-400":e.includes("副都心")?"bg-amber-700":e.includes("浅草")?"bg-rose-400":e.includes("三田")?"bg-blue-700":e.includes("新宿")?"bg-lime-500":e.includes("大江戸")?"bg-pink-600":"bg-slate-500"}function k(a){document.getElementById("loading-state").classList.add("hidden"),document.getElementById("result-state").classList.add("hidden"),document.getElementById("error-state").classList.remove("hidden"),document.getElementById("error-message").textContent=a,document.getElementById("route-subheader").textContent=""}function S(a,e=null,r=[]){const t=document.getElementById("route-timeline");t&&(t.innerHTML="",a.forEach((s,i)=>{const o=i===a.length-1;let c=T(s.railway||"");if(e&&e.reasons&&s.railway_id){const d=s.railway_id.split(".").pop();e.reasons.find(v=>v.railway===d)&&(e.level==="HIGH"?c="bg-red-500":e.level==="MEDIUM"&&(c="bg-amber-500"))}const m=document.createElement("div");m.className="flex";let p="";i===0?p=`<div class="text-xl font-bold text-slate-800">${s.departure_time}</div>`:p=`
                <div class="text-sm text-slate-500 leading-tight">${a[i-1].arrival_time}着</div>
                <div class="text-base font-bold text-slate-800 leading-tight">${s.departure_time}発</div>
            `;let f="";i===0?f='<div class="w-6 h-6 bg-slate-800 text-white rounded-sm font-bold text-xs flex items-center justify-center z-10 shadow-md">発</div>':f='<div class="w-4 h-4 bg-white border-2 border-slate-400 rounded-full z-10 shadow-sm"></div>',m.innerHTML=`
            <div class="w-20 text-right pr-4 flex flex-col justify-center gap-0.5">
                ${p}
            </div>
            <div class="w-8 flex flex-col items-center relative">
                 ${f}
                 <div class="w-1.5 ${c} h-full absolute top-4 z-0 opacity-80"></div>
            </div>
            <div class="flex-1 pl-2 py-1 items-center flex">
                <span class="text-lg font-bold text-slate-800 border-b border-slate-200 pb-1 w-full">${s.from}</span>
            </div>
        `,t.appendChild(m);const n=s.train_number?`<span class="text-slate-500 text-sm ml-2">${s.train_type} ${s.train_number}</span>`:s.train_type?`<span class="text-slate-500 text-sm ml-2">${s.train_type}</span>`:"",l=document.createElement("div");if(l.className="flex min-h-[4rem]",l.innerHTML=`
            <div class="w-20"></div> <!-- Time Spacer -->
            <div class="w-8 flex flex-col items-center relative">
                 <div class="w-1.5 ${c} h-full absolute top-0 bottom-0 z-0 opacity-80"></div>
            </div>
            <div class="flex-1 pl-2 py-3 flex flex-col justify-center">
                 <div class="flex items-center">
                    <span class="text-2xl mr-2">🚃</span>
                    <div>
                        <div class="font-bold text-slate-700 text-sm">${s.railway}</div>
                        ${n}
                    </div>
                 </div>
                 ${s.note?`<div class="text-xs text-amber-600 mt-1 ml-8 font-medium">⚠️ ${s.note}</div>`:""}
            </div>
        `,t.appendChild(l),o){const d=document.createElement("div");d.className="flex",d.innerHTML=`
                 <div class="w-20 text-right pr-4 flex flex-col justify-center">
                    <div class="text-xl font-bold text-slate-800">${s.arrival_time}</div>
                </div>
                <div class="w-8 flex flex-col items-center relative">
                     <div class="w-1.5 ${c} h-3 absolute top-0 z-0 opacity-80"></div> <!-- Connect from above -->
                     <div class="w-6 h-6 bg-slate-600 text-white rounded-sm font-bold text-xs flex items-center justify-center z-10 mt-2 shadow-md">着</div>
                </div>
                <div class="flex-1 pl-2 py-2 items-center flex">
                    <span class="text-lg font-bold text-slate-800 border-b border-slate-200 pb-1 w-full">${s.to}</span>
                </div>
            `,t.appendChild(d)}}))}let E=[];document.addEventListener("DOMContentLoaded",async()=>{const a=new URLSearchParams(window.location.search),e=a.get("from"),r=a.get("to"),t=a.get("time"),s=a.get("day_type");if(!e||!r||!t){k("出発駅、到着駅、時刻を指定してください。");return}document.getElementById("route-header").textContent=`${e} → ${r}`,document.getElementById("route-subheader").textContent=`${t} 以降の電車を検索中...`,await _(e,r,t,s),document.getElementById("back-to-list").addEventListener("click",()=>{B()})});async function _(a,e,r,t=null){try{const s=await H(a,e,r,t);if(!s.routes||s.routes.length===0){k("ルートが見つかりませんでした。");return}E=s.routes,j(),document.getElementById("loading-state").classList.add("hidden"),document.getElementById("result-state").classList.remove("hidden"),B()}catch(s){s.message&&k(s.message)}}function B(){document.getElementById("route-list-view").classList.remove("hidden"),document.getElementById("route-detail-view").classList.add("hidden"),document.getElementById("global-back-link").classList.remove("hidden"),document.getElementById("main-header").classList.remove("hidden"),document.getElementById("route-header").textContent="検索結果"}function M(a){document.getElementById("route-list-view").classList.add("hidden"),document.getElementById("route-detail-view").classList.remove("hidden"),document.getElementById("global-back-link").classList.add("hidden"),document.getElementById("main-header").classList.add("hidden"),N(a)}function j(){const a=document.getElementById("route-list-container");a.innerHTML="";let e=-1,r=-1;E.forEach((t,s)=>{const i=t.scores?.speed||0,o=t.scores?.comfort||0,c=t.scores?.reliability||0,m=t.scores?.cost||0,p=i+o+c+m;p>r&&(r=p,e=s)}),E.forEach((t,s)=>{const i=t.segments||[],o=i.length>0&&i[0].departure_time?i[0].departure_time:"--:--",m=(i.length>0?i[i.length-1]:null)?.arrival_time||"--:--",p=t.transfers||0,f=t.risk||{level:"LOW"};let n="";if(o!=="--:--"&&m!=="--:--"){const[b,x]=o.split(":").map(Number),[g,w]=m.split(":").map(Number);let $=g*60+w-(b*60+x);$<0&&($+=1440);const y=Math.floor($/60),L=$%60;n=y>0?`${y}時間${L}分`:`${L}分`}const l=document.createElement("div");let d="bg-white hover:bg-slate-50 border-slate-200 shadow-sm";f.level==="HIGH"?d="bg-red-50 hover:bg-red-100 border-red-200 shadow-sm":f.level==="MEDIUM"&&(d="bg-amber-50 hover:bg-amber-100 border-amber-200 shadow-sm");const u=s===e&&r>0;u&&(d+=" ring-2 ring-emerald-500 ring-offset-2"),l.className=`p-6 md:p-8 rounded-xl border transition-all cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-6 md:gap-0 ${d} focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 relative`,l.setAttribute("role","button"),l.setAttribute("tabindex","0"),l.setAttribute("aria-label",`${o}発 ${m}着 乗換${p}回 ${n}`);let v="";f.level==="HIGH"?v='<span class="px-2 py-1 rounded text-xs font-bold bg-red-100 text-red-700 border border-red-200">遅延リスク高</span>':f.level==="MEDIUM"?v='<span class="px-2 py-1 rounded text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200">遅延注意</span>':v='<span class="px-2 py-1 rounded text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">平常運行</span>';const h=u?`<div class="absolute -top-3 left-6 bg-yellow-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-md flex items-center gap-1">
                <span>⭐️</span> ベストバランス
            </div>`:"";l.innerHTML=`
            ${h}
            <div class="w-full md:w-auto">
                <div class="flex items-center gap-3 mb-1">
                    <span class="text-2xl font-bold text-slate-800">${m} 着</span>
                    <span class="text-sm text-slate-500 hidden md:inline">(${o} 発)</span>
                    ${n?`<span class="text-sm font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">${n}</span>`:""}
                </div>
                <div class="text-sm text-slate-500 mt-2">
                    乗換 ${p}回
                    ${t.fare?`<span class="ml-3 text-slate-800 font-bold">¥${t.fare.toLocaleString()}</span>`:""}
                </div>
            </div>
            <div class="w-full md:w-auto flex justify-center md:block">
                <!-- 4-Axis Scores -->
                <div class="mt-0 md:mt-3 text-xs space-y-1 w-full md:w-48">
                    <div class="flex items-center gap-4">
                        <span class="w-8 text-slate-500">速さ</span>
                        <div class="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div class="h-full bg-blue-500" style="width: ${(t.scores?.speed||0)*20}%"></div>
                        </div>
                        <span class="w-6 text-right font-mono text-slate-600">${(t.scores?.speed||0).toFixed(1)}</span>
                    </div>
                    <div class="flex items-center gap-4">
                        <span class="w-8 text-slate-500">快適</span>
                        <div class="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div class="h-full bg-emerald-500" style="width: ${(t.scores?.comfort||0)*20}%"></div>
                        </div>
                        <span class="w-6 text-right font-mono text-slate-600">${(t.scores?.comfort||0).toFixed(1)}</span>
                    </div>
                    <div class="flex items-center gap-4">
                        <span class="w-8 text-slate-500">安定</span>
                        <div class="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div class="h-full bg-purple-500" style="width: ${(t.scores?.reliability||0)*20}%"></div>
                        </div>
                        <span class="w-6 text-right font-mono text-slate-600">${(t.scores?.reliability||0).toFixed(1)}</span>
                    </div>
                    <div class="flex items-center gap-4">
                        <span class="w-8 text-slate-500">安さ</span>
                        <div class="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div class="h-full bg-orange-500" style="width: ${(t.scores?.cost||0)*20}%"></div>
                        </div>
                        <span class="w-6 text-right font-mono text-slate-600">${(t.scores?.cost||0).toFixed(1)}</span>
                    </div>
                </div>
            </div>
            <div class="w-full md:w-auto text-left md:text-right flex flex-row-reverse md:block justify-between items-center md:items-end">
                <div class="md:mb-2">${v}</div>
                <div class="text-xs text-slate-400 mt-0 md:mt-2 flex items-center justify-end gap-1">
                    詳細を見る
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                </div>
            </div>
        `,l.addEventListener("click",()=>{M(s)}),l.addEventListener("keydown",b=>{(b.key==="Enter"||b.key===" ")&&(b.preventDefault(),M(s))}),a.appendChild(l)})}function N(a){const e=E[a];if(!e)return;const r=e.segments||[],t=r.length>0&&r[0].departure_time?r[0].departure_time:"--:--",i=(r.length>0?r[r.length-1]:null)?.arrival_time||"--:--";let o="--分";if(t!=="--:--"&&i!=="--:--"&&t&&i){const[d,u]=t.split(":").map(Number),[v,h]=i.split(":").map(Number);let b=v*60+h-(d*60+u);b<0&&(b+=1440);const x=Math.floor(b/60),g=b%60;o=x>0?`${x}時間${g}分`:`${g}分`}document.getElementById("first-departure").textContent=t,document.getElementById("arrival-time").textContent=i,document.getElementById("transfer-count").textContent=`乗換 ${e.transfers||0}回`;const c=document.getElementById("total-fare");c&&(c.textContent=e.fare?`¥${e.fare.toLocaleString()}`:"---"),document.getElementById("total-duration").textContent=o,e.fare&&(document.getElementById("total-duration").textContent+=` / ¥${e.fare.toLocaleString()}`),document.getElementById("route-header").textContent=`${t} 発 → ${i} 着`;const m=document.getElementById("route-summary-container"),p=document.getElementById("arrival-time"),f=e.risk&&e.risk.level?e.risk.level:"LOW",n={HIGH:{container:"bg-gradient-to-r from-red-50 to-rose-50 border-red-200",arrivalText:"text-red-600"},MEDIUM:{container:"bg-gradient-to-r from-amber-50 to-orange-50 border-amber-200",arrivalText:"text-amber-600"},LOW:{container:"bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-200",arrivalText:"text-emerald-600"}},l=n[f]||n.LOW;m.className=`rounded-2xl p-5 mb-6 border ${l.container}`,p.className=`text-4xl font-bold leading-none ${l.arrivalText}`,D(e),S(r,e.risk,e.delay_warnings),A(e)}function D(a){const e=document.getElementById("delay-warnings");if(!e)return;e.innerHTML="";const r=a.delay_warnings||[],t=a.risk||{level:"LOW",reasons:[]},s=a.crowd||{level:"UNKNOWN",score:0,details:[]},i=a.venue_warnings||{transfer_warnings:[],passing_info:[]};function o(n,l,d,u,v,h=!1){const b={red:{bg:"bg-red-50",border:"border-red-200",header:"text-red-800",headerBg:"hover:bg-red-100"},amber:{bg:"bg-amber-50",border:"border-amber-200",header:"text-amber-800",headerBg:"hover:bg-amber-100"},orange:{bg:"bg-orange-50",border:"border-orange-200",header:"text-orange-800",headerBg:"hover:bg-orange-100"},blue:{bg:"bg-blue-50",border:"border-blue-200",header:"text-blue-800",headerBg:"hover:bg-blue-100"},emerald:{bg:"bg-emerald-50",border:"border-emerald-200",header:"text-emerald-800",headerBg:"hover:bg-emerald-100"},slate:{bg:"bg-slate-50",border:"border-slate-200",header:"text-slate-700",headerBg:"hover:bg-slate-100"}},x=b[u]||b.slate,g=document.createElement("div");g.className=`${x.bg} ${x.border} border rounded-xl overflow-hidden mb-2`,g.innerHTML=`
            <button 
                class="w-full flex items-center justify-between p-4 ${x.headerBg} transition-colors"
                aria-expanded="${h}"
                aria-controls="accordion-content-${n}"
                id="accordion-btn-${n}"
            >
                <div class="flex items-center gap-2">
                    <span class="text-xl">${l}</span>
                    <span class="font-bold ${x.header}">${d}</span>
                </div>
                <svg class="w-5 h-5 ${x.header} transition-transform duration-200 ${h?"rotate-180":""}" id="accordion-icon-${n}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            <div id="accordion-content-${n}" class="${h?"":"hidden"} px-4 pb-4">
                ${v}
            </div>
        `;const w=g.querySelector(`#accordion-btn-${n}`);return w.addEventListener("click",()=>{const y=!(w.getAttribute("aria-expanded")==="true");w.setAttribute("aria-expanded",y);const L=g.querySelector(`#accordion-icon-${n}`),I=g.querySelector(`#accordion-content-${n}`);y?(L.classList.add("rotate-180"),I.classList.remove("hidden")):(L.classList.remove("rotate-180"),I.classList.add("hidden"))}),g}let c=!1;const m=(n,l,d="slate")=>`
        <div class="bg-white/60 rounded-lg p-3 border border-${d}-100">
            <p class="font-medium text-${d}-800">${n}</p>
            <p class="text-xs text-slate-500 mt-1">${l}</p>
        </div>
    `,p=(n,l)=>`
        <div class="bg-white/60 rounded-lg p-3 border border-emerald-100 flex items-center gap-3">
            <div class="w-8 h-8 bg-emerald-100 rounded-full flex items-center justify-center shrink-0">
                <svg class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
            </div>
            <div>
                <p class="font-medium text-emerald-800">${n}</p>
                <p class="text-xs text-slate-500">${l}</p>
            </div>
        </div>
    `;if(c=!0,r.length>0){const n=r.map(l=>{let d="";if(l.timestamp)try{const u=new Date(l.timestamp);d=`${u.getHours().toString().padStart(2,"0")}:${u.getMinutes().toString().padStart(2,"0")} 時点`}catch{}return`
                <div class="bg-white/60 rounded-lg p-3 border border-red-100 mb-2 last:mb-0">
                    <div class="flex items-center justify-between">
                        <p class="font-medium text-red-800">${l.railway}</p>
                        ${d?`<span class="text-xs text-red-400">${d}</span>`:""}
                    </div>
                    <p class="text-xs text-slate-500 mt-1">${l.reason||"遅延が発生しています"}</p>
                </div>
            `}).join("");e.appendChild(o("realtime","📡",`運行情報 (${r.length}件の遅延)`,"red",n,!0))}else{const n=p("平常運行","現在、すべての路線で遅延は発生していません");e.appendChild(o("realtime","📡","運行情報","emerald",n,!1))}{c=!0;const n=t.level==="HIGH"?"red":t.level==="MEDIUM"?"amber":"emerald",l=t.level==="HIGH"?"高リスク":t.level==="MEDIUM"?"注意":"低リスク";let d="";t.reasons.length>0?d=`
                <p class="text-xs text-slate-500 mb-2">過去の遅延データに基づく予測:</p>
                <div class="space-y-2">
                    ${t.reasons.map(u=>m(u.railway||"",u.rate||u.display||"",n)).join("")}
                </div>
            `:d=p("リスクなし","過去の遅延データに問題は見つかりませんでした"),e.appendChild(o("risk","📊",`遅延リスク: ${l}`,n,d,t.level!=="LOW"))}const f=[...i.transfer_warnings,...i.passing_info];if(f.length>0){c=!0;let n="";i.transfer_warnings.length>0&&(n+=`
                <p class="text-xs text-amber-600 font-medium mb-2">乗換駅周辺</p>
                <div class="space-y-2 mb-3">
                    ${i.transfer_warnings.map(l=>m(`${l.station}駅 → ${l.venue}`,`収容人数: ${l.capacity.toLocaleString()}人 / ${l.note}`,"amber")).join("")}
                </div>
            `),i.passing_info.length>0&&(n+=`
                <p class="text-xs text-slate-500 mb-2">通過駅周辺</p>
                <p class="text-sm text-slate-600">${i.passing_info.map(l=>`${l.station}(${l.venues.join(", ")})`).join(" / ")}</p>
            `),e.appendChild(o("venue","📍",`周辺イベント (${f.length}件)`,"amber",n,!1))}if(s.level!=="UNKNOWN"&&s.details&&s.details.length>0){c=!0;const n=s.level==="HIGH"?"amber":"slate",l=s.level==="HIGH"?"混雑":s.level==="MEDIUM"?"普通":"空いている",d=`
            <div class="bg-white/60 rounded-lg p-3 border border-${n}-100">
                <div class="flex items-center gap-3 mb-2">
                    <div class="text-xl font-bold text-slate-800">${s.score.toLocaleString()}</div>
                    <div class="text-xs text-slate-500">人/日 (平均)</div>
                    <span class="ml-auto px-2 py-1 text-xs font-medium bg-${n}-100 text-${n}-700 rounded-full">${l}</span>
                </div>
                <p class="text-xs text-slate-500">経路: ${s.details.join(" → ")}</p>
            </div>
        `;e.appendChild(o("crowd","📊",`経路の混雑度: ${l}`,n,d,!1))}if(!c){const n=document.createElement("div");n.className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 text-center",n.innerHTML=`
            <div class="flex flex-col items-center gap-2">
                <div class="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
                    <svg class="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                </div>
                <p class="text-emerald-800 font-medium">すべての路線が平常運行中</p>
                <p class="text-emerald-600 text-xs">遅延情報・混雑情報はありません</p>
            </div>
        `,e.appendChild(n)}}function A(a){const e=document.getElementById("ai-diagnose-btn"),r=document.getElementById("ai-diagnosis-result");if(!e||!r)return;r.classList.add("hidden"),r.innerHTML="",e.disabled=!1,e.innerHTML=`
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        診断開始
    `;const t=e.cloneNode(!0);e.parentNode.replaceChild(t,e),t.addEventListener("click",async()=>{t.disabled=!0,t.innerHTML=`
            <svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            診断中...
        `,r.classList.remove("hidden"),r.innerHTML=`
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
        `;try{const s=await C(a);W(r,s),t.innerHTML=`
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                再診断
            `,t.disabled=!1}catch(s){r.innerHTML=`
                <div class="bg-red-50 border border-red-200 rounded-xl p-4">
                    <div class="flex items-center gap-2 text-red-700">
                        <span class="text-xl">⚠️</span>
                        <span class="font-medium">診断エラー</span>
                    </div>
                    <p class="text-red-600 text-sm mt-2">${s.message||"AI診断に失敗しました。しばらく経ってから再度お試しください。"}</p>
                </div>
            `,t.innerHTML=`
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                再試行
            `,t.disabled=!1}})}function W(a,e){const r=e.diagnosis||"診断結果がありません";r.split(`
`).filter(t=>t.trim()),a.innerHTML=`
        <div class="mt-4 px-1">
            <div class="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100">
                <span class="text-lg">✨</span>
                <span class="font-bold text-slate-700">AIアドバイス</span>
                <span class="ml-auto text-xs text-slate-400">${e.model||"AI"}</span>
            </div>
            <div class="prose prose-sm max-w-none text-slate-600">
                 ${R(r)}
            </div>
        </div>
    `}function R(a){return a.replace(/^### (.+)(?:\n|$)/gm,'<h4 class="font-bold text-slate-800 mt-3 mb-1">$1</h4>').replace(/^## (.+)(?:\n|$)/gm,'<h3 class="font-bold text-slate-900 mt-4 mb-2">$1</h3>').replace(/^# (.+)(?:\n|$)/gm,'<h2 class="font-bold text-slate-900 text-lg mt-4 mb-2">$1</h2>').replace(/^\d+\. (.+)(?:\n|$)/gm,'<p class="font-semibold text-slate-800">$1</p>').replace(/^[-•] (.+)(?:\n|$)/gm,'<p class="pl-4 text-slate-700 before:content-["•"] before:mr-2 before:text-slate-400">$1</p>').replace(/\*\*(.+?)\*\*/g,'<strong class="text-slate-800">$1</strong>').replace(/\n/g,"<br>")}
