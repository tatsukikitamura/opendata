import{s as B,d as H}from"./api-DVUU3mqz.js";/* empty css              */function C(n){const e=n.toLowerCase();return e.includes("山手")?"bg-green-500":e.includes("中央")&&e.includes("快速")?"bg-orange-500":e.includes("中央")&&e.includes("総武")?"bg-yellow-500":e.includes("京浜東北")?"bg-sky-500":e.includes("埼京")?"bg-emerald-600":e.includes("湘南新宿")?"bg-orange-600":e.includes("総武快速")||e.includes("総武線快速")?"bg-blue-600":e.includes("常磐")?"bg-cyan-500":e.includes("東海道")?"bg-orange-400":e.includes("横須賀")?"bg-blue-500":e.includes("武蔵野")?"bg-orange-600":e.includes("京葉")?"bg-red-500":e.includes("銀座")?"bg-orange-400":e.includes("丸ノ内")?"bg-red-500":e.includes("日比谷")?"bg-gray-400":e.includes("東西")?"bg-sky-400":e.includes("千代田")?"bg-green-600":e.includes("有楽町")?"bg-yellow-600":e.includes("半蔵門")?"bg-purple-500":e.includes("南北")?"bg-emerald-400":e.includes("副都心")?"bg-amber-700":e.includes("浅草")?"bg-rose-400":e.includes("三田")?"bg-blue-700":e.includes("新宿")?"bg-lime-500":e.includes("大江戸")?"bg-pink-600":"bg-slate-500"}function y(n){document.getElementById("loading-state").classList.add("hidden"),document.getElementById("result-state").classList.add("hidden"),document.getElementById("error-state").classList.remove("hidden"),document.getElementById("error-message").textContent=n,document.getElementById("route-subheader").textContent=""}function T(n,e=null){const s=document.getElementById("route-timeline");s&&(s.innerHTML="",n.forEach((t,i)=>{const d=i===n.length-1;let c=C(t.railway||"");if(e&&e.reasons&&t.railway_id){const l=t.railway_id.split(".").pop();e.reasons.find(g=>g.railway===l)&&(e.level==="HIGH"?c="bg-red-500":e.level==="MEDIUM"&&(c="bg-amber-500"))}const m=document.createElement("div");m.className="flex";let u="";i===0?u=`<div class="text-xl font-bold text-slate-800">${t.departure_time}</div>`:u=`
                <div class="text-sm text-slate-500 leading-tight">${n[i-1].arrival_time}着</div>
                <div class="text-base font-bold text-slate-800 leading-tight">${t.departure_time}発</div>
            `;let r="";i===0?r='<div class="w-6 h-6 bg-slate-800 text-white rounded-sm font-bold text-xs flex items-center justify-center z-10 shadow-md">発</div>':r='<div class="w-4 h-4 bg-white border-2 border-slate-400 rounded-full z-10 shadow-sm"></div>',m.innerHTML=`
            <div class="w-20 text-right pr-4 flex flex-col justify-center gap-0.5">
                ${u}
            </div>
            <div class="w-8 flex flex-col items-center relative">
                 ${r}
                 <div class="w-1.5 ${c} h-full absolute top-4 z-0 opacity-80"></div>
            </div>
            <div class="flex-1 pl-2 py-1 items-center flex">
                <span class="text-lg font-bold text-slate-800 border-b border-slate-200 pb-1 w-full">${t.from}</span>
            </div>
        `,s.appendChild(m);const a=t.train_number?`<span class="text-slate-500 text-sm ml-2">${t.train_type} ${t.train_number}</span>`:t.train_type?`<span class="text-slate-500 text-sm ml-2">${t.train_type}</span>`:"",o=document.createElement("div");if(o.className="flex min-h-[4rem]",o.innerHTML=`
            <div class="w-20"></div> <!-- Time Spacer -->
            <div class="w-8 flex flex-col items-center relative">
                 <div class="w-1.5 ${c} h-full absolute top-0 bottom-0 z-0 opacity-80"></div>
            </div>
            <div class="flex-1 pl-2 py-3 flex flex-col justify-center">
                 <div class="flex items-center">
                    <span class="text-2xl mr-2">🚃</span>
                    <div>
                        <div class="font-bold text-slate-700 text-sm">${t.railway}</div>
                        ${a}
                    </div>
                 </div>
                 ${t.note?`<div class="text-xs text-amber-600 mt-1 ml-8 font-medium">⚠️ ${t.note}</div>`:""}
            </div>
        `,s.appendChild(o),d){const l=document.createElement("div");l.className="flex",l.innerHTML=`
                 <div class="w-20 text-right pr-4 flex flex-col justify-center">
                    <div class="text-xl font-bold text-slate-800">${t.arrival_time}</div>
                </div>
                <div class="w-8 flex flex-col items-center relative">
                     <div class="w-1.5 ${c} h-3 absolute top-0 z-0 opacity-80"></div> <!-- Connect from above -->
                     <div class="w-6 h-6 bg-slate-600 text-white rounded-sm font-bold text-xs flex items-center justify-center z-10 mt-2 shadow-md">着</div>
                </div>
                <div class="flex-1 pl-2 py-2 items-center flex">
                    <span class="text-lg font-bold text-slate-800 border-b border-slate-200 pb-1 w-full">${t.to}</span>
                </div>
            `,s.appendChild(l)}}))}let $=[];document.addEventListener("DOMContentLoaded",async()=>{const n=new URLSearchParams(window.location.search),e=n.get("from"),s=n.get("to"),t=n.get("time");if(!e||!s||!t){y("出発駅、到着駅、時刻を指定してください。");return}document.getElementById("route-header").textContent=`${e} → ${s}`,document.getElementById("route-subheader").textContent=`${t} 以降の電車を検索中...`,await _(e,s,t),document.getElementById("back-to-list").addEventListener("click",()=>{I()})});async function _(n,e,s){try{const t=await B(n,e,s);if(!t.routes||t.routes.length===0){y("ルートが見つかりませんでした。");return}$=t.routes,j(),document.getElementById("loading-state").classList.add("hidden"),document.getElementById("result-state").classList.remove("hidden"),I()}catch(t){t.message&&y(t.message)}}function I(){document.getElementById("route-list-view").classList.remove("hidden"),document.getElementById("route-detail-view").classList.add("hidden"),document.getElementById("global-back-link").classList.remove("hidden"),document.getElementById("main-header").classList.remove("hidden"),document.getElementById("route-header").textContent="検索結果"}function k(n){document.getElementById("route-list-view").classList.add("hidden"),document.getElementById("route-detail-view").classList.remove("hidden"),document.getElementById("global-back-link").classList.add("hidden"),document.getElementById("main-header").classList.add("hidden"),S(n)}function j(){const n=document.getElementById("route-list-container");n.innerHTML="";let e=-1,s=-1;$.forEach((t,i)=>{const d=t.scores?.speed||0,c=t.scores?.comfort||0,m=t.scores?.reliability||0,u=t.scores?.cost||0,r=d+c+m+u;r>s&&(s=r,e=i)}),$.forEach((t,i)=>{const d=t.segments||[],c=d.length>0&&d[0].departure_time?d[0].departure_time:"--:--",u=(d.length>0?d[d.length-1]:null)?.arrival_time||"--:--",r=t.transfers||0,a=t.risk||{level:"LOW"};let o="";if(c!=="--:--"&&u!=="--:--"){const[p,x]=c.split(":").map(Number),[h,M]=u.split(":").map(Number);let w=h*60+M-(p*60+x);w<0&&(w+=1440);const L=Math.floor(w/60),E=w%60;o=L>0?`${L}時間${E}分`:`${E}分`}const l=document.createElement("div");let f="bg-white hover:bg-slate-50 border-slate-200 shadow-sm";a.level==="HIGH"?f="bg-red-50 hover:bg-red-100 border-red-200 shadow-sm":a.level==="MEDIUM"&&(f="bg-amber-50 hover:bg-amber-100 border-amber-200 shadow-sm");const g=i===e&&s>0;g&&(f+=" ring-2 ring-emerald-500 ring-offset-2"),l.className=`p-8 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${f} focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 relative`,l.setAttribute("role","button"),l.setAttribute("tabindex","0"),l.setAttribute("aria-label",`${c}発 ${u}着 乗換${r}回 ${o}`);let b="";a.level==="HIGH"?b='<span class="px-2 py-1 rounded text-xs font-bold bg-red-100 text-red-700 border border-red-200">遅延リスク高</span>':a.level==="MEDIUM"?b='<span class="px-2 py-1 rounded text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200">遅延注意</span>':b='<span class="px-2 py-1 rounded text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">平常運行</span>';const v=g?`<div class="absolute -top-3 left-6 bg-yellow-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-md flex items-center gap-1">
                <span>⭐️</span> ベストバランス
            </div>`:"";l.innerHTML=`
            ${v}
            <div>
                <div class="flex items-center gap-3 mb-1">
                    <span class="text-2xl font-bold text-slate-800">${u} 着</span>
                    <span class="text-sm text-slate-500">(${c} 発)</span>
                    ${o?`<span class="text-sm font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">${o}</span>`:""}
                </div>
                <div class="text-sm text-slate-500 mt-2">
                    乗換 ${r}回
                    ${t.fare?`<span class="ml-3 text-slate-800 font-bold">¥${t.fare.toLocaleString()}</span>`:""}
                </div>
            </div>
            <div>
                <!-- 4-Axis Scores -->
                <div class="mt-3 text-xs space-y-1 w-48">
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
            <div class="text-right">
                ${b}
                <div class="text-xs text-slate-400 mt-2 flex items-center justify-end gap-1">
                    詳細を見る
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                </div>
            </div>
        `,l.addEventListener("click",()=>{k(i)}),l.addEventListener("keydown",p=>{(p.key==="Enter"||p.key===" ")&&(p.preventDefault(),k(i))}),n.appendChild(l)})}function S(n){const e=$[n];if(!e)return;const s=e.segments||[],t=s.length>0&&s[0].departure_time?s[0].departure_time:"--:--",d=(s.length>0?s[s.length-1]:null)?.arrival_time||"--:--";let c="--分";if(t!=="--:--"&&d!=="--:--"&&t&&d){const[f,g]=t.split(":").map(Number),[b,v]=d.split(":").map(Number);let p=b*60+v-(f*60+g);p<0&&(p+=1440);const x=Math.floor(p/60),h=p%60;c=x>0?`${x}時間${h}分`:`${h}分`}document.getElementById("first-departure").textContent=t,document.getElementById("arrival-time").textContent=d,document.getElementById("transfer-count").textContent=`乗換 ${e.transfers||0}回`;const m=document.getElementById("total-fare");m&&(m.textContent=e.fare?`¥${e.fare.toLocaleString()}`:"---"),document.getElementById("total-duration").textContent=c,e.fare&&(document.getElementById("total-duration").textContent+=` / ¥${e.fare.toLocaleString()}`),document.getElementById("route-header").textContent=`${t} 発 → ${d} 着`;const u=document.getElementById("route-summary-container"),r=document.getElementById("arrival-time"),a=e.risk&&e.risk.level?e.risk.level:"LOW",o={HIGH:{container:"bg-gradient-to-r from-red-50 to-rose-50 border-red-200",arrivalText:"text-red-600"},MEDIUM:{container:"bg-gradient-to-r from-amber-50 to-orange-50 border-amber-200",arrivalText:"text-amber-600"},LOW:{container:"bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-200",arrivalText:"text-emerald-600"}},l=o[a]||o.LOW;u.className=`rounded-2xl p-5 mb-6 border ${l.container}`,r.className=`text-4xl font-bold leading-none ${l.arrivalText}`,N(e),T(s,e.risk),D(e)}function N(n){const e=document.getElementById("delay-warnings");if(!e)return;e.innerHTML="";const s=n.delay_warnings||[],t=n.risk||{level:"LOW",reasons:[]},i=n.crowd||{level:"UNKNOWN",score:0,details:[]},d=n.venue_warnings||{transfer_warnings:[],passing_info:[]};function c(r,a,o,l,f,g=!1){const b={red:{bg:"bg-red-50",border:"border-red-200",header:"text-red-800",headerBg:"hover:bg-red-100"},amber:{bg:"bg-amber-50",border:"border-amber-200",header:"text-amber-800",headerBg:"hover:bg-amber-100"},orange:{bg:"bg-orange-50",border:"border-orange-200",header:"text-orange-800",headerBg:"hover:bg-orange-100"},blue:{bg:"bg-blue-50",border:"border-blue-200",header:"text-blue-800",headerBg:"hover:bg-blue-100"},emerald:{bg:"bg-emerald-50",border:"border-emerald-200",header:"text-emerald-800",headerBg:"hover:bg-emerald-100"},slate:{bg:"bg-slate-50",border:"border-slate-200",header:"text-slate-700",headerBg:"hover:bg-slate-100"}},v=b[l]||b.slate,p=document.createElement("div");return p.className=`${v.bg} ${v.border} border rounded-xl overflow-hidden mb-2`,p.innerHTML=`
            <button 
                class="w-full flex items-center justify-between p-4 ${v.headerBg} transition-colors"
                aria-expanded="${g}"
                aria-controls="accordion-content-${r}"
                onclick="this.setAttribute('aria-expanded', this.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'); document.getElementById('accordion-content-${r}').classList.toggle('hidden');"
            >
                <div class="flex items-center gap-2">
                    <span class="text-xl">${a}</span>
                    <span class="font-bold ${v.header}">${o}</span>
                </div>
                <svg class="w-5 h-5 ${v.header} transition-transform" style="transform: rotate(${g?"180deg":"0deg"});" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            <div id="accordion-content-${r}" class="${g?"":"hidden"} px-4 pb-4">
                ${f}
            </div>
        `,p}let m=!1;if(s.length>0){m=!0;const r=s.map(a=>{let o="";if(a.timestamp)try{const l=new Date(a.timestamp);o=`${l.getHours().toString().padStart(2,"0")}:${l.getMinutes().toString().padStart(2,"0")} 時点`}catch{}return`
                <div class="bg-white/60 rounded-lg p-3 border border-red-100 mb-2 last:mb-0">
                    <div class="flex items-center justify-between">
                        <p class="text-red-800 font-medium">${a.railway}</p>
                        ${o?`<span class="text-xs text-red-400">${o}</span>`:""}
                    </div>
                    <p class="text-red-700/80 text-sm mt-1">${a.reason||"遅延が発生しています"}</p>
                </div>
            `}).join("");e.appendChild(c("realtime","🚨",`リアルタイム遅延 (${s.length}件)`,"red",r,!0))}{m=!0;const r=t.level==="HIGH"?"red":t.level==="MEDIUM"?"amber":"emerald",a=t.level==="HIGH"?"高い":t.level==="MEDIUM"?"中程度":"低い";let o="";t.reasons.length>0?o=`
                <p class="text-xs text-slate-500 mb-2">過去の遅延実績データに基づく予測:</p>
                <div class="space-y-2">
                    ${t.reasons.map(l=>`
                        <div class="bg-white/60 rounded-lg p-3 border border-current/10">
                            <p class="font-medium text-sm">${l.railway||""}</p>
                            <p class="text-xs text-slate-600 mt-1">${l.rate||l.display||""}</p>
                        </div>
                    `).join("")}
                </div>
            `:o=`
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
            `,e.appendChild(c("risk","⚠️",`遅延リスク: ${a}`,r,o,t.level!=="LOW"))}const u=[...d.transfer_warnings,...d.passing_info];if(u.length>0){m=!0;let r="";d.transfer_warnings.length>0&&(r+=`
                <p class="text-xs text-orange-600 font-medium mb-2">⚠️ 乗換駅周辺</p>
                ${d.transfer_warnings.map(a=>`
                    <div class="bg-white/60 rounded-lg p-3 border border-orange-100 mb-2">
                        <p class="font-medium text-orange-900">📍 ${a.station}駅 → ${a.venue}</p>
                        <p class="text-xs text-slate-500 mt-1">収容人数: ${a.capacity.toLocaleString()}人 / ${a.note}</p>
                    </div>
                `).join("")}
            `),d.passing_info.length>0&&(r+=`
                <p class="text-xs text-slate-500 mt-3 mb-2">ℹ️ 通過駅周辺</p>
                <p class="text-sm text-slate-600">${d.passing_info.map(a=>`${a.station}(${a.venues.join(", ")})`).join(" / ")}</p>
            `),e.appendChild(c("venue","🎪",`イベント情報 (${u.length}件)`,"orange",r,!1))}if(i.level!=="UNKNOWN"&&i.details&&i.details.length>0){m=!0;const r=i.level==="HIGH"?"大都市圏":i.level==="MEDIUM"?"中規模":"郊外",a=`
            <div class="flex items-center gap-3 mb-3">
                <div class="text-2xl font-bold text-blue-800">${i.score.toLocaleString()}</div>
                <div class="text-xs text-slate-500">人/日<br>(平均乗降客数)</div>
                <span class="ml-auto px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">${r}</span>
            </div>
            <div class="text-xs text-slate-500">
                <p class="font-medium mb-1">経由駅の規模:</p>
                <p>${i.details.join(", ")}</p>
            </div>
        `;e.appendChild(c("crowd","📊","駅混雑度","blue",a,!1))}if(!m){const r=document.createElement("div");r.className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 text-center",r.innerHTML=`
            <div class="flex flex-col items-center gap-2">
                <div class="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
                    <svg class="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                </div>
                <p class="text-emerald-800 font-medium">すべての路線が平常運行中</p>
                <p class="text-emerald-600 text-xs">遅延情報・混雑情報はありません</p>
            </div>
        `,e.appendChild(r)}}function D(n){const e=document.getElementById("ai-diagnose-btn"),s=document.getElementById("ai-diagnosis-result");if(!e||!s)return;s.classList.add("hidden"),s.innerHTML="",e.disabled=!1,e.innerHTML=`
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        診断開始
    `;const t=e.cloneNode(!0);e.parentNode.replaceChild(t,e),t.addEventListener("click",async()=>{t.disabled=!0,t.innerHTML=`
            <svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            診断中...
        `,s.classList.remove("hidden"),s.innerHTML=`
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
        `;try{const i=await H(n);A(s,i),t.innerHTML=`
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                再診断
            `,t.disabled=!1}catch(i){s.innerHTML=`
                <div class="bg-red-50 border border-red-200 rounded-xl p-4">
                    <div class="flex items-center gap-2 text-red-700">
                        <span class="text-xl">⚠️</span>
                        <span class="font-medium">診断エラー</span>
                    </div>
                    <p class="text-red-600 text-sm mt-2">${i.message||"AI診断に失敗しました。しばらく経ってから再度お試しください。"}</p>
                </div>
            `,t.innerHTML=`
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                再試行
            `,t.disabled=!1}})}function A(n,e){const s=e.diagnosis||"診断結果がありません";s.split(`
`).filter(t=>t.trim()),n.innerHTML=`
        <div class="mt-4 px-1">
            <div class="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100">
                <span class="text-lg">✨</span>
                <span class="font-bold text-slate-700">AIアドバイス</span>
                <span class="ml-auto text-xs text-slate-400">${e.model||"AI"}</span>
            </div>
            <div class="prose prose-sm max-w-none text-slate-600">
                 ${W(s)}
            </div>
        </div>
    `}function W(n){return n.replace(/^### (.+)(?:\n|$)/gm,'<h4 class="font-bold text-slate-800 mt-3 mb-1">$1</h4>').replace(/^## (.+)(?:\n|$)/gm,'<h3 class="font-bold text-slate-900 mt-4 mb-2">$1</h3>').replace(/^# (.+)(?:\n|$)/gm,'<h2 class="font-bold text-slate-900 text-lg mt-4 mb-2">$1</h2>').replace(/^\d+\. (.+)(?:\n|$)/gm,'<p class="font-semibold text-slate-800">$1</p>').replace(/^[-•] (.+)(?:\n|$)/gm,'<p class="pl-4 text-slate-700 before:content-["•"] before:mr-2 before:text-slate-400">$1</p>').replace(/\*\*(.+?)\*\*/g,'<strong class="text-slate-800">$1</strong>').replace(/\n/g,"<br>")}
