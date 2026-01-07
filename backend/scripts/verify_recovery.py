import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Load .env
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

from services.routing import route_graph, initialize_graph, get_graph

# Force graph reload just in case
initialize_graph()

def verify():
    print("Testing route search...")
    
    # Check graph
    if not route_graph.is_built:
        print("CRITICAL: Graph not initialized!")
        return

    from_st = "odpt.Station:JR-East.Sobumain.Chiba"
    to_st = "odpt.Station:JR-East.ChuoRapid.Tokyo"
    
    print(f"Resolving {from_st}...")
    ids = route_graph._resolve_station(from_st)
    print(f"  Result: {ids}")
    
    print(f"Resolving {to_st}...")
    ids_to = route_graph._resolve_station(to_st)
    print(f"  Result: {ids_to}")
    
    # Try searching by name if ID fails
    if not ids:
        print("Searching by name '千葉'...")
        ids = route_graph.find_station_by_name("千葉")
        print(f"  Result: {ids}")
        if ids: from_st = ids[0]

    if not ids_to:
        print("Searching by name '東京'...")
        ids_to = route_graph.find_station_by_name("東京")
        print(f"  Result: {ids_to}")
        if ids_to: to_st = ids_to[0]
        
    print(f"Searching route from {from_st} to {to_st}...")
    routes = route_graph.find_routes(from_st, to_st, limit=1)
    
    if not routes:
        print("CRITICAL: No routes found!")
        return
        
    print(f"Found {len(routes)} theoretical routes.")
    
    # Test Time-based search (Fallback verification)
    from services.timetable.core import search_route_with_times
    from db.database import SessionLocal
    
    db = SessionLocal()
    try:
        print("Applying timetable (expecting fallback)...")
        timed = search_route_with_times(db, routes[0], "08:00")
        
        segments = timed.get("segments", [])
        print(f"Timed segments: {len(segments)}")
        if not segments:
            print("CRITICAL: No timed segments!")
        else:
            first = segments[0]
            print(f"First segment departure: {first.get('departure_time')}")
            print(f"First segment note: {first.get('note')}")
            
            if first.get('departure_time'):
                print("Recovery verification PASSED (Fallback active).")
            else:
                 print("CRITICAL: Departure time is None despite fallback!")

    finally:
        db.close()

if __name__ == "__main__":
    verify()
