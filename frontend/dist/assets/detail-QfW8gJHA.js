import{s as k,d as E}from"./api-D0nMKdtm.js";function M(r){const e=r.toLowerCase();return e.includes("山手")?"bg-green-500":e.includes("中央")&&e.includes("快速")?"bg-orange-500":e.includes("中央")&&e.includes("総武")?"bg-yellow-500":e.includes("京浜東北")?"bg-sky-500":e.includes("埼京")?"bg-emerald-600":e.includes("湘南新宿")?"bg-orange-600":e.includes("総武快速")||e.includes("総武線快速")?"bg-blue-600":e.includes("常磐")?"bg-cyan-500":e.includes("東海道")?"bg-orange-400":e.includes("横須賀")?"bg-blue-500":e.includes("武蔵野")?"bg-orange-600":e.includes("京葉")?"bg-red-500":e.includes("銀座")?"bg-orange-400":e.includes("丸ノ内")?"bg-red-500":e.includes("日比谷")?"bg-gray-400":e.includes("東西")?"bg-sky-400":e.includes("千代田")?"bg-green-600":e.includes("有楽町")?"bg-yellow-600":e.includes("半蔵門")?"bg-purple-500":e.includes("南北")?"bg-emerald-400":e.includes("副都心")?"bg-amber-700":e.includes("浅草")?"bg-rose-400":e.includes("三田")?"bg-blue-700":e.includes("新宿")?"bg-lime-500":e.includes("大江戸")?"bg-pink-600":"bg-slate-500"}function h(r){document.getElementById("loading-state").classList.add("hidden"),document.getElementById("result-state").classList.add("hidden"),document.getElementById("error-state").classList.remove("hidden"),document.getElementById("error-message").textContent=r,document.getElementById("route-subheader").textContent=""}function I(r){const e=document.getElementById("route-timeline");e&&(e.innerHTML="",r.forEach((s,t)=>{const d=t===r.length-1,i=M(s.railway||""),o=document.createElement("div");o.className="flex";let m="";t===0?m=`<div class="text-xl font-bold text-slate-800">${s.departure_time}</div>`:m=`
                <div class="text-sm text-slate-500 leading-tight">${r[t-1].arrival_time}着</div>
                <div class="text-base font-bold text-slate-800 leading-tight">${s.departure_time}発</div>
            `;let u="";t===0?u='<div class="w-6 h-6 bg-slate-800 text-white rounded-sm font-bold text-xs flex items-center justify-center z-10 shadow-md">発</div>':u='<div class="w-4 h-4 bg-white border-2 border-slate-400 rounded-full z-10 shadow-sm"></div>',o.innerHTML=`
            <div class="w-20 text-right pr-4 flex flex-col justify-center gap-0.5">
                ${m}
            </div>
            <div class="w-8 flex flex-col items-center relative">
                 ${u}
                 <div class="w-1.5 ${i} h-full absolute top-4 z-0 opacity-80"></div>
            </div>
            <div class="flex-1 pl-2 py-1 items-center flex">
                <span class="text-lg font-bold text-slate-800 border-b border-slate-200 pb-1 w-full">${s.from}</span>
            </div>
        `,e.appendChild(o);const l=s.train_number?`<span class="text-slate-500 text-sm ml-2">${s.train_type} ${s.train_number}</span>`:s.train_type?`<span class="text-slate-500 text-sm ml-2">${s.train_type}</span>`:"",n=document.createElement("div");if(n.className="flex min-h-[4rem]",n.innerHTML=`
            <div class="w-20"></div> <!-- Time Spacer -->
            <div class="w-8 flex flex-col items-center relative">
                 <div class="w-1.5 ${i} h-full absolute top-0 bottom-0 z-0 opacity-80"></div>
            </div>
            <div class="flex-1 pl-2 py-3 flex flex-col justify-center">
                 <div class="flex items-center">
                    <span class="text-2xl mr-2">🚃</span>
                    <div>
                        <div class="font-bold text-slate-700 text-sm">${s.railway}</div>
                        ${l}
                    </div>
                 </div>
                 ${s.note?`<div class="text-xs text-amber-600 mt-1 ml-8 font-medium">⚠️ ${s.note}</div>`:""}
            </div>
        `,e.appendChild(n),d){const a=document.createElement("div");a.className="flex",a.innerHTML=`
                 <div class="w-20 text-right pr-4 flex flex-col justify-center">
                    <div class="text-xl font-bold text-slate-800">${s.arrival_time}</div>
                </div>
                <div class="w-8 flex flex-col items-center relative">
                     <div class="w-1.5 ${i} h-3 absolute top-0 z-0 opacity-80"></div> <!-- Connect from above -->
                     <div class="w-6 h-6 bg-slate-600 text-white rounded-sm font-bold text-xs flex items-center justify-center z-10 mt-2 shadow-md">着</div>
                </div>
                <div class="flex-1 pl-2 py-2 items-center flex">
                    <span class="text-lg font-bold text-slate-800 border-b border-slate-200 pb-1 w-full">${s.to}</span>
                </div>
            `,e.appendChild(a)}}))}let w=[];document.addEventListener("DOMContentLoaded",async()=>{const r=new URLSearchParams(window.location.search),e=r.get("from"),s=r.get("to"),t=r.get("time");if(!e||!s||!t){h("出発駅、到着駅、時刻を指定してください。");return}document.getElementById("route-header").textContent=`${e} → ${s}`,document.getElementById("route-subheader").textContent=`${t} 以降の電車を検索中...`,await B(e,s,t),document.getElementById("back-to-list").addEventListener("click",()=>{L()})});async function B(r,e,s){try{const t=await k(r,e,s);if(!t.routes||t.routes.length===0){h("ルートが見つかりませんでした。");return}w=t.routes,H(),document.getElementById("loading-state").classList.add("hidden"),document.getElementById("result-state").classList.remove("hidden"),L()}catch(t){t.message&&h(t.message)}}function L(){document.getElementById("route-list-view").classList.remove("hidden"),document.getElementById("route-detail-view").classList.add("hidden"),document.getElementById("global-back-link").classList.remove("hidden"),document.getElementById("main-header").classList.remove("hidden"),document.getElementById("route-header").textContent="検索結果"}function y(r){document.getElementById("route-list-view").classList.add("hidden"),document.getElementById("route-detail-view").classList.remove("hidden"),document.getElementById("global-back-link").classList.add("hidden"),document.getElementById("main-header").classList.add("hidden"),C(r)}function H(){const r=document.getElementById("route-list-container");r.innerHTML="",w.forEach((e,s)=>{const t=e.segments||[],d=t.length>0&&t[0].departure_time?t[0].departure_time:"--:--",o=(t.length>0?t[t.length-1]:null)?.arrival_time||"--:--",m=e.transfers||0,u=e.risk||{level:"LOW"};let l="";if(d!=="--:--"&&o!=="--:--"){const[b,v]=d.split(":").map(Number),[x,p]=o.split(":").map(Number);let g=x*60+p-(b*60+v);g<0&&(g+=1440);const f=Math.floor(g/60),$=g%60;l=f>0?`${f}時間${$}分`:`${$}分`}const n=document.createElement("div");let a="bg-white hover:bg-slate-50 border-slate-200 shadow-sm";u.level==="HIGH"?a="bg-red-50 hover:bg-red-100 border-red-200 shadow-sm":u.level==="MEDIUM"&&(a="bg-amber-50 hover:bg-amber-100 border-amber-200 shadow-sm"),n.className=`p-8 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${a} focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2`,n.setAttribute("role","button"),n.setAttribute("tabindex","0"),n.setAttribute("aria-label",`${d}発 ${o}着 乗換${m}回 ${l}`);let c="";u.level==="HIGH"?c='<span class="px-2 py-1 rounded text-xs font-bold bg-red-100 text-red-700 border border-red-200">遅延リスク高</span>':u.level==="MEDIUM"?c='<span class="px-2 py-1 rounded text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200">遅延注意</span>':c='<span class="px-2 py-1 rounded text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">平常運行</span>',n.innerHTML=`
            <div>
                <div class="flex items-center gap-3 mb-1">
                    <span class="text-2xl font-bold text-slate-800">${o} 着</span>
                    <span class="text-sm text-slate-500">(${d} 発)</span>
                    ${l?`<span class="text-sm font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">${l}</span>`:""}
                </div>
                <div class="text-sm text-slate-500 mt-2">
                    乗換 ${m}回
                </div>
            </div>
            <div>
                <!-- 3-Axis Scores -->
                <div class="mt-3 text-xs space-y-1 w-48">
                    <div class="flex items-center gap-4">
                        <span class="w-8 text-slate-500">速さ</span>
                        <div class="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div class="h-full bg-blue-500" style="width: ${(e.scores?.speed||0)*20}%"></div>
                        </div>
                        <span class="w-6 text-right font-mono text-slate-600">${(e.scores?.speed||0).toFixed(1)}</span>
                    </div>
                    <div class="flex items-center gap-4">
                        <span class="w-8 text-slate-500">快適</span>
                        <div class="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div class="h-full bg-emerald-500" style="width: ${(e.scores?.comfort||0)*20}%"></div>
                        </div>
                        <span class="w-6 text-right font-mono text-slate-600">${(e.scores?.comfort||0).toFixed(1)}</span>
                    </div>
                    <div class="flex items-center gap-4">
                        <span class="w-8 text-slate-500">安定</span>
                        <div class="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div class="h-full bg-purple-500" style="width: ${(e.scores?.reliability||0)*20}%"></div>
                        </div>
                        <span class="w-6 text-right font-mono text-slate-600">${(e.scores?.reliability||0).toFixed(1)}</span>
                    </div>
                </div>
            </div>
            <div class="text-right">
                ${c}
                <div class="text-xs text-slate-400 mt-2 flex items-center justify-end gap-1">
                    詳細を見る
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                </div>
            </div>
        `,n.addEventListener("click",()=>{y(s)}),n.addEventListener("keydown",b=>{(b.key==="Enter"||b.key===" ")&&(b.preventDefault(),y(s))}),r.appendChild(n)})}function C(r){const e=w[r];if(!e)return;const s=e.segments||[],t=s.length>0&&s[0].departure_time?s[0].departure_time:"--:--",i=(s.length>0?s[s.length-1]:null)?.arrival_time||"--:--";let o="--分";if(t!=="--:--"&&i!=="--:--"&&t&&i){const[c,b]=t.split(":").map(Number),[v,x]=i.split(":").map(Number);let p=v*60+x-(c*60+b);p<0&&(p+=1440);const g=Math.floor(p/60),f=p%60;o=g>0?`${g}時間${f}分`:`${f}分`}document.getElementById("first-departure").textContent=t,document.getElementById("arrival-time").textContent=i,document.getElementById("transfer-count").textContent=`乗換 ${e.transfers||0}回`,document.getElementById("total-duration").textContent=o,document.getElementById("route-header").textContent=`${t} 発 → ${i} 着`;const m=document.getElementById("route-summary-container"),u=document.getElementById("arrival-time"),l=e.risk&&e.risk.level?e.risk.level:"LOW",n={HIGH:{container:"bg-gradient-to-r from-red-50 to-rose-50 border-red-200",arrivalText:"text-red-600"},MEDIUM:{container:"bg-gradient-to-r from-amber-50 to-orange-50 border-amber-200",arrivalText:"text-amber-600"},LOW:{container:"bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-200",arrivalText:"text-emerald-600"}},a=n[l]||n.LOW;m.className=`rounded-2xl p-5 mb-6 border ${a.container}`,u.className=`text-4xl font-bold leading-none ${a.arrivalText}`,T(e),I(s),j(e)}function T(r){const e=document.getElementById("delay-warnings");if(!e)return;e.innerHTML="";const s=r.delay_warnings||[],t=r.risk||{level:"LOW",reasons:[]},d=r.crowd||{level:"UNKNOWN",score:0,details:[]},i=r.venue_warnings||{transfer_warnings:[],passing_info:[]};function o(l,n,a,c,b,v=!1){const x={red:{bg:"bg-red-50",border:"border-red-200",header:"text-red-800",headerBg:"hover:bg-red-100"},amber:{bg:"bg-amber-50",border:"border-amber-200",header:"text-amber-800",headerBg:"hover:bg-amber-100"},orange:{bg:"bg-orange-50",border:"border-orange-200",header:"text-orange-800",headerBg:"hover:bg-orange-100"},blue:{bg:"bg-blue-50",border:"border-blue-200",header:"text-blue-800",headerBg:"hover:bg-blue-100"},emerald:{bg:"bg-emerald-50",border:"border-emerald-200",header:"text-emerald-800",headerBg:"hover:bg-emerald-100"},slate:{bg:"bg-slate-50",border:"border-slate-200",header:"text-slate-700",headerBg:"hover:bg-slate-100"}},p=x[c]||x.slate,g=document.createElement("div");return g.className=`${p.bg} ${p.border} border rounded-xl overflow-hidden mb-2`,g.innerHTML=`
            <button 
                class="w-full flex items-center justify-between p-4 ${p.headerBg} transition-colors"
                aria-expanded="${v}"
                aria-controls="accordion-content-${l}"
                onclick="this.setAttribute('aria-expanded', this.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'); document.getElementById('accordion-content-${l}').classList.toggle('hidden');"
            >
                <div class="flex items-center gap-2">
                    <span class="text-xl">${n}</span>
                    <span class="font-bold ${p.header}">${a}</span>
                </div>
                <svg class="w-5 h-5 ${p.header} transition-transform" style="transform: rotate(${v?"180deg":"0deg"});" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            <div id="accordion-content-${l}" class="${v?"":"hidden"} px-4 pb-4">
                ${b}
            </div>
        `,g}let m=!1;if(s.length>0){m=!0;const l=s.map(n=>{let a="";if(n.timestamp)try{const c=new Date(n.timestamp);a=`${c.getHours().toString().padStart(2,"0")}:${c.getMinutes().toString().padStart(2,"0")} 時点`}catch{}return`
                <div class="bg-white/60 rounded-lg p-3 border border-red-100 mb-2 last:mb-0">
                    <div class="flex items-center justify-between">
                        <p class="text-red-800 font-medium">${n.railway}</p>
                        ${a?`<span class="text-xs text-red-400">${a}</span>`:""}
                    </div>
                    <p class="text-red-700/80 text-sm mt-1">${n.reason||"遅延が発生しています"}</p>
                </div>
            `}).join("");e.appendChild(o("realtime","🚨",`リアルタイム遅延 (${s.length}件)`,"red",l,!0))}{m=!0;const l=t.level==="HIGH"?"red":t.level==="MEDIUM"?"amber":"emerald",n=t.level==="HIGH"?"高い":t.level==="MEDIUM"?"中程度":"低い";let a="";t.reasons.length>0?a=`
                <p class="text-xs text-slate-500 mb-2">過去の遅延実績データに基づく予測:</p>
                <div class="space-y-2">
                    ${t.reasons.map(c=>`
                        <div class="bg-white/60 rounded-lg p-3 border border-current/10">
                            <p class="font-medium text-sm">${c.railway||""}</p>
                            <p class="text-xs text-slate-600 mt-1">${c.rate||c.display||""}</p>
                        </div>
                    `).join("")}
                </div>
            `:a=`
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
            `,e.appendChild(o("risk","⚠️",`遅延リスク: ${n}`,l,a,t.level!=="LOW"))}const u=[...i.transfer_warnings,...i.passing_info];if(u.length>0){m=!0;let l="";i.transfer_warnings.length>0&&(l+=`
                <p class="text-xs text-orange-600 font-medium mb-2">⚠️ 乗換駅周辺</p>
                ${i.transfer_warnings.map(n=>`
                    <div class="bg-white/60 rounded-lg p-3 border border-orange-100 mb-2">
                        <p class="font-medium text-orange-900">📍 ${n.station}駅 → ${n.venue}</p>
                        <p class="text-xs text-slate-500 mt-1">収容人数: ${n.capacity.toLocaleString()}人 / ${n.note}</p>
                    </div>
                `).join("")}
            `),i.passing_info.length>0&&(l+=`
                <p class="text-xs text-slate-500 mt-3 mb-2">ℹ️ 通過駅周辺</p>
                <p class="text-sm text-slate-600">${i.passing_info.map(n=>`${n.station}(${n.venues.join(", ")})`).join(" / ")}</p>
            `),e.appendChild(o("venue","🎪",`イベント情報 (${u.length}件)`,"orange",l,!1))}if(d.level!=="UNKNOWN"&&d.details&&d.details.length>0){m=!0;const l=d.level==="HIGH"?"大都市圏":d.level==="MEDIUM"?"中規模":"郊外",n=`
            <div class="flex items-center gap-3 mb-3">
                <div class="text-2xl font-bold text-blue-800">${d.score.toLocaleString()}</div>
                <div class="text-xs text-slate-500">人/日<br>(平均乗降客数)</div>
                <span class="ml-auto px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">${l}</span>
            </div>
            <div class="text-xs text-slate-500">
                <p class="font-medium mb-1">経由駅の規模:</p>
                <p>${d.details.join(", ")}</p>
            </div>
        `;e.appendChild(o("crowd","📊","駅混雑度","blue",n,!1))}if(!m){const l=document.createElement("div");l.className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 text-center",l.innerHTML=`
            <div class="flex flex-col items-center gap-2">
                <div class="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
                    <svg class="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                </div>
                <p class="text-emerald-800 font-medium">すべての路線が平常運行中</p>
                <p class="text-emerald-600 text-xs">遅延情報・混雑情報はありません</p>
            </div>
        `,e.appendChild(l)}}function j(r){const e=document.getElementById("ai-diagnose-btn"),s=document.getElementById("ai-diagnosis-result");if(!e||!s)return;s.classList.add("hidden"),s.innerHTML="",e.disabled=!1,e.innerHTML=`
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
        `;try{const d=await E(r);_(s,d),t.innerHTML=`
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                再診断
            `,t.disabled=!1}catch(d){s.innerHTML=`
                <div class="bg-red-50 border border-red-200 rounded-xl p-4">
                    <div class="flex items-center gap-2 text-red-700">
                        <span class="text-xl">⚠️</span>
                        <span class="font-medium">診断エラー</span>
                    </div>
                    <p class="text-red-600 text-sm mt-2">${d.message||"AI診断に失敗しました。しばらく経ってから再度お試しください。"}</p>
                </div>
            `,t.innerHTML=`
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                再試行
            `,t.disabled=!1}})}function _(r,e){const s=e.diagnosis||"診断結果がありません";s.split(`
`).filter(t=>t.trim()),r.innerHTML=`
        <div class="mt-4 px-1">
            <div class="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100">
                <span class="text-lg">✨</span>
                <span class="font-bold text-slate-700">AIアドバイス</span>
                <span class="ml-auto text-xs text-slate-400">${e.model||"AI"}</span>
            </div>
            <div class="prose prose-sm max-w-none text-slate-600">
                 ${S(s)}
            </div>
        </div>
    `}function S(r){return r.replace(/^### (.+)(?:\n|$)/gm,'<h4 class="font-bold text-slate-800 mt-3 mb-1">$1</h4>').replace(/^## (.+)(?:\n|$)/gm,'<h3 class="font-bold text-slate-900 mt-4 mb-2">$1</h3>').replace(/^# (.+)(?:\n|$)/gm,'<h2 class="font-bold text-slate-900 text-lg mt-4 mb-2">$1</h2>').replace(/^\d+\. (.+)(?:\n|$)/gm,'<p class="font-semibold text-slate-800">$1</p>').replace(/^[-•] (.+)(?:\n|$)/gm,'<p class="pl-4 text-slate-700 before:content-["•"] before:mr-2 before:text-slate-400">$1</p>').replace(/\*\*(.+?)\*\*/g,'<strong class="text-slate-800">$1</strong>').replace(/\n/g,"<br>")}
