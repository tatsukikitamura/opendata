
"""
Search API router.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from services.routing import get_graph
from services.timetable.core import search_route_with_times
from services.delay import check_route_delay, get_delay_summary
from services.risk import get_route_risk
from services.venue import get_venue_warnings
from services.score import calculate_route_scores
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
        # Verify if mapped station name needs normalization? 
        # The search uses Japanese names (e.g. "東京"), stats usage Japanese keys.
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
    # limit=5, logic is now internal to find_routes (Buffer Variation + Penalty)
    theoretical_routes = graph.find_routes(from_station, to_station, limit=5)
    
    # Determine weekday type
    now = datetime.now()
    if now.weekday() >= 6: # Sunday (0=Mon, 6=Sun)
        # Check for Holiday calendar logic? 
        # Python weekday: Mon=0 ... Sun=6
        # Usually Sat=5, Sun=6.
        weekday_type = "Holiday"
    elif now.weekday() == 5: # Saturday
        weekday_type = "Saturday"
    else:
        # Check for national holidays? (Advanced)
        # For now, simplistic Weekday.
        weekday_type = "Weekday"
        
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
    
    # Clean up internal fields and add delay warnings
    current_date = datetime.now().date().isoformat()
    departure_time_str = f"{current_date}T{search_time}"

    for route in top_routes:
        route.pop("_arrival", None)
        
        # Add risk score
        route["risk"] = get_route_risk(route, departure_time_str)
        
        # Add delay warnings
        delay_warnings = []
        for segment in route.get("segments", []):
            railway = segment.get("railway", "")
            if railway:
                delay_sec = check_route_delay(railway)
                if delay_sec:
                    delay_warnings.append({
                        "railway": railway,
                        "delay_seconds": delay_sec,
                        "delay_minutes": delay_sec // 60
                    })
        route["delay_warnings"] = delay_warnings
        
        # Add Crowd Metrics
        route["crowd"] = get_crowd_metrics(route.get("segments", []))
        
        # Add Venue Warnings
        route["venue_warnings"] = get_venue_warnings(route.get("segments", []))

    # Calculate 3-axis scores (Speed, Comfort, Reliability)
    # Passed top_routes for relative speed comparison
    for route in top_routes:
        route["scores"] = calculate_route_scores(route, top_routes)
    
    return {"routes": top_routes, "total_found": len(candidates)}
