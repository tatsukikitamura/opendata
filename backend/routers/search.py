
"""
Search API router.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from services.route_graph import get_graph
from services.timetable.core import search_route_with_times
from services.timetable.utils import minutes_to_time
from datetime import datetime

router = APIRouter()


@router.get("/search")
def search_route_api(
    from_station: str = Query(..., description="Departure station"),
    to_station: str = Query(..., description="Arrival station")
):
    """
    Find best route (shortest time) using graph search (Dijkstra).
    This returns theoretical route without actual train times.
    """
    graph = get_graph()
    result = graph.find_route(from_station, to_station)
    return result


@router.get("/search_with_times")
def search_route_with_times_api(
    from_station: str = Query(..., description="Departure station"),
    to_station: str = Query(..., description="Arrival station"),
    time: str = Query(..., description="Departure time (HH:MM)"),
    type: str = Query("departure", description="Search type (departure/arrival)"),
    db: Session = Depends(get_db)
):
    """
    Find best route and map it to actual train timetable.
    """
    graph = get_graph()
    
    # 1. Find best route structure (railways and transfer stations)
    route_result = graph.find_route(from_station, to_station)
    
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
    
    return result
