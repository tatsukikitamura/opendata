
"""
Search API router.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from services.routing import get_graph
from services.timetable.core import search_route_with_times
from services.risk import get_route_risk, get_current_delays
from services.venue import get_venue_warnings
from services.score import calculate_route_scores
from services.fare_scraper import FareScraper
from datetime import datetime

import json
import os

router = APIRouter()

# Load station stats
STATS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "station_stats.json")
STATION_STATS = {}
if os.path.exists(STATS_FILE):
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        STATION_STATS = json.load(f)


def get_crowd_metrics(route_segments):
    """
    Calculate route crowdedness based on station volume.
    Returns:
        dict: {
            "score": int (average daily passengers),
            "level": str (HIGH/MEDIUM/LOW),
            "details": list (strings)
        }
    """
    if not STATION_STATS:
        return {"score": 0, "level": "UNKNOWN", "details": []}
        
    stations = set()
    # Collect all unique stations used (From and To)
    for seg in route_segments:
        stations.add(seg.get("from"))
        stations.add(seg.get("to"))
        
    if not stations:
        return {"score": 0, "level": "UNKNOWN", "details": []}
        
    total_volume = 0
    count = 0
    details = []
    
    for station in stations:
        # Simple lookup (exact match)
        vol = STATION_STATS.get(station, 0)
        if vol > 0:
            total_volume += vol
            count += 1
            details.append(f"{station}: {vol//1000}k")
            
    if count == 0:
        return {"score": 0, "level": "LOW", "details": []}
        
    avg_volume = total_volume // count
    
    # Thresholds
    if avg_volume > 150000:
        level = "HIGH"
    elif avg_volume > 50000:
        level = "MEDIUM"
    else:
        level = "LOW"
        
    return {
        "score": avg_volume,
        "level": level,
        "details": details
    }




@router.get("/search")
def search_route_api(
    from_station: str = Query(..., description="Departure station"),
    to_station: str = Query(..., description="Arrival station"),
    time: str = Query(..., description="Departure time (HH:MM)"),
    db: Session = Depends(get_db)
):
    """
    Find multiple route options with different transfer trade-offs.
    Returns up to 3 unique routes sorted by actual arrival time.
    """
    graph = get_graph()
    
    # Build station name map
    station_map = {}
    if hasattr(graph, "station_info"):
        for station_id, info in graph.station_info.items():
            name_ja = info.get("name_ja", "")
            name_en = info.get("name_en", "")
            if name_ja and name_en:
                station_map[name_ja] = name_en
            if name_en:
                station_map[name_en] = name_en
    
    # Ensure time format
    search_time = time
    if len(time) == 4 and time.isdigit():
        search_time = f"{time[:2]}:{time[2:]}"
    
    # Use iterative penalty method to find up to 5 distinct routes
    candidates = []
    
    # Find theoretical routes first
    theoretical_routes = graph.find_routes(from_station, to_station, limit=5)
    
    # Determine weekday type
    now = datetime.now()
    if now.weekday() >= 6: # Sunday (0=Mon, 6=Sun)
        weekday_type = "Holiday"
    elif now.weekday() == 5: # Saturday
        weekday_type = "Saturday"
    else:
        weekday_type = "Weekday"
    
    # Import mapping for Japanese to English railway names (once)
    from services.constants import RAILWAY_JA_TO_EN
    from concurrent.futures import ThreadPoolExecutor
    
    # Prepare common variables for tasks
    current_date = datetime.now().date().isoformat()
    departure_time_str = f"{current_date}T{search_time}"

    # Use ThreadPoolExecutor for speculative execution
    with ThreadPoolExecutor(max_workers=6) as executor:
        for route_result in theoretical_routes:
            # Apply timetable
            timed_result = search_route_with_times(
                db, route_result, search_time, weekday_type,
                transfer_buffer=5, station_name_map=station_map
            )
            
            if "error" in timed_result:
                continue
        
            # Skip routes with incomplete timetable data (null departure times)
            segments = timed_result.get("segments", [])
            has_null_departure = any(seg.get("departure_time") is None for seg in segments)
            if has_null_departure:
                continue
            
            # --- Speculative Execution Start ---
            # Submit auxiliary tasks immediately to run consistently with other route searches
            
            # Prepare arguments for FareScraper
            via_stations = []
            seg_list = timed_result.get("segments", [])
            if len(seg_list) > 1:
                for i in range(len(seg_list) - 1):
                    via_stations.append(seg_list[i]["to"])
            
            # Submit Risk Calculation
            _risk_future = executor.submit(get_route_risk, timed_result, departure_time_str)
            timed_result["_risk_future"] = _risk_future
            
            # Submit Fare Scraping
            # Note: We need to pass a copy or ensure immutability if needed, but strings/lists here are fine.
            _fare_future = executor.submit(FareScraper.get_fare, from_station, to_station, via_stations)
            timed_result["_fare_future"] = _fare_future
            # --- Speculative Execution End ---
            
            # Get arrival time for sorting
            if segments:
                last_seg = next((s for s in reversed(segments) if s.get("arrival_time")), None)
                if last_seg:
                    arrival = last_seg.get("arrival_time", "99:99")
                    timed_result["_arrival"] = arrival
                    candidates.append(timed_result)
    
    # Sort by arrival time
    candidates.sort(key=lambda x: x.get("_arrival", "99:99"))
    top_routes = candidates[:5]
    
    # Get current real-time delays ONCE for all routes
    current_delays_data = get_current_delays()
    current_delays = current_delays_data["delays"]
    current_delay_map = {}
    for d in current_delays:
        # Normalize key to match route segment logic (English short code)
        raw = d["railway_name_en"]
        key = raw
        if "." in raw:
            key = raw.split(".")[-1]
        current_delay_map[key] = d
    

    
    
    # ---------------------------------------------------------
    # Retrieve Results from Futures for Top Routes
    # ---------------------------------------------------------
    
    # Collect risk results
    for route in top_routes:
        future = route.pop("_risk_future", None)
        if future:
            try:
                route["risk"] = future.result()
            except Exception as e:
                print(f"[ERROR] get_route_risk task failed: {e}")
                route["risk"] = {"score": 0, "level": "UNKNOWN", "reasons": []}
        else:
            route["risk"] = {"score": 0, "level": "UNKNOWN", "reasons": []}

    # Collect fare results
    for route in top_routes:
        future = route.pop("_fare_future", None)
        if future:
            try:
                fare_result = future.result()
                if fare_result and "total_fare" in fare_result:
                    route["fare"] = fare_result["total_fare"]
                else:
                    route["fare"] = None
            except Exception as e:
                print(f"[ERROR] FareScraper task failed: {e}")
                route["fare"] = None
        else:
            route["fare"] = None
    
    # Apply results to routes and add other metadata
    for idx, route in enumerate(top_routes):
        route.pop("_arrival", None)
        

        
        # Get REAL-TIME delay warnings for railways in this route
        delay_warnings = []
        route_railways = set()
        
        for seg in route.get("segments", []):
            railway = seg.get("railway", "")
            if railway:
                # Normalize railway name - try Japanese to English conversion
                if railway in RAILWAY_JA_TO_EN:
                    railway = RAILWAY_JA_TO_EN[railway]
                elif "." in railway:
                    railway = railway.split(".")[-1]
                route_railways.add(railway)
        
        for railway_name in route_railways:
            if railway_name in current_delay_map:
                delay_info = current_delay_map[railway_name]
                delay_warnings.append({
                    "railway": delay_info.get("railway_name", railway_name),
                    "railway_id": delay_info.get("railway_name_en", ""), # Use short code/EN name as ID for matching
                    "status": delay_info.get("status", ""),
                    "reason": delay_info.get("status_text", "遅延情報あり"),
                    "timestamp": delay_info.get("timestamp", "")
                })
        route["delay_warnings"] = delay_warnings
        
        # Add Crowd Metrics
        route["crowd"] = get_crowd_metrics(route.get("segments", []))
        
        # Add Venue Warnings
        route["venue_warnings"] = get_venue_warnings(route.get("segments", []))



    # Calculate 3-axis scores (Speed, Comfort, Reliability)
    for route in top_routes:
        route["scores"] = calculate_route_scores(route, top_routes)
    
    return {"routes": top_routes, "total_found": len(candidates)}
