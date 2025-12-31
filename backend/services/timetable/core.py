
"""
Core timetable search logic.
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from .finder import find_train_for_segment, get_arrival_time
from .utils import time_to_minutes, minutes_to_time


def search_route_with_times(
    db: Session,
    route_result: Dict,
    departure_time: str,
    weekday: str = "Weekday",
    transfer_buffer: int = 5,
    station_name_map: Dict[str, str] = None
) -> Dict:
    """
    Take a route from /search and add actual train times from timetable.
    
    Args:
        db: Database session
        route_result: Result from route_graph.find_route()
        departure_time: Desired departure time (HH:MM)
        weekday: Weekday/Saturday/Holiday
        transfer_buffer: Minutes needed for transfer
        station_name_map: Mapping from Japanese to English station names
    
    Returns:
        Route with actual train times for each segment
    """
    if "error" in route_result:
        return route_result
    
    segments = route_result.get("segments", [])
    if not segments:
        return {"error": "No segments in route"}
    
    # Build Japanese to English station name mapping if not provided
    if station_name_map is None:
        station_name_map = {}
    
    timed_segments = []
    current_time = departure_time
    
    for segment in segments:
        if segment.get("type") != "ride":
            continue
            
        from_station_ja = segment.get("from", "")
        to_station_ja = segment.get("to", "")
        railway = segment.get("railway", "")
        
        # Convert Japanese station name to English
        from_station_en = station_name_map.get(from_station_ja, from_station_ja)
        to_station_en = station_name_map.get(to_station_ja, to_station_ja)
        
        # Find actual train (with direction filtering)
        train = find_train_for_segment(db, from_station_en, to_station_en, railway, current_time, weekday)
        
        if train:
            # Calculate actual arrival time at destination station
            # Use English railway name from train dict (it's normalized in find_train_for_segment)
            arrival_time = get_arrival_time(
                db, 
                train["train_number"], 
                train["railway"], 
                to_station_en, 
                weekday
            )
            
            # Default to 15 mins if arrival time not found (fallback)
            travel_time_minutes = 15
            if arrival_time:
                dep_min = time_to_minutes(train["departure_time"])
                arr_min = time_to_minutes(arrival_time)
                
                # Handle potential day crossing (23:50 -> 00:10)
                if arr_min < dep_min:
                    arr_min += 24 * 60
                
                travel_time_minutes = arr_min - dep_min
                current_time_str = arrival_time
            else:
                # Fallback: estimate time based on number of stations? (not implemented)
                # Just add fixed time for now if data missing
                dep_min = time_to_minutes(train["departure_time"])
                current_time_str = minutes_to_time(dep_min + travel_time_minutes)
            
            timed_segments.append({
                "from": from_station_ja,
                "to": to_station_ja,
                "railway": railway,
                "departure_time": train["departure_time"],
                "arrival_time": arrival_time or current_time_str,  # Add arrival time
                "train_type": train["train_type"],
                "destination": train["destination"],
                "train_number": train["train_number"]
            })
            
            # Update current time for next segment (arrival + transfer buffer)
            # Add transfer buffer only if there are more segments
            current_min = time_to_minutes(current_time_str)
            current_time = minutes_to_time(current_min + transfer_buffer)
        else:
            timed_segments.append({
                "from": from_station_ja,
                "to": to_station_ja,
                "railway": railway,
                "departure_time": None,
                "note": f"時刻表データなし (検索: {from_station_en})"
            })

    # Calculate actual total duration based on first departure and last arrival
    actual_total_time = route_result.get("total_time")
    
    if timed_segments:
        # Find first segment with valid departure time
        first_valid_seg = next((s for s in timed_segments if s.get("departure_time")), None)
        # Find last segment with valid arrival time
        last_valid_seg = next((s for s in reversed(timed_segments) if s.get("arrival_time")), None)
        
        if first_valid_seg and last_valid_seg:
            start_t = first_valid_seg["departure_time"]
            end_t = last_valid_seg["arrival_time"]
            
            start_m = time_to_minutes(start_t)
            end_m = time_to_minutes(end_t)
            
            if end_m < start_m:
                end_m += 24 * 60
            
            actual_total_time = round(float(end_m - start_m), 2)
            
    return {
        "from": route_result.get("from"),
        "to": route_result.get("to"),
        "theoretical_time": actual_total_time, # Now represents actual total travel duration
        "transfers": route_result.get("transfers"),
        "requested_departure": departure_time,
        "segments": timed_segments
    }
