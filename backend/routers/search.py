
"""
Search API router.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from services.route_graph import get_graph
from services.timetable.core import search_route_with_times
from services.delay_service import check_route_delay, get_delay_summary
from services.risk_service import get_route_risk
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
    transfer_buffer: int = Query(0, description="Additional time for transfers (minutes)")
):
    """
    Find best route (shortest time) using graph search (Dijkstra).
    This returns theoretical route without actual train times.
    """
    graph = get_graph()
    result = graph.find_route(from_station, to_station, transfer_buffer=transfer_buffer)
    return result


@router.get("/search_with_times")
def search_route_with_times_api(
    from_station: str = Query(..., description="Departure station"),
    to_station: str = Query(..., description="Arrival station"),
    time: str = Query(..., description="Departure time (HH:MM)"),
    type: str = Query("departure", description="Search type (departure/arrival)"),
    transfer_buffer: int = Query(0, description="Additional time for transfers in graph search (minutes)"),
    db: Session = Depends(get_db)
):
    """
    Find best route and map it to actual train timetable.
    """
    graph = get_graph()
    
    # 1. Find best route structure (railways and transfer stations)
    route_result = graph.find_route(from_station, to_station, transfer_buffer=transfer_buffer)
    
    station_map = {}
    if hasattr(graph, "station_info"):
        for station_id, info in graph.station_info.items():
            name_ja = info.get("name_ja", "")
            name_en = info.get("name_en", "")
            if name_ja and name_en:
                station_map[name_ja] = name_en
            # Also map English to English for consistency
            if name_en:
                station_map[name_en] = name_en
    
    # 3. Find actual trains for each segment
    weekday_type = "Weekday"  # Default to weekday for now
    
    # Ensure time is in HH:MM format
    if len(time) == 4 and time.isdigit():
        time = f"{time[:2]}:{time[2:]}"
        
    result = search_route_with_times(
        db, 
        route_result, 
        time, 
        weekday_type, 
        transfer_buffer=5,
        station_name_map=station_map
    )
    
    # 4. Check for delays on routes used
    delay_warnings = []
    segments = result.get("segments", [])
    checked_railways = set()
    
    for segment in segments:
        railway = segment.get("railway", "")
        if railway and railway not in checked_railways:
            checked_railways.add(railway)
            delay_sec = check_route_delay(railway)
            if delay_sec:
                delay_warnings.append({
                    "railway": railway,
                    "delay_seconds": delay_sec,
                    "delay_minutes": delay_sec // 60,
                    "message": f"{railway}: 約{delay_sec // 60}分の遅延"
                })
    
    result["delay_warnings"] = delay_warnings
    
    return result


@router.get("/delays")
def get_delays_api():
    """Get current delay summary for all routes."""
    return get_delay_summary()


@router.get("/search_multi")
def search_multi_route_api(
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
    
    # Use iterative penalty method to find up to 3 distinct routes
    candidates = []
    
    # Find theoretical routes first
    theoretical_routes = graph.find_routes(from_station, to_station, limit=3, transfer_buffer=5)
    
    for route_result in theoretical_routes:
        # Apply timetable
        timed_result = search_route_with_times(
            db, route_result, search_time, "Weekday",
            transfer_buffer=5, station_name_map=station_map
        )
        
        if "error" in timed_result:
            continue
        
        # Get arrival time for sorting
        segments = timed_result.get("segments", [])
        if segments:
            last_seg = next((s for s in reversed(segments) if s.get("arrival_time")), None)
            if last_seg:
                arrival = last_seg.get("arrival_time", "99:99")
                timed_result["_arrival"] = arrival
                timed_result["transfer_buffer_used"] = 5
                candidates.append(timed_result)
    
    # Sort by arrival time
    candidates.sort(key=lambda x: x.get("_arrival", "99:99"))
    top_routes = candidates[:3]
    
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

    
    return {"routes": top_routes, "total_found": len(candidates)}
