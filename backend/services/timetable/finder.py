
"""
Train finding logic using actual timetable data.
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from db.models import StationDeparture, StationOrder
from .direction import get_expected_direction, get_heuristic_direction

# Cache for get_arrival_time - timetable data is static
_arrival_time_cache = {}


def get_arrival_time(
    db: Session,
    train_number: str,
    railway_name: str,
    station_name: str,
    weekday: str = "Weekday",
    after_time: str = None
) -> Optional[str]:
    """
    Get the arrival time of a train at a specific station.
    If after_time is provided, ensures the arrival is after that time (handling day crossing).
    """
    # OPTIMIZATION: Check cache first (timetable data is static)
    cache_key = (train_number, station_name.lower(), weekday, after_time)
    if cache_key in _arrival_time_cache:
        return _arrival_time_cache[cache_key]
    
    base_query = db.query(StationDeparture).filter(
        StationDeparture.train_number == train_number,
        StationDeparture.station_name.ilike(station_name),
        StationDeparture.weekday_type == weekday
    )
    
    # Try finding exact railway match first
    entries = base_query.filter(StationDeparture.railway_name == railway_name).all()
    
    if not entries:
        # Fallback: Try ANY railway (fixing direct service name changes)
        entries = base_query.all()
        
    if not entries:
        _arrival_time_cache[cache_key] = None
        return None
        
    if not after_time:
        result = entries[0].departure_time
        _arrival_time_cache[cache_key] = result
        return result
    
    # Logic to find the correct entry relative to after_time
    # Candidates:
    # 1. Same day, time > after_time
    # 2. Next day (time < after_time, usually early morning)
    
    # Sort entries by time
    entries.sort(key=lambda x: x.departure_time)
    
    # 1. Look for same day future time
    for entry in entries:
        if entry.departure_time > after_time:
            _arrival_time_cache[cache_key] = entry.departure_time
            return entry.departure_time
            
    # 2. If not found, look for early morning time (day crossing)
    # Assuming the train arrives the next day (e.g. 00:15)
    # We pick the earliest time that is significantly smaller than after_time
    # But only if it makes sense (e.g., < 04:00)
    for entry in entries:
        if entry.departure_time < "04:00": # Heuristic for next day
            _arrival_time_cache[cache_key] = entry.departure_time
            return entry.departure_time
             
    # If no suitable time found, return None (invalid direction or loop)
    _arrival_time_cache[cache_key] = None
    return None


def find_train_for_segment(
    db: Session,
    from_station: str,
    to_station: str,
    railway: str,
    after_time: str,
    weekday: str = "Weekday"
) -> Optional[Dict]:
    """
    Find the first train on a specific railway from a station after a given time.
    Includes direction filtering to ensure the train goes towards the destination.
    """
    # Get English railway name (from shared constants)
    from services.constants import RAILWAY_JA_TO_EN
    railway_en = RAILWAY_JA_TO_EN.get(railway, railway)
    
    expected_direction = get_expected_direction(db, railway_en, from_station, to_station)
    
    # Try alternate station names if direct lookup likely fails (e.g. "Shin-Okubo" vs "ShinOkubo")
    search_stations = [from_station]
    if "-" in from_station:
        search_stations.append(from_station.replace("-", ""))
        
    departures = []
    found_station_name = from_station
    
    for station_name in search_stations:
        # First try detailed direction if available (but for ChuoSobuLocal we might skip)
        query = db.query(StationDeparture).filter(
            StationDeparture.station_name.ilike(station_name),
            StationDeparture.railway_name == railway_en,
            StationDeparture.departure_time >= after_time,
            StationDeparture.weekday_type == weekday
        )
        results = query.order_by(StationDeparture.departure_time).limit(30).all()
        if results:
            departures = results
            found_station_name = station_name
            # If we found matches with this name, stick with it for direction checks too
            if station_name != from_station:
                 # Update expected direction with correct name if needed
                 new_dir = get_expected_direction(db, railway_en, station_name, to_station.replace("-", "") if "-" in to_station else to_station)
                 if new_dir:
                     expected_direction = new_dir
            break

    if expected_direction is None:
        expected_direction = get_heuristic_direction(to_station, from_station)
    
    # Railways where direction field is unreliable (all marked as one direction)
    # Using station index based filtering instead of direction field for these
    unreliable_direction_railways = {"ChuoSobuLocal", "Keiyo"}
    
    # For ChuoSobuLocal and similar, get station indices for destination-based filtering
    from_idx = None
    to_idx = None
    station_idx_map = {}  # Pre-fetched station order map for O(1) lookups
    
    if railway_en in unreliable_direction_railways and expected_direction:
        # OPTIMIZATION: Fetch ALL station orders for this railway in one query
        # This avoids 16+ queries inside the loop (was the main bottleneck)
        all_orders = db.query(StationOrder).filter(
            StationOrder.railway_name == railway_en
        ).all()
        
        # Build lookup dictionary for O(1) access
        for rec in all_orders:
            station_idx_map[rec.station_name.lower()] = rec.station_index
            # Also add without hyphen for name variations
            if "-" in rec.station_name:
                station_idx_map[rec.station_name.replace("-", "").lower()] = rec.station_index
        
        # Get from/to indices from the map
        from_idx = station_idx_map.get(from_station.lower())
        to_idx = station_idx_map.get(to_station.lower())
        
        # Try alternate names if not found
        if from_idx is None and "-" in from_station:
            from_idx = station_idx_map.get(from_station.replace("-", "").lower())
        if to_idx is None and "-" in to_station:
            to_idx = station_idx_map.get(to_station.replace("-", "").lower())
    
    # Filter by direction
    arrival_checks_count = 0
    for departure in departures:
        dest = (departure.destination_station or "").lower()
        
        # For unreliable direction railways, use destination-based filtering
        if railway_en in unreliable_direction_railways:
            if from_idx is not None and to_idx is not None:
                # OPTIMIZATION: Use pre-fetched map instead of DB query
                dest_idx = station_idx_map.get(dest)
                if dest_idx is None and "-" in dest:
                    dest_idx = station_idx_map.get(dest.replace("-", ""))
                
                if dest_idx is not None:
                    # If going west (to_idx > from_idx), destination should be >= to_idx
                    # If going east (to_idx < from_idx), destination should be <= to_idx
                    if to_idx > from_idx:  # Going west (higher index)
                        if dest_idx < to_idx:
                            continue  # Destination is east of target, wrong way
                    else:  # Going east (lower index)
                        if dest_idx > to_idx:
                            continue  # Destination is west of target, wrong way
        else:
            # Normal direction check for reliable railways
            if expected_direction and departure.direction != expected_direction:
                continue
        
        if railway_en == "Yamanote":
            # Yamanote direction is reliable (Inbound/Outbound)
            # Just ensure we don't accidentally filter out if direction is missing
            if not departure.direction:
                continue # Or pass? Better to be safe.
            # Normal check will handle it below (or above loop)
            pass
        
        # Verify that this train actually stops at the destination station
        # This prevents picking through-trains that skip intermediate stops on this railway (e.g. Metro through service)
        # Handle station name variations (e.g. Nishi-Funabashi -> NishiFunabashi)
        check_to_stations = [to_station.lower()]
        if "-" in to_station:
            check_to_stations.append(to_station.replace("-", "").lower())
        
        arrival_check = None
        arrival_checks_count += 1
        
        # OPTIMIZATION: For unreliable direction railways where we already verified
        # the destination station is on the right path using station indices,
        # we can skip the expensive get_arrival_time DB call
        if railway_en in unreliable_direction_railways and from_idx is not None and to_idx is not None:
            # We already verified direction - just check destination matches
            train_dest = (departure.destination_station or "").lower()
            # Check if train destination is at or beyond our target station
            dest_ok = train_dest in check_to_stations
            if not dest_ok and dest_idx is not None:
                if to_idx > from_idx:
                    dest_ok = dest_idx >= to_idx  # Going west, destination should be >= target
                else:
                    dest_ok = dest_idx <= to_idx  # Going east, destination should be <= target
            if not dest_ok:
                continue
        else:
            # Normal verification path for other railways
            for ts in check_to_stations:
                arrival_check = get_arrival_time(db, departure.train_number, departure.railway_name, ts, weekday)
                if arrival_check:
                    break
            
            # If no arrival record found, check if destination station matches target
            # (Terminal stations don't have departure records, only arrival)
            if not arrival_check:
                train_dest = (departure.destination_station or "").lower()
                if train_dest not in check_to_stations:
                    continue

        return {
            "departure_time": departure.departure_time,
            "railway": departure.railway_name,
            "train_type": departure.train_type,
            "destination": departure.destination_station,
            "train_number": departure.train_number,
            "direction": departure.direction
        }
    
    return None
