
"""
Train finding logic using actual timetable data.
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from db.models import StationDeparture, StationOrder
from .direction import get_expected_direction, get_heuristic_direction


def get_arrival_time(
    db: Session,
    train_number: str,
    railway_name: str,
    station_name: str,
    weekday: str = "Weekday"
) -> Optional[str]:
    """
    Get the arrival time of a train at a specific station.
    """
    record = db.query(StationDeparture).filter(
        StationDeparture.train_number == train_number,
        StationDeparture.railway_name == railway_name,
        StationDeparture.station_name.ilike(station_name),
        StationDeparture.weekday_type == weekday
    ).first()
    
    if record:
        return record.departure_time
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
    unreliable_direction_railways = {"ChuoSobuLocal"}
    
    # For ChuoSobuLocal, get station indices for destination-based filtering
    from_idx = None
    to_idx = None
    if railway_en in unreliable_direction_railways and expected_direction:
        from_rec = db.query(StationOrder).filter(
            StationOrder.railway_name == railway_en,
            StationOrder.station_name == from_station
        ).first()
        to_rec = db.query(StationOrder).filter(
            StationOrder.railway_name == railway_en,
            StationOrder.station_name == to_station
        ).first()
        if from_rec and to_rec:
            from_idx = from_rec.station_index
            to_idx = to_rec.station_index
    
    # Filter by direction
    for departure in departures:
        dest = (departure.destination_station or "").lower()
        
        # For unreliable direction railways, use destination-based filtering
        if railway_en in unreliable_direction_railways:
            if from_idx is not None and to_idx is not None:
                # Get destination station index
                dest_rec = db.query(StationOrder).filter(
                    StationOrder.railway_name == railway_en,
                    StationOrder.station_name.ilike(dest)
                ).first()
                
                if dest_rec:
                    dest_idx = dest_rec.station_index
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
        
        return {
            "departure_time": departure.departure_time,
            "railway": departure.railway_name,
            "train_type": departure.train_type,
            "destination": departure.destination_station,
            "train_number": departure.train_number,
            "direction": departure.direction
        }
    
    return None
