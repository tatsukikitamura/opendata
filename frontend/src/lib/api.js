
const API_BASE = "http://127.0.0.1:8000";

/**
 * Find best route with actual train times.
 * @param {string} from - Departure station
 * @param {string} to - Arrival station
 * @param {string} time - Departure time (HH:MM)
 * @returns {Promise<Object>} Route result
 */
export async function searchRouteWithTimes(from, to, time) {
    try {
        const url = `${API_BASE}/search_with_times?from_station=${encodeURIComponent(from)}&to_station=${encodeURIComponent(to)}&time=${encodeURIComponent(time)}`;
        const res = await fetch(url);
        const data = await res.json();
        return data;
    } catch (e) {
        console.error("API Error:", e);
        throw new Error("サーバーに接続できませんでした。");
    }
}

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
