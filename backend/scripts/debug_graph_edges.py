
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from services.route_graph import initialize_graph, get_graph

def debug_edges():
    print("Initializing graph...")
    initialize_graph()
    graph = get_graph()
    
    # Nishi-Funabashi ID
    station_names = ["西船橋", "飯田橋"]
    station_ids = []
    
    for name in station_names:
        ids = graph.find_station_by_name(name)
        print(f"{name}: {ids}")
        if ids:
            station_ids.append(ids[0]) # Just take first generic one
    
    nishi_funabashi = "odpt.Station:JR-East.ChuoSobuLocal.NishiFunabashi"
    if nishi_funabashi not in graph.edges:
        print(f"{nishi_funabashi} not in edges map?")
        # Try checking keys
        keys = [k for k in graph.edges.keys() if "NishiFunabashi" in k]
        print(f"Keys matching NishiFunabashi: {keys}")
        if keys:
            nishi_funabashi = keys[0]
            
    print(f"Edges from {nishi_funabashi}:")
    edges = graph.edges.get(nishi_funabashi, [])
    for edge in edges:
        to_id = edge["to"]
        to_name = graph.station_info.get(to_id, {}).get("name_ja", to_id)
        railway = graph.station_info.get(to_id, {}).get("railway", "Unknown")
        time = edge["time"]
        print(f"  -> {to_name} ({to_id}) via {railway} : {time} mins")

if __name__ == "__main__":
    debug_edges()
