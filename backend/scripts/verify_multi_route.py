
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from services.route_graph import initialize_graph, get_graph

def verify_multi_route():
    print("Initializing graph...")
    initialize_graph()
    graph = get_graph()
    
    start = "千葉"
    end = "高田馬場"
    
    print(f"Finding routes from {start} to {end}...")
    
    routes = graph.find_routes(start, end, limit=3)
    
    print(f"Found {len(routes)} routes.")
    
    for i, r in enumerate(routes):
        path = r["path"]
        railways = set()
        for j in range(len(path)-1):
            s1 = path[j]
            s2 = path[j+1]
            # Find edge railway
             # Using simplified edge access if possible, or build_result logic
            pass
        
        # Print summary
        segments = r["segments"]
        seg_summary = " -> ".join([
            f"{s['railway'] if 'railway' in s else 'Transfer'}({s['from']}->{s['to']})" 
            for s in segments
        ])
        print(f"Route {i+1}: {r['theoretical_time']} mins : {seg_summary}")

    if len(routes) >= 2:
        print("SUCCESS: Found multiple routes.")
    else:
        print("WARNING: Found only 1 route (or 0).")

if __name__ == "__main__":
    verify_multi_route()
