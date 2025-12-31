"""
Route Graph for theoretical fastest route search.
Builds a graph from ODPT Station and Railway data,
and implements Dijkstra's algorithm for shortest path.
"""

from collections import defaultdict
import heapq
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

API_KEY = os.getenv("ODPT_ACCESS_TOKEN")
BASE_URL = "https://api-challenge.odpt.org/api/v4"
TRAVEL_TIMES_FILE = os.path.join(os.path.dirname(__file__), "travel_times.json")


class RouteGraph:
    def __init__(self):
        self.edges = defaultdict(list)  # station_id -> [(to_station_id, time, type), ...]
        self.station_info = {}  # station_id -> {name, railway, ...}
        self.station_by_name = defaultdict(list)  # station_name -> [station_id, ...]
        self.railways = {}  # railway_id -> {name, stations, ...}
        self.is_built = False


    def build_from_odpt(self):
        """Fetch ODPT data and build the graph."""
        if not API_KEY:
            raise EnvironmentError("ODPT_ACCESS_TOKEN is not set")

        print("Fetching station data...")
        stations = self._fetch_stations()
        print(f"  -> {len(stations)} stations fetched")

        print("Fetching railway data...")
        railways = self._fetch_railways()
        print(f"  -> {len(railways)} railways fetched")

        print("Building graph...")
        self._build_nodes(stations)
        self._build_ride_edges(railways)
        self._build_transfer_edges()
        
        self.is_built = True
        print(f"Graph built: {len(self.station_info)} nodes, {sum(len(e) for e in self.edges.values())} edges")

    def _fetch_stations(self) -> list:
        """Fetch stations from ODPT API for all supported operators."""
        operators = [
            "odpt.Operator:JR-East",
            "odpt.Operator:TokyoMetro",
            "odpt.Operator:Toei",
        ]
        all_stations = []
        for operator in operators:
            try:
                url = f"{BASE_URL}/odpt:Station"
                params = {
                    "odpt:operator": operator,
                    "acl:consumerKey": API_KEY
                }
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                all_stations.extend(data)
                print(f"    {operator.split(':')[-1]}: {len(data)} stations")
            except Exception as e:
                print(f"    {operator.split(':')[-1]}: Error - {e}")
        return all_stations

    def _fetch_railways(self) -> list:
        """Fetch railways from ODPT API for all supported operators."""
        operators = [
            "odpt.Operator:JR-East",
            "odpt.Operator:TokyoMetro",
            "odpt.Operator:Toei",
        ]
        all_railways = []
        for operator in operators:
            try:
                url = f"{BASE_URL}/odpt:Railway"
                params = {
                    "odpt:operator": operator,
                    "acl:consumerKey": API_KEY
                }
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                all_railways.extend(data)
                print(f"    {operator.split(':')[-1]}: {len(data)} railways")
            except Exception as e:
                print(f"    {operator.split(':')[-1]}: Error - {e}")
        return all_railways

    def _build_nodes(self, stations: list):
        """Build station nodes from ODPT station data."""
        for station in stations:
            station_id = station.get("owl:sameAs")
            title = station.get("odpt:stationTitle", {})
            name_ja = title.get("ja", station.get("dc:title", ""))
            name_en = title.get("en", "")
            railway = station.get("odpt:railway")

            self.station_info[station_id] = {
                "id": station_id,
                "name_ja": name_ja,
                "name_en": name_en,
                "railway": railway
            }
            self.station_by_name[name_ja].append(station_id)

    def _build_ride_edges(self, railways: list):
        """Build ride edges from railway station order."""
        
        # Load travel times from DB into a dictionary for fast lookup
        # Key: (from_simple_name, to_simple_name) -> time_minutes
        travel_times = {}
        try:
            from db.database import SessionLocal
            from db.models import StationInterval
            db = SessionLocal()
            intervals = db.query(StationInterval).all()
            for inv in intervals:
                travel_times[(inv.from_station, inv.to_station)] = inv.time_minutes
            db.close()
            print(f"Loaded {len(travel_times)} travel time intervals from DB")
        except Exception as e:
            print(f"Warning: Could not load travel times from DB: {e}")

        for railway in railways:
            railway_id = railway.get("owl:sameAs")
            title = railway.get("odpt:railwayTitle", {})
            name_ja = title.get("ja", railway.get("dc:title", ""))
            station_order = railway.get("odpt:stationOrder", [])

            self.railways[railway_id] = {
                "id": railway_id,
                "name_ja": name_ja,
                "stations": [s["odpt:station"] for s in station_order]
            }

            # Add edges between adjacent stations
            for i in range(len(station_order) - 1):
                from_station = station_order[i]["odpt:station"]
                to_station = station_order[i + 1]["odpt:station"]
                
                # Look up actual travel time, default to 3 minutes if not found
                # Match using simplified names (last part of ID)
                from_simple = from_station.split(".")[-1]
                to_simple = to_station.split(".")[-1]
                
                time_forward = travel_times.get((from_simple, to_simple), 3.0)
                time_backward = travel_times.get((to_simple, from_simple), 3.0)

                # Bidirectional edges with actual times (or default)
                self.edges[from_station].append({
                    "to": to_station,
                    "time": time_forward,
                    "type": "ride",
                    "railway": railway_id
                })
                self.edges[to_station].append({
                    "to": from_station,
                    "time": time_backward,
                    "type": "ride",
                    "railway": railway_id
                })

    def _build_transfer_edges(self):
        """Build transfer edges for same-name stations (0 minute transfer)."""
        for name, station_ids in self.station_by_name.items():
            if len(station_ids) > 1:
                # Add transfer edges between all stations with the same name
                for i, s1 in enumerate(station_ids):
                    for s2 in station_ids[i + 1:]:
                        # Transfer time = 0 (theoretical)
                        self.edges[s1].append({
                            "to": s2,
                            "time": 0,
                            "type": "transfer"
                        })
                        self.edges[s2].append({
                            "to": s1,
                            "time": 0,
                            "type": "transfer"
                        })

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

    def find_route(self, from_query: str, to_query: str, transfer_buffer: int = 0) -> dict:
        """
        Find shortest route using Dijkstra's algorithm.
        
        Args:
            from_query: Station name or ID
            to_query: Station name or ID
            transfer_buffer: Additional time for transfers (minutes)
        
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

        # Dijkstra's algorithm
        # Priority queue: (total_time, current_station, path, transfers)
        pq = []
        for start in from_stations:
            heapq.heappush(pq, (0, start, [start], 0))

        visited = set()
        
        while pq:
            total_time, current, path, transfers = heapq.heappop(pq)

            if current in to_set:
                return self._build_result(path, total_time, transfers, transfer_buffer)

            if current in visited:
                continue
            visited.add(current)

            for edge in self.edges.get(current, []):
                next_station = edge["to"]
                if next_station in visited:
                    continue

                edge_time = edge["time"]
                new_transfers = transfers

                # Add transfer buffer for transfers
                if edge["type"] == "transfer":
                    edge_time += transfer_buffer
                    new_transfers += 1

                heapq.heappush(pq, (
                    total_time + edge_time,
                    next_station,
                    path + [next_station],
                    new_transfers
                ))

        return {"error": "No route found"}

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
                        "type": "ride"
                    })
                    railways_used.append(current_railway)

                # Start new segment
                segment_start = station_id
                segment_start_name = station_name
                current_railway = None

                # Find next railway
                if i + 1 < len(path):
                    for edge in self.edges.get(station_id, []):
                        if edge["to"] == path[i + 1] and edge["type"] == "ride":
                            current_railway = edge.get("railway")
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
                    "type": "ride"
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
            "path": [self.station_info.get(s, {}).get("name_ja", s) for s in path]
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
        route_graph.build_from_odpt()

