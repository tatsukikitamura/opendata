
/**
 * Get color class for railway line.
 * @param {string} railway - Railway name
 * @returns {string} Tailwind CSS class for background color
 */
export function formatDuration(minutes) {
    if (!minutes) return "";
    minutes = Math.round(minutes);
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    
    if (h > 0) {
        return `${h}時間${m}分`;
    }
    return `${m}分`;
}

/**
 * Get color class for railway line.
 */
export function getLineColor(railway) {
    const name = railway.toLowerCase();
    
    // JR Lines
    if (name.includes("山手")) return "bg-green-500";
    if (name.includes("中央") && name.includes("快速")) return "bg-orange-500";
    if (name.includes("中央") && name.includes("総武")) return "bg-yellow-500";
    if (name.includes("京浜東北")) return "bg-sky-500";
    if (name.includes("埼京")) return "bg-emerald-600";
    if (name.includes("湘南新宿")) return "bg-orange-600";
    if (name.includes("総武快速") || name.includes("総武線快速")) return "bg-blue-600";
    if (name.includes("常磐")) return "bg-cyan-500";
    if (name.includes("東海道")) return "bg-orange-400";
    if (name.includes("横須賀")) return "bg-blue-500";
    if (name.includes("武蔵野")) return "bg-orange-600";
    if (name.includes("京葉")) return "bg-red-500";
    
    // Metro / Toei (placeholder colors)
    if (name.includes("銀座")) return "bg-orange-400";
    if (name.includes("丸ノ内")) return "bg-red-500";
    if (name.includes("日比谷")) return "bg-gray-400";
    if (name.includes("東西")) return "bg-sky-400";
    if (name.includes("千代田")) return "bg-green-600";
    if (name.includes("有楽町")) return "bg-yellow-600";
    if (name.includes("半蔵門")) return "bg-purple-500";
    if (name.includes("南北")) return "bg-emerald-400";
    if (name.includes("副都心")) return "bg-amber-700";
    
    if (name.includes("浅草")) return "bg-rose-400";
    if (name.includes("三田")) return "bg-blue-700";
    if (name.includes("新宿")) return "bg-lime-500";
    if (name.includes("大江戸")) return "bg-pink-600";
    
    // Default
    return "bg-slate-500";
}

/**
 * Show error message in UI.
 * @param {string} message 
 */
export function showError(message) {
    document.getElementById("loading-state").classList.add("hidden");
    document.getElementById("result-state").classList.add("hidden");
    document.getElementById("error-state").classList.remove("hidden");
    document.getElementById("error-message").textContent = message;
    document.getElementById("route-subheader").textContent = "";
}
