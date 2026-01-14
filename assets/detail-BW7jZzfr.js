import{s as H,d as C}from"./api-BA95tgqH.js";/* empty css              */function S(a){const e=a.toLowerCase();return e.includes("山手")?"bg-green-500":e.includes("中央")&&e.includes("快速")?"bg-orange-500":e.includes("中央")&&e.includes("総武")?"bg-yellow-500":e.includes("京浜東北")?"bg-sky-500":e.includes("埼京")?"bg-emerald-600":e.includes("湘南新宿")?"bg-orange-600":e.includes("総武快速")||e.includes("総武線快速")?"bg-blue-600":e.includes("常磐")?"bg-cyan-500":e.includes("東海道")?"bg-orange-400":e.includes("横須賀")?"bg-blue-500":e.includes("武蔵野")?"bg-orange-600":e.includes("京葉")?"bg-red-500":e.includes("銀座")?"bg-orange-400":e.includes("丸ノ内")?"bg-red-500":e.includes("日比谷")?"bg-gray-400":e.includes("東西")?"bg-sky-400":e.includes("千代田")?"bg-green-600":e.includes("有楽町")?"bg-yellow-600":e.includes("半蔵門")?"bg-purple-500":e.includes("南北")?"bg-emerald-400":e.includes("副都心")?"bg-amber-700":e.includes("浅草")?"bg-rose-400":e.includes("三田")?"bg-blue-700":e.includes("新宿")?"bg-lime-500":e.includes("大江戸")?"bg-pink-600":"bg-slate-500"}function I(a){document.getElementById("loading-state").classList.add("hidden"),document.getElementById("result-state").classList.add("hidden"),document.getElementById("error-state").classList.remove("hidden"),document.getElementById("error-message").textContent=a,document.getElementById("route-subheader").textContent=""}function T(a,e=null,l=[]){const t=document.getElementById("route-timeline");t&&(t.innerHTML="",a.forEach((s,i)=>{const d=i===a.length-1;let m=S(s.railway||"");if(e&&e.reasons&&s.railway_id){const o=s.railway_id.split(".").pop();e.reasons.find(v=>v.railway===o)&&(e.level==="HIGH"?m="bg-red-500":e.level==="MEDIUM"&&(m="bg-amber-500"))}const u=document.createElement("div");u.className="flex";let p="";i===0?p=`<div class="text-xl font-bold text-slate-800">${s.departure_time}</div>`:p=`
                <div class="text-sm text-slate-500 leading-tight">${a[i-1].arrival_time}着</div>
                <div class="text-base font-bold text-slate-800 leading-tight">${s.departure_time}発</div>
            `;let f="";i===0?f='<div class="w-6 h-6 bg-slate-800 text-white rounded-sm font-bold text-xs flex items-center justify-center z-10 shadow-md">発</div>':f='<div class="w-4 h-4 bg-white border-2 border-slate-400 rounded-full z-10 shadow-sm"></div>',u.innerHTML=`
            <div class="w-20 text-right pr-4 flex flex-col justify-center gap-0.5">
                ${p}
            </div>
            <div class="w-8 flex flex-col items-center relative">
                 ${f}
                 <div class="w-1.5 ${m} h-full absolute top-4 z-0 opacity-80"></div>
            </div>
            <div class="flex-1 pl-2 py-1 items-center flex">
                <span class="text-lg font-bold text-slate-800 border-b border-slate-200 pb-1 w-full">${s.from}</span>
            </div>
        `,t.appendChild(u);const r=s.train_number?`<span class="text-slate-500 text-sm ml-2">${s.train_type} ${s.train_number}</span>`:s.train_type?`<span class="text-slate-500 text-sm ml-2">${s.train_type}</span>`:"",n=document.createElement("div");if(n.className="flex min-h-[4rem]",n.innerHTML=`
            <div class="w-20"></div> <!-- Time Spacer -->
            <div class="w-8 flex flex-col items-center relative">
                 <div class="w-1.5 ${m} h-full absolute top-0 bottom-0 z-0 opacity-80"></div>
            </div>
            <div class="flex-1 pl-2 py-3 flex flex-col justify-center">
                 <div class="flex items-center">
                    <span class="text-2xl mr-2">🚃</span>
                    <div>
                        <div class="font-bold text-slate-700 text-sm">${s.railway}</div>
                        ${r}
                    </div>
                 </div>
                 ${s.note?`<div class="text-xs text-amber-600 mt-1 ml-8 font-medium">⚠️ ${s.note}</div>`:""}
            </div>
        `,t.appendChild(n),d){const o=document.createElement("div");o.className="flex",o.innerHTML=`
                 <div class="w-20 text-right pr-4 flex flex-col justify-center">
                    <div class="text-xl font-bold text-slate-800">${s.arrival_time}</div>
                </div>
                <div class="w-8 flex flex-col items-center relative">
                     <div class="w-1.5 ${m} h-3 absolute top-0 z-0 opacity-80"></div> <!-- Connect from above -->
                     <div class="w-6 h-6 bg-slate-600 text-white rounded-sm font-bold text-xs flex items-center justify-center z-10 mt-2 shadow-md">着</div>
                </div>
                <div class="flex-1 pl-2 py-2 items-center flex">
                    <span class="text-lg font-bold text-slate-800 border-b border-slate-200 pb-1 w-full">${s.to}</span>
                </div>
            `,t.appendChild(o)}}))}let k=[];document.addEventListener("DOMContentLoaded",async()=>{const a=new URLSearchParams(window.location.search),e=a.get("from"),l=a.get("to"),t=a.get("time"),s=a.get("day_type");if(!e||!l||!t){I("出発駅、到着駅、時刻を指定してください。");return}document.getElementById("route-header").textContent=`${e} → ${l}`,document.getElementById("route-subheader").textContent=`${t} 以降の電車を検索中...`,await _(e,l,t,s),document.getElementById("back-to-list").addEventListener("click",()=>{B()})});async function _(a,e,l,t=null){try{const s=await H(a,e,l,t);if(!s.routes||s.routes.length===0){I("ルートが見つかりませんでした。");return}k=s.routes,j(),document.getElementById("loading-state").classList.add("hidden"),document.getElementById("result-state").classList.remove("hidden");const d=new URLSearchParams(window.location.search).get("route");d!==null&&k[d]?E(parseInt(d),!1):B(!1)}catch(s){s.message&&I(s.message)}}function B(a=!0){if(document.getElementById("route-list-view").classList.remove("hidden"),document.getElementById("route-detail-view").classList.add("hidden"),document.getElementById("global-back-link").classList.remove("hidden"),document.getElementById("main-header").classList.remove("hidden"),document.getElementById("route-header").textContent="検索結果",a){const e=new URL(window.location);e.searchParams.delete("route"),window.history.replaceState({},"",e)}}function E(a,e=!0){if(document.getElementById("route-list-view").classList.add("hidden"),document.getElementById("route-detail-view").classList.remove("hidden"),document.getElementById("global-back-link").classList.add("hidden"),document.getElementById("main-header").classList.add("hidden"),N(a),e){const l=new URL(window.location);l.searchParams.set("route",a),console.log("Debug: Updating URL state to route:",a,l.toString()),window.history.replaceState({},"",l.toString())}}function j(){const a=document.getElementById("route-list-container");a.innerHTML="";let e=-1,l=-1;k.forEach((t,s)=>{const i=t.scores?.speed||0,d=t.scores?.comfort||0,m=t.scores?.reliability||0,u=t.scores?.cost||0,p=i+d+m+u;p>l&&(l=p,e=s)}),k.forEach((t,s)=>{const i=t.segments||[],d=i.length>0&&i[0].departure_time?i[0].departure_time:"--:--",u=(i.length>0?i[i.length-1]:null)?.arrival_time||"--:--",p=t.transfers||0,f=t.risk||{level:"LOW"};let r="";if(d!=="--:--"&&u!=="--:--"){const[g,x]=d.split(":").map(Number),[b,w]=u.split(":").map(Number);let $=b*60+w-(g*60+x);$<0&&($+=1440);const y=Math.floor($/60),L=$%60;r=y>0?`${y}時間${L}分`:`${L}分`}const n=document.createElement("div");let o="bg-white hover:bg-slate-50 border-slate-200 shadow-sm";f.level==="HIGH"?o="bg-red-50 hover:bg-red-100 border-red-200 shadow-sm":f.level==="MEDIUM"&&(o="bg-amber-50 hover:bg-amber-100 border-amber-200 shadow-sm");const c=s===e&&l>0;c&&(o+=" ring-2 ring-emerald-500 ring-offset-2"),n.className=`p-6 md:p-8 rounded-xl border transition-all cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-6 md:gap-0 ${o} focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 relative`,n.setAttribute("role","button"),n.setAttribute("tabindex","0"),n.setAttribute("aria-label",`${d}発 ${u}着 乗換${p}回 ${r}`);let v="";f.level==="HIGH"?v='<span class="px-2 py-1 rounded text-xs font-bold bg-red-100 text-red-700 border border-red-200">遅延リスク高</span>':f.level==="MEDIUM"?v='<span class="px-2 py-1 rounded text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200">遅延注意</span>':v='<span class="px-2 py-1 rounded text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">平常運行</span>';const h=c?`<div class="absolute -top-3 left-6 bg-yellow-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-md flex items-center gap-1">
                <span>⭐️</span> ベストバランス
            </div>`:"";n.innerHTML=`
            ${h}
            <div class="w-full md:w-auto">
                <div class="flex items-center gap-3 mb-1">
                    <span class="text-2xl font-bold text-slate-800">${u} 着</span>
                    <span class="text-sm text-slate-500 hidden md:inline">(${d} 発)</span>
                    ${r?`<span class="text-sm font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">${r}</span>`:""}
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
        `,n.addEventListener("click",()=>{E(s)}),n.addEventListener("keydown",g=>{(g.key==="Enter"||g.key===" ")&&(g.preventDefault(),E(s))}),a.appendChild(n)})}function N(a){const e=k[a];if(!e)return;const l=e.segments||[],t=l.length>0&&l[0].departure_time?l[0].departure_time:"--:--",i=(l.length>0?l[l.length-1]:null)?.arrival_time||"--:--";let d="--分";if(t!=="--:--"&&i!=="--:--"&&t&&i){const[o,c]=t.split(":").map(Number),[v,h]=i.split(":").map(Number);let g=v*60+h-(o*60+c);g<0&&(g+=1440);const x=Math.floor(g/60),b=g%60;d=x>0?`${x}時間${b}分`:`${b}分`}document.getElementById("first-departure").textContent=t,document.getElementById("arrival-time").textContent=i,document.getElementById("transfer-count").textContent=`乗換 ${e.transfers||0}回`;const m=document.getElementById("total-fare");m&&(m.textContent=e.fare?`¥${e.fare.toLocaleString()}`:"---"),document.getElementById("total-duration").textContent=d,e.fare&&(document.getElementById("total-duration").textContent+=` / ¥${e.fare.toLocaleString()}`),document.getElementById("route-header").textContent=`${t} 発 → ${i} 着`;const u=document.getElementById("route-summary-container"),p=document.getElementById("arrival-time"),f=e.risk&&e.risk.level?e.risk.level:"LOW",r={HIGH:{container:"bg-gradient-to-r from-red-50 to-rose-50 border-red-200",arrivalText:"text-red-600"},MEDIUM:{container:"bg-gradient-to-r from-amber-50 to-orange-50 border-amber-200",arrivalText:"text-amber-600"},LOW:{container:"bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-200",arrivalText:"text-emerald-600"}},n=r[f]||r.LOW;u.className=`rounded-2xl p-5 mb-6 border ${n.container}`,p.className=`text-4xl font-bold leading-none ${n.arrivalText}`,D(e),T(l,e.risk,e.delay_warnings),U(e)}function D(a){const e=document.getElementById("delay-warnings");if(!e)return;e.innerHTML="";const l=a.delay_warnings||[],t=a.risk||{level:"LOW",reasons:[]},s=a.crowd||{level:"UNKNOWN",score:0,details:[]},i=a.venue_warnings||{transfer_warnings:[],passing_info:[]};function d(r,n,o,c,v,h=!1){const g={red:{bg:"bg-red-50",border:"border-red-200",header:"text-red-800",headerBg:"hover:bg-red-100"},amber:{bg:"bg-amber-50",border:"border-amber-200",header:"text-amber-800",headerBg:"hover:bg-amber-100"},orange:{bg:"bg-orange-50",border:"border-orange-200",header:"text-orange-800",headerBg:"hover:bg-orange-100"},blue:{bg:"bg-blue-50",border:"border-blue-200",header:"text-blue-800",headerBg:"hover:bg-blue-100"},emerald:{bg:"bg-emerald-50",border:"border-emerald-200",header:"text-emerald-800",headerBg:"hover:bg-emerald-100"},slate:{bg:"bg-slate-50",border:"border-slate-200",header:"text-slate-700",headerBg:"hover:bg-slate-100"}},x=g[c]||g.slate,b=document.createElement("div");b.className=`${x.bg} ${x.border} border rounded-xl overflow-hidden mb-2`,b.innerHTML=`
            <button 
                class="w-full flex items-center justify-between p-4 ${x.headerBg} transition-colors"
                aria-expanded="${h}"
                aria-controls="accordion-content-${r}"
                id="accordion-btn-${r}"
            >
                <div class="flex items-center gap-2">
                    <span class="text-xl">${n}</span>
                    <span class="font-bold ${x.header}">${o}</span>
                </div>
                <svg class="w-5 h-5 ${x.header} transition-transform duration-200 ${h?"rotate-180":""}" id="accordion-icon-${r}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            <div id="accordion-content-${r}" class="${h?"":"hidden"} px-4 pb-4">
                ${v}
            </div>
        `;const w=b.querySelector(`#accordion-btn-${r}`);return w.addEventListener("click",()=>{const y=!(w.getAttribute("aria-expanded")==="true");w.setAttribute("aria-expanded",y);const L=b.querySelector(`#accordion-icon-${r}`),M=b.querySelector(`#accordion-content-${r}`);y?(L.classList.add("rotate-180"),M.classList.remove("hidden")):(L.classList.remove("rotate-180"),M.classList.add("hidden"))}),b}let m=!1;const u=(r,n,o="slate")=>`
        <div class="bg-white/60 rounded-lg p-3 border border-${o}-100">
            <p class="font-medium text-${o}-800">${r}</p>
            <p class="text-xs text-slate-500 mt-1">${n}</p>
        </div>
    `,p=(r,n)=>`
        <div class="bg-white/60 rounded-lg p-3 border border-emerald-100 flex items-center gap-3">
            <div class="w-8 h-8 bg-emerald-100 rounded-full flex items-center justify-center shrink-0">
                <svg class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
            </div>
            <div>
                <p class="font-medium text-emerald-800">${r}</p>
                <p class="text-xs text-slate-500">${n}</p>
            </div>
        </div>
    `;if(m=!0,l.length>0){const r=l.map(n=>{let o="";if(n.timestamp)try{const c=new Date(n.timestamp);o=`${c.getHours().toString().padStart(2,"0")}:${c.getMinutes().toString().padStart(2,"0")} 時点`}catch{}return`
                <div class="bg-white/60 rounded-lg p-3 border border-red-100 mb-2 last:mb-0">
                    <div class="flex items-center justify-between">
                        <a href="line.html?line=${encodeURIComponent(n.railway_name_en||n.railway)}" class="font-medium text-red-800 hover:underline hover:text-red-900">${n.railway}</a>
                        ${o?`<span class="text-xs text-red-400">${o}</span>`:""}
                    </div>
                    <p class="text-xs text-slate-500 mt-1">${n.reason||"遅延が発生しています"}</p>
                </div>
            `}).join("");e.appendChild(d("realtime","📡",`運行情報 (${l.length}件の遅延)`,"red",r,!0))}else{const r=p("平常運行","現在、すべての路線で遅延は発生していません");e.appendChild(d("realtime","📡","運行情報","emerald",r,!1))}{m=!0;const r=t.level==="HIGH"?"red":t.level==="MEDIUM"?"amber":"emerald",n=t.level==="HIGH"?"高リスク":t.level==="MEDIUM"?"注意":"低リスク";let o="";t.reasons.length>0?o=`
                <p class="text-xs text-slate-500 mb-2">過去の遅延データに基づく予測:</p>
                <div class="space-y-2">
                    ${t.reasons.map(c=>{const v=c.id?`<a href="line.html?line=${encodeURIComponent(c.id)}" class="hover:underline hover:opacity-80">${c.railway}</a>`:c.railway||"";return u(v,c.rate||c.display||"",r)}).join("")}
                </div>
            `:o=p("リスクなし","過去の遅延データに問題は見つかりませんでした"),e.appendChild(d("risk","📊",`遅延リスク: ${n}`,r,o,t.level!=="LOW"))}const f=[...i.transfer_warnings,...i.passing_info];if(f.length>0){m=!0;let r="";i.transfer_warnings.length>0&&(r+=`
                <p class="text-xs text-amber-600 font-medium mb-2">乗換駅周辺</p>
                <div class="space-y-2 mb-3">
                    ${i.transfer_warnings.map(n=>{const c=`<a href="${n.url||`https://www.google.com/search?q=${encodeURIComponent(n.venue+" イベント 公式")}`}" target="_blank" rel="noopener noreferrer" class="underline hover:text-amber-600 decoration-amber-400 underline-offset-2">${n.venue}</a>`;return u(`${n.station}駅 → ${c}`,`収容人数: ${n.capacity.toLocaleString()}人 / ${n.note}`,"amber")}).join("")}
                </div>
            `),i.passing_info.length>0&&(r+=`
                <p class="text-xs text-slate-500 mb-2">通過駅周辺</p>
                <p class="text-sm text-slate-600">${i.passing_info.map(n=>`${n.station}(${n.venues.join(", ")})`).join(" / ")}</p>
            `),e.appendChild(d("venue","📍",`周辺イベント (${f.length}件)`,"amber",r,!1))}if(s.level!=="UNKNOWN"&&s.details&&s.details.length>0){m=!0;const r=s.level==="HIGH"?"amber":"slate",n=s.level==="HIGH"?"混雑":s.level==="MEDIUM"?"普通":"空いている",o=`
            <div class="bg-white/60 rounded-lg p-3 border border-${r}-100">
                <div class="flex items-center gap-3 mb-2">
                    <div class="text-xl font-bold text-slate-800">${s.score.toLocaleString()}</div>
                    <div class="text-xs text-slate-500">人/日 (平均)</div>
                    <span class="ml-auto px-2 py-1 text-xs font-medium bg-${r}-100 text-${r}-700 rounded-full">${n}</span>
                </div>
                <p class="text-xs text-slate-500">経路: ${s.details.join(" → ")}</p>
            </div>
        `;e.appendChild(d("crowd","📊",`経路の混雑度: ${n}`,r,o,!1))}if(!m){const r=document.createElement("div");r.className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 text-center",r.innerHTML=`
            <div class="flex flex-col items-center gap-2">
                <div class="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
                    <svg class="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                </div>
                <p class="text-emerald-800 font-medium">すべての路線が平常運行中</p>
                <p class="text-emerald-600 text-xs">遅延情報・混雑情報はありません</p>
            </div>
        `,e.appendChild(r)}}function U(a){const e=document.getElementById("ai-diagnose-btn"),l=document.getElementById("ai-diagnosis-result");if(!e||!l)return;l.classList.add("hidden"),l.innerHTML="",e.disabled=!1,e.innerHTML=`
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        診断開始
    `;const t=e.cloneNode(!0);e.parentNode.replaceChild(t,e),t.addEventListener("click",async()=>{t.disabled=!0,t.innerHTML=`
            <svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            診断中...
        `,l.classList.remove("hidden"),l.innerHTML=`
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
        `;try{const s=await C(a);R(l,s),t.innerHTML=`
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                再診断
            `,t.disabled=!1}catch(s){l.innerHTML=`
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
            `,t.disabled=!1}})}function R(a,e){const l=e.diagnosis||"診断結果がありません";l.split(`
`).filter(t=>t.trim()),a.innerHTML=`
        <div class="mt-4 px-1">
            <div class="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100">
                <span class="text-lg">✨</span>
                <span class="font-bold text-slate-700">AIアドバイス</span>
                <span class="ml-auto text-xs text-slate-400">${e.model||"AI"}</span>
            </div>
            <div class="prose prose-sm max-w-none text-slate-600">
                 ${A(l)}
            </div>
        </div>
    `}function A(a){return a.replace(/^### (.+)(?:\n|$)/gm,'<h4 class="font-bold text-slate-800 mt-3 mb-1">$1</h4>').replace(/^## (.+)(?:\n|$)/gm,'<h3 class="font-bold text-slate-900 mt-4 mb-2">$1</h3>').replace(/^# (.+)(?:\n|$)/gm,'<h2 class="font-bold text-slate-900 text-lg mt-4 mb-2">$1</h2>').replace(/^\d+\. (.+)(?:\n|$)/gm,'<p class="font-semibold text-slate-800">$1</p>').replace(/^[-•] (.+)(?:\n|$)/gm,'<p class="pl-4 text-slate-700 before:content-["•"] before:mr-2 before:text-slate-400">$1</p>').replace(/\*\*(.+?)\*\*/g,'<strong class="text-slate-800">$1</strong>').replace(/\n/g,"<br>")}
