"""Force initialize the graph and test"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.routing import initialize_graph, get_graph

print("Force initializing graph...")
initialize_graph()

graph = get_graph()
print(f"Graph is_built: {graph.is_built}")
print(f"Station info count: {len(graph.station_info)}")
print(f"Edges count: {len(graph.edges)}")

# Test search
routes = graph.find_routes('東京', '新宿', limit=1)
print(f"Routes found: {len(routes)}")
