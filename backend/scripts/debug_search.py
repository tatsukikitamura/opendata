"""
Debug script to diagnose why search is returning 0 routes.
"""
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.routing import get_graph, initialize_graph
from services.timetable.core import search_route_with_times
from db.database import SessionLocal

def main():
    print("=== Debug Search ===\n")
    
    # Force initialize
    print("1. Initializing graph...")
    initialize_graph()
    graph = get_graph()
    print(f"   is_built: {graph.is_built}")
    print(f"   station_info: {len(graph.station_info)}")
    
    # 2. Test theoretical route finding with actual query
    from_station = "千葉"
    to_station = "高田馬場"
    
    print(f"\n2. Finding routes: {from_station} -> {to_station}")
    routes = graph.find_routes(from_station, to_station, limit=5)
    print(f"   Found: {len(routes)} routes")
    
    if not routes:
        print("   ERROR: No theoretical routes found!")
        # Check if stations exist
        from_matches = graph.find_station_by_name(from_station)
        to_matches = graph.find_station_by_name(to_station)
        print(f"   Stations matching '{from_station}': {from_matches}")
        print(f"   Stations matching '{to_station}': {to_matches}")
        return
    
    # Show first route
    for i, route in enumerate(routes[:2]):
        segs = route.get("segments", [])
        print(f"   Route {i+1}: {len(segs)} segments")
        for seg in segs:
            print(f"      {seg.get('from')} -> {seg.get('to')} via {seg.get('railway')}")
    
    # 3. Test timetable lookup
    print("\n3. Testing timetable lookup...")
    db = SessionLocal()
    
    try:
        now = datetime.now()
        # Sunday = 6, Saturday = 5
        if now.weekday() == 6:
            weekday_type = "Holiday"
        elif now.weekday() == 5:
            weekday_type = "Saturday"
        else:
            weekday_type = "Weekday"
        print(f"   Today is weekday={now.weekday()}, using type: {weekday_type}")
        
        # Build station map
        station_map = {}
        if hasattr(graph, "station_info"):
            for station_id, info in graph.station_info.items():
                name_ja = info.get("name_ja", "")
                name_en = info.get("name_en", "")
                if name_ja and name_en:
                    station_map[name_ja] = name_en
            print(f"   Station map entries: {len(station_map)}")
        
        # Try first route
        result = search_route_with_times(
            db, routes[0], "18:00", weekday_type,
            transfer_buffer=5, station_name_map=station_map
        )
        
        print(f"   Result keys: {list(result.keys())}")
        
        if "error" in result:
            print(f"   ERROR: {result['error']}")
        else:
            segments = result.get("segments", [])
            print(f"   Segments with times: {len(segments)}")
            
            null_dep_count = 0
            for seg in segments:
                dep = seg.get("departure_time")
                arr = seg.get("arrival_time")
                if dep is None:
                    null_dep_count += 1
                print(f"      {seg.get('from')} -> {seg.get('to')}: dep={dep}, arr={arr}")
            
            print(f"\n   Null departure times: {null_dep_count}")
            if null_dep_count > 0:
                print("   WARNING: Routes with null departure are filtered out!")
                
    finally:
        db.close()
    
    print("\n=== Done ===")

if __name__ == "__main__":
    main()
