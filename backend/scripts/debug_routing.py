"""Debug the routing graph to see why find_routes returns 0"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.routing import get_graph

def main():
    print("=== Debug Routing Graph ===\n")
    
    graph = get_graph()
    
    # Check what stations exist
    print("Checking stations in graph...")
    
    if hasattr(graph, 'stations'):
        print(f"  Total stations: {len(graph.stations)}")
        # Look for stations containing "東京" or "新宿"
        tokyo_matches = [s for s in graph.stations if '東京' in s]
        shinjuku_matches = [s for s in graph.stations if '新宿' in s]
        print(f"  Stations with '東京': {tokyo_matches[:5]}")
        print(f"  Stations with '新宿': {shinjuku_matches[:5]}")
    else:
        print("  No 'stations' attribute")
    
    if hasattr(graph, 'station_info'):
        print(f"  station_info entries: {len(graph.station_info)}")
    
    # Check graph internals
    if hasattr(graph, '_graph'):
        print(f"  _graph nodes: {len(graph._graph.nodes)}")
    
    # Try different station names
    print("\n2. Trying different station name formats...")
    test_pairs = [
        ("東京", "新宿"),
        ("Tokyo", "Shinjuku"),
        ("odpt.Station:JR-East.Yamanote.Tokyo", "odpt.Station:JR-East.Yamanote.Shinjuku"),
    ]
    
    for from_s, to_s in test_pairs:
        routes = graph.find_routes(from_s, to_s, limit=1)
        print(f"  {from_s} -> {to_s}: {len(routes)} routes")
    
    # Check if graph has any data at all
    print("\n3. Checking graph structure...")
    for attr in dir(graph):
        if not attr.startswith('_'):
            val = getattr(graph, attr)
            if isinstance(val, (dict, list, set)):
                print(f"  {attr}: {type(val).__name__} with {len(val)} items")

if __name__ == "__main__":
    main()
