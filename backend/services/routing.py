"""
Route Graph for theoretical fastest route search.
Builds a graph from ODPT Station and Railway data,
and implements Dijkstra's algorithm for shortest path.
"""


from db.database import SessionLocal
from db.models import Station, Railway, RouteEdge
import os
from collections import defaultdict
import heapq

# Removed unused imports and constants


API_KEY = os.getenv("ODPT_ACCESS_TOKEN")
from .constants import (
    ODPT_BASE_URL as BASE_URL,
    TRAVEL_TIMES_FILE,
    OPERATOR_JR_EAST,
    OPERATOR_TOKYO_METRO,
    OPERATOR_TOEI,
    ALL_OPERATORS,
    GTFS_METRO_CODES,
    GTFS_TOEI_CODES,
    METRO_TOEI_RAILWAY_INFO,
    RAILWAY_JA_TO_EN
)

API_KEY = os.getenv("ODPT_ACCESS_TOKEN")



class RouteGraph:
    def __init__(self):
        self.edges = defaultdict(list)  # station_id -> [(to_station_id, time, type), ...]
        self.station_info = {}  # station_id -> {name, railway, ...}
        self.station_by_name = defaultdict(list)  # station_name -> [station_id, ...]
        self.railways = {}  # railway_id -> {name, stations, ...}
        self.is_built = False

    def load_from_db(self):
        """Build the graph from the database."""
        print("Loading graph from DB...")
        db = SessionLocal()
        try:
            # 1. Load Railways
            railways = db.query(Railway).all()
            for r in railways:
                self.railways[r.id] = {
                    "id": r.id,
                    "name_ja": r.name_ja,
                    "name_en": r.name_en
                }
            print(f"  Loaded {len(railways)} railways.")

            # 2. Load Stations
            stations = db.query(Station).all()
            for s in stations:
                self.station_info[s.id] = {
                    "id": s.id,
                    "name_ja": s.name_ja,
                    "name_en": s.name_en,
                    "railway": s.railway_id,
                    "lat": s.lat,
                    "lon": s.lon
                }
                self.station_by_name[s.name_ja].append(s.id)
            print(f"  Loaded {len(stations)} stations.")

            # 3. Load Edges
            edges = db.query(RouteEdge).all()
            count = 0
            for e in edges:
                self.edges[e.from_station_id].append({
                    "to": e.to_station_id,
                    "time": e.time_minutes,
                    "type": e.type,
                    "railway": e.railway_id
                })
                count += 1
            print(f"  Loaded {count} edges.")

            self.is_built = True

        except Exception as e:
            print(f"Error loading graph from DB: {e}")
        finally:
            db.close()

    def find_station_by_name(self, name: str) -> list:
        """Find station IDs by Japanese name."""
        # Exact match
        if name in self.station_by_name:
            return self.station_by_name[name]
        
        # Partial match
        matches = []
        for station_name, ids in self.station_by_name.items():
            if name in station_name:
                matches.extend(ids)
        return matches

    def find_route(self, from_query: str, to_query: str, transfer_buffer: int = 0, penalty_edges: set = None) -> dict:
        """
        Find shortest route using Dijkstra's algorithm.
        
        Args:
            from_query: Station name or ID
            to_query: Station name or ID
            transfer_buffer: Additional time for transfers (minutes)
            penalty_edges: Set of (u, v) tuples to penalize (2.0x cost)
        
        Returns:
            Route information including path, total time, and details
        """
        if not self.is_built:
            return {"error": "Graph not built. Call build_from_odpt() first."}

        # Resolve station names to IDs
        from_stations = self._resolve_station(from_query)
        to_stations = self._resolve_station(to_query)

        if not from_stations:
            return {"error": f"Station not found: {from_query}"}
        if not to_stations:
            return {"error": f"Station not found: {to_query}"}

        to_set = set(to_stations)
        penalty_edges = penalty_edges or set()

        # Dijkstra's algorithm with parent tracking (optimized)
        # Priority queue: (total_time, current_station, transfers)
        pq = []
        parent = {}  # station -> (prev_station, total_time, transfers)
        
        for start in from_stations:
            heapq.heappush(pq, (0, start, 0))
            parent[start] = (None, 0, 0)

        visited = set()
        
        while pq:
            total_time, current, transfers = heapq.heappop(pq)

            if current in to_set:
                # Reconstruct path from parent chain
                path = []
                node = current
                while node is not None:
                    path.append(node)
                    node = parent[node][0]
                path.reverse()
                return self._build_result(path, total_time, transfers, transfer_buffer)

            if current in visited:
                continue
            visited.add(current)

            for edge in self.edges[current]:
                next_station = edge["to"]
                if next_station in visited:
                    continue

                edge_time = edge["time"]
                
                if not penalty_edges:
                    pass
                
                if (current, next_station) in penalty_edges or (next_station, current) in penalty_edges:
                    edge_time *= 5.0
                
                new_transfers = transfers

                # Add transfer buffer for transfers
                if edge["type"] == "transfer":
                    edge_time += transfer_buffer
                    new_transfers += 1

                new_time = total_time + edge_time
                
                # Only add if we haven't found a better path to this station
                if next_station not in parent or new_time < parent[next_station][1]:
                    parent[next_station] = (current, new_time, new_transfers)
                    heapq.heappush(pq, (new_time, next_station, new_transfers))

        return {"error": "No route found"}

    def find_routes(self, from_query: str, to_query: str, limit: int = 5) -> list:
        """
        Find up to 'limit' diverse routes using Hybrid Strategy:
        1. Variable Transfer Buffer: [0, 5, 20] minutes
        2. Penalty Method: If < limit routes, penalize existing paths and retry.
        """
        routes = []
        seen_paths = set()
        
        # Step 1: Variable Transfer Buffer Strategy
        # 0: Fastest (accept transfers)
        # 5: Balanced (standard)
        # 10: Minimum transfers (1 transfer = 10min penalty)
        buffers = [0, 5, 10]
        
        for buf in buffers:
            if len(routes) >= limit:
                break
                
            # No penalties for this phase, just varying buffer
            result = self.find_route(from_query, to_query, transfer_buffer=buf, penalty_edges=set())
            
            if "error" in result:
                continue
                
            path_ids = tuple(result.get("path_ids", []))
            if not path_ids or path_ids in seen_paths:
                continue
                
            seen_paths.add(path_ids)
            routes.append(result)

        # Step 2: Penalty Method (Fill remaining slots)
        # If we still need routes, use penalty method on top of standard buffer (5min)
        penalty_edges = set()
        
        # Initialize penalties with paths found so far
        for r in routes:
            path_list = r.get("path_ids", [])
            for i in range(len(path_list) - 1):
                u, v = path_list[i], path_list[i+1]
                penalty_edges.add((u, v))
                penalty_edges.add((v, u))

        # Try to find more routes until we hit the limit
        # We allow up to known retries to find distinct paths
        extra_attempts = (limit - len(routes)) * 2
        
        for _ in range(extra_attempts):
            if len(routes) >= limit:
                break
                
            result = self.find_route(from_query, to_query, transfer_buffer=5, penalty_edges=penalty_edges)
            
            if "error" in result:
                break
            
            path_ids = tuple(result.get("path_ids", []))
            
            if not path_ids or path_ids in seen_paths:
                # If we found duplicates despite penalties, force penalize this path heavily
                # (Existing logic handles this somewhat by accumulating penalties, but let's be explicit)
                path_list = result.get("path_ids", [])
                for i in range(len(path_list) - 1):
                    u, v = path_list[i], path_list[i+1]
                    penalty_edges.add((u, v))
                    penalty_edges.add((v, u))
                continue
            else:
                seen_paths.add(path_ids)
                routes.append(result)
                
                # Add this new path to penalties for next iteration
                path_list = result.get("path_ids", [])
                for i in range(len(path_list) - 1):
                    u, v = path_list[i], path_list[i+1]
                    penalty_edges.add((u, v))
                    penalty_edges.add((v, u))
        
        # Sort routes by total time (theoretical)
        routes.sort(key=lambda x: x.get("theoretical_time", float("inf")))
        
        return routes

    def _resolve_station(self, query: str) -> list:
        """Resolve station name or ID to list of station IDs."""
        # If it looks like an ID, use directly
        if query.startswith("odpt.Station:"):
            if query in self.station_info:
                return [query]
            return []
        
        # Otherwise, search by name
        return self.find_station_by_name(query)

    def _build_result(self, path: list, total_time: int, transfers: int, transfer_buffer: int) -> dict:
        """Build the result dictionary from the path."""
        segments = []
        current_railway = None
        segment_start = None
        segment_start_name = None
        railways_used = []  # Track railways to count actual transfers

        current_segment_time = 0

        for i, station_id in enumerate(path):
            info = self.station_info.get(station_id, {})
            station_name = info.get("name_ja", station_id)

            if i == 0:
                segment_start = station_id
                segment_start_name = station_name
                # Find railway for first segment
                if i + 1 < len(path):
                    for edge in self.edges.get(station_id, []):
                        if edge["to"] == path[i + 1] and edge["type"] == "ride":
                            current_railway = edge.get("railway")
                            current_segment_time += edge.get("time", 0)
                            break
                continue

            # Check if this is a transfer
            is_transfer = False
            for edge in self.edges.get(path[i - 1], []):
                if edge["to"] == station_id and edge["type"] == "transfer":
                    is_transfer = True
                    break

            if is_transfer:
                # End current segment
                if current_railway:
                    railway_info = self.railways.get(current_railway, {})
                    segments.append({
                        "from": segment_start_name,
                        "to": self.station_info.get(path[i - 1], {}).get("name_ja", path[i - 1]),
                        "railway": railway_info.get("name_ja", current_railway),
                        "type": "ride",
                        "theoretical_time": current_segment_time
                    })
                    railways_used.append(current_railway)

                # Start new segment
                segment_start = station_id
                segment_start_name = station_name
                current_railway = None
                current_segment_time = 0

                # Find next railway
                if i + 1 < len(path):
                    for edge in self.edges.get(station_id, []):
                        if edge["to"] == path[i + 1] and edge["type"] == "ride":
                            current_railway = edge.get("railway")
                            current_segment_time += edge.get("time", 0)
                            break
            else:
                # Accumulate time for current segment if not transfer
                 if i + 1 < len(path):
                    for edge in self.edges.get(station_id, []):
                        if edge["to"] == path[i + 1] and edge["type"] == "ride":
                            # Only add if it's the same railway we are tracking
                            if edge.get("railway") == current_railway:
                                current_segment_time += edge.get("time", 0)
                            break

        # Add final segment
        if segment_start and path:
            last_station = path[-1]
            if segment_start != last_station and current_railway:
                railway_info = self.railways.get(current_railway, {})
                segments.append({
                    "from": segment_start_name,
                    "to": self.station_info.get(last_station, {}).get("name_ja", last_station),
                    "railway": railway_info.get("name_ja", current_railway),
                    "type": "ride",
                    "theoretical_time": current_segment_time
                })
                railways_used.append(current_railway)

        # Calculate actual transfers: number of railway changes (ride segments - 1)
        ride_segments = [s for s in segments if s["type"] == "ride"]
        actual_transfers = max(0, len(ride_segments) - 1)

        from_info = self.station_info.get(path[0], {})
        to_info = self.station_info.get(path[-1], {})

        return {
            "from": from_info.get("name_ja", path[0]),
            "to": to_info.get("name_ja", path[-1]),
            "total_time": total_time,
            "theoretical_time": total_time,
            "transfers": actual_transfers,
            "transfer_buffer": transfer_buffer,
            "segments": segments,
            "segments": segments,
            "path": [self.station_info.get(s, {}).get("name_ja", s) for s in path],
            "path_ids": path
        }

# Global instance
route_graph = RouteGraph()

def get_graph() -> RouteGraph:
    """Get the global route graph instance."""
    return route_graph

def initialize_graph():
    """Initialize the graph by building it from ODPT data."""
    print("Initializing route graph...")
    global route_graph
    if not route_graph.is_built:
        route_graph.load_from_db()


