"""
Venue Service - Checks if route passes through event venue stations.
"""

import os
import json
from typing import Dict, List, Set

# Load venues data
VENUES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "venues.json")
VENUES = []
STATION_TO_VENUES: Dict[str, List[dict]] = {}

if os.path.exists(VENUES_FILE):
    with open(VENUES_FILE, "r", encoding="utf-8") as f:
        VENUES = json.load(f)
    
    # Build station -> venues index
    for venue in VENUES:
        for station in venue.get("stations", []):
            if station not in STATION_TO_VENUES:
                STATION_TO_VENUES[station] = []
            STATION_TO_VENUES[station].append(venue)


def get_venue_warnings(segments: List[dict]) -> dict:
    """
    Check route segments for venue stations.
    
    Args:
        segments: List of route segments with 'from', 'to', 'type' fields
        
    Returns:
        {
            "transfer_warnings": [...],  # Stations where user changes trains
            "passing_info": [...]        # Stations user passes through
        }
    """
    if not segments:
        return {"transfer_warnings": [], "passing_info": []}
    
    # Collect transfer stations and passing stations
    transfer_stations: Set[str] = set()
    passing_stations: Set[str] = set()
    
    for i, seg in enumerate(segments):
        from_station = seg.get("from", "")
        to_station = seg.get("to", "")
        seg_type = seg.get("type", "")
        
        # First segment: departure station (乗車駅)
        if i == 0 and from_station:
            transfer_stations.add(from_station)
        
        # Last segment: arrival station (降車駅)
        if i == len(segments) - 1 and to_station:
            transfer_stations.add(to_station)
        
        # Transfer segments
        if seg_type == "transfer":
            if from_station:
                transfer_stations.add(from_station)
            if to_station:
                transfer_stations.add(to_station)
        
        # All other stations are passing through
        if from_station and from_station not in transfer_stations:
            passing_stations.add(from_station)
        if to_station and to_station not in transfer_stations:
            passing_stations.add(to_station)
    
    # Remove transfer stations from passing (in case they were added before)
    passing_stations -= transfer_stations
    
    # Match with venues
    transfer_warnings = []
    for station in transfer_stations:
        if station in STATION_TO_VENUES:
            for venue in STATION_TO_VENUES[station]:
                transfer_warnings.append({
                    "station": station,
                    "venue": venue.get("name"),
                    "capacity": venue.get("capacity"),
                    "note": venue.get("note", "")
                })
    
    passing_info = []
    for station in passing_stations:
        if station in STATION_TO_VENUES:
            venues = STATION_TO_VENUES[station]
            passing_info.append({
                "station": station,
                "venues": [v.get("name") for v in venues]
            })
    
    # Sort by capacity (larger venues first)
    transfer_warnings.sort(key=lambda x: x.get("capacity", 0), reverse=True)
    
    return {
        "transfer_warnings": transfer_warnings,
        "passing_info": passing_info
    }
