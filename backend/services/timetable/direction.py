
"""
Direction determination logic for timetable search.
"""
from typing import Optional
from sqlalchemy.orm import Session
from db.models import StationOrder


def get_expected_direction(db: Session, railway_name: str, from_station: str, to_station: str) -> Optional[str]:
    """
    Determine expected direction (Inbound/Outbound) based on station order.
    
    Returns:
        "Outbound" if to_station has higher index than from_station
        "Inbound" if to_station has lower index
        None if cannot determine
    """
    # Get station indices
    from_record = db.query(StationOrder).filter(
        StationOrder.railway_name == railway_name,
        StationOrder.station_name == from_station
    ).first()
    
    to_record = db.query(StationOrder).filter(
        StationOrder.railway_name == railway_name,
        StationOrder.station_name == to_station
    ).first()
    
    if from_record and to_record:
        # Special handling for Yamanote Line (Circular)
        if "Yamanote" in railway_name:
            return _get_yamanote_direction(from_record.station_index, to_record.station_index)
            
        if to_record.station_index > from_record.station_index:
            return "Outbound"  # Higher index = Outbound direction
        else:
            return "Inbound"  # Lower index = Inbound direction
    
    return None


def _get_yamanote_direction(from_idx: int, to_idx: int) -> str:
    """
    Determine direction for Yamanote line considering circular loop.
    Station count is roughly 30.
    
    Order in DB (Osaki -> Shibuya -> Ikebukuro -> Tokyo -> Shinagawa)
    Increasing Index = Clockwise = Outbound (Sotomawari)
    Decreasing Index = Counter-Clockwise = Inbound (Uchimawari)
    """
    diff = to_idx - from_idx
    half_circle = 15  # Approx half of 30 stations
    
    # Check simple case (short distance)
    if abs(diff) <= half_circle:
        if diff > 0:
            return "Outbound"  # Clockwise (Sotomawari)
        else:
            return "Inbound"   # Counter-Clockwise (Uchimawari)
    else:
        # Wrap around case (long distance in index, but short in loop)
        # e.g. 30 -> 1 (diff = -29) -> effectively +1 -> Outbound
        # e.g. 1 -> 30 (diff = +29) -> effectively -1 -> Inbound
        if diff > 0:
            return "Inbound"   # Effectively going backward across boundary
        else:
            return "Outbound"  # Effectively going forward across boundary


def get_heuristic_direction(to_station: str, from_station: str) -> Optional[str]:
    """Fallback direction based on terminal stations (when DB data missing)."""
    to_lower = to_station.lower()
    
    # Common terminal stations for each direction
    tokyo_side = {
        "tokyo", "shinagawa", "ueno", "akihabara", "kinshicho", 
        "shinjuku", "shibuya", "ikebukuro", "yokohama", "ofuna"
    }
    chiba_side = {
        "chiba", "tsudanuma", "funabashi", "inage", "nishifunabashi",
        "kimitsu", "narita", "naritaairport"
    }
    
    if any(s in to_lower for s in tokyo_side):
        return "Inbound"
    elif any(s in to_lower for s in chiba_side):
        return "Outbound"
        
    return None
