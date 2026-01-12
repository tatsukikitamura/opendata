
const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

/**
 * Verify backend connection.
 * @returns {Promise<boolean>}
 */
export async function checkBackendHealth() {
    try {
        const res = await fetch(API_BASE);
        return res.ok;
    } catch (e) {
        return false;
    }
}

/**
 * Find multiple route options with different transfer trade-offs.
 * @param {string} from - Departure station
 * @param {string} to - Arrival station
 * @param {string} time - Departure time (HH:MM)
 * @param {string} [dayType] - Day type (Weekday, Saturday, Holiday)
 * @returns {Promise<Object>} Object with routes array
 */
export async function searchRoute(from, to, time, dayType = null) {
    try {
        let url = `${API_BASE}/search?from_station=${encodeURIComponent(from)}&to_station=${encodeURIComponent(to)}&time=${encodeURIComponent(time)}`;
        if (dayType) {
            url += `&day_type=${encodeURIComponent(dayType)}`;
        }
        const res = await fetch(url);
        const data = await res.json();
        return data;
    } catch (e) {
        console.error("API Error:", e);
        throw new Error("サーバーに接続できませんでした。");
    }
}
/**
 * Get all available stations.
 * @returns {Promise<string[]>} List of station names
 */
export async function getStations() {
    try {
        const res = await fetch(`${API_BASE}/stations`);
        const data = await res.json();
        return data;
    } catch (e) {
        console.error("API Error:", e);
        return [];
    }
}

/**
 * Get AI diagnosis for a route.
 * @param {Object} routeData - Route data including segments, risk, crowd, etc.
 * @returns {Promise<Object>} AI diagnosis result
 */
export async function diagnoseRoute(routeData) {
    try {
        const res = await fetch(`${API_BASE}/diagnose`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                segments: routeData.segments || [],
                risk: routeData.risk || null,
                crowd: routeData.crowd || null,
                venue_warnings: routeData.venue_warnings || null,
                delay_warnings: routeData.delay_warnings || null
            })
        });
        
        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.detail || 'AI診断に失敗しました');
        }
        
        return await res.json();
    } catch (e) {
        console.error("AI Diagnosis Error:", e);
        throw e;
    }
}

/**
 * Get current delay information.
 * @returns {Promise<Array>} List of delayed railways
 */
export async function getCurrentDelays() {
    try {
        const res = await fetch(`${API_BASE}/api/delays/current`);
        if (!res.ok) return { updated_at: null, delays: [] };
        return await res.json();
    } catch (e) {
        console.error("Delay Info Error:", e);
        return { updated_at: null, delays: [] };
    }
}

/**
 * Get delay history for a railway.
 * @param {string} railwayName - Short name or ID
 * @returns {Promise<Array>} List of historical delay records
 */
export async function getDelayHistory(railwayName) {
    try {
        const res = await fetch(`${API_BASE}/api/delays/history?railway=${encodeURIComponent(railwayName)}`);
        if (!res.ok) throw new Error("History fetch failed");
        return await res.json();
    } catch (e) {
        console.error("Delay History Error:", e);
        throw e;
    }
}
