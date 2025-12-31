
"""
Stations and Railways API router.
"""
from fastapi import APIRouter
from services.route_graph import get_graph

router = APIRouter()


@router.get("/stations")
def get_stations():
    """Get all available stations in the graph."""
    graph = get_graph()
    stations = set()
    
    # Extract unique station names
    for info in graph.station_info.values():
        name = info.get("name_ja") or info.get("name", "")
        if name:
            stations.add(name)
            
    return sorted(list(stations))


@router.get("/railways")
def get_railways():
    """Get all available railways."""
    graph = get_graph()
    railways = set()
    
    # Extract unique railway names from edges
    for from_station, edge_list in graph.edges.items():
        for edge in edge_list:
            railway = edge.get("railway")
            # Filter out station IDs (railway usually looks like "odpt.Railway:Company.Line")
            if railway and "Railway" in railway:
                # Optionally resolve to simpler name if needed, but returning full ID is fine for now
                # Or if we have a railway map in graph, use it
                railways.add(railway)
            
    return sorted(list(railways))
