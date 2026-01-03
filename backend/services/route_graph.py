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
import csv
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
        self._load_gtfs_railway_info() # Add Metro info
        print(f"  -> {len(railways)} railways fetched")

        print("Building graph...")
        # Incorporate GTFS stations
        gtfs_stations = self._load_gtfs_stations_data()
        print(f"  -> {len(gtfs_stations)} GTFS stations loaded")
        stations.extend(gtfs_stations)
        
        self._build_nodes(stations)
        self._build_ride_edges(railways)
        self._build_transfer_edges()
        
        # Load GTFS edges (accurate times)
        self._load_gtfs_edges()
        
        self.is_built = True
        print(f"Graph built: {len(self.station_info)} nodes, {sum(len(e) for e in self.edges.values())} edges")

    def _fetch_stations(self) -> list:
        """Fetch stations from ODPT API for all supported railways."""
        # Use railway list from constants or fetch dynamically?
        # For robustness, let's fetch railways first (already doing it in _fetch_railways),
        # but here we need station list.
        # Let's iterate over known operators but maybe handle pagination?
        # ODPT API doesn't use standard pagination header usually.
        # Instead, let's fetch by railway for Metro/Toei to be safe.
        
        # JR East usually works fine by operator (800+ stations).
        # Metro/Toei seems to fail.
        
        all_stations = []
        
        # 1. JR East (By Operator)
        try:
            url = f"{BASE_URL}/odpt:Station"
            params = {
                "odpt:operator": "odpt.Operator:JR-East",
                "acl:consumerKey": API_KEY
            }
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            all_stations.extend(data)
            print(f"    JR-East: {len(data)} stations")
        except Exception as e:
            print(f"    JR-East: Error - {e}")

        # 2. Metro & Toei (By Railway - to ensure completeness)
        # We need the railway IDs. Let's use the ones from constants if possible, 
        # OR we can rely on _fetch_railways having run effectively? No, _fetch_stations runs first.
        # Let's hardcode the operators to fetch Railway IDs first, then Stations.
        
        other_operators = [
            "odpt.Operator:TokyoMetro",
            "odpt.Operator:Toei"
        ]
        
        for operator in other_operators:
            try:
                # First get railways for this operator
                r_url = f"{BASE_URL}/odpt:Railway"
                r_params = {
                    "odpt:operator": operator,
                    "acl:consumerKey": API_KEY
                }
                r_resp = requests.get(r_url, params=r_params, timeout=30)
                r_resp.raise_for_status()
                railways = r_resp.json()
                
                op_stations = []
                for r in railways:
                    railway_id = r["owl:sameAs"]
                    s_url = f"{BASE_URL}/odpt:Station"
                    s_params = {
                        "odpt:railway": railway_id,
                        "acl:consumerKey": API_KEY
                    }
                    s_resp = requests.get(s_url, params=s_params, timeout=30)
                    s_resp.raise_for_status()
                    s_data = s_resp.json()
                    op_stations.extend(s_data)
                
                all_stations.extend(op_stations)
                print(f"    {operator.split(':')[-1]}: {len(op_stations)} stations")
                
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

    def find_routes(self, from_query: str, to_query: str, limit: int = 3, transfer_buffer: int = 5) -> list:
        """Find multiple distinct routes using iterative penalty method."""
        routes = []
        penalty_edges = set()
        seen_paths = set()
        
        for _ in range(limit * 2): # Try more times than limit to find valid distinct routes
            if len(routes) >= limit:
                break
                
            result = self.find_route(from_query, to_query, transfer_buffer, penalty_edges)
            if "error" in result:
                break
                
            path_ids = tuple(result.get("path_ids", []))
            
            if not path_ids or path_ids in seen_paths:
                # If we found duplicates despite penalties, maybe we are stuck.
                # Force penalize this duplicate path again to push it further down
                path_list = result.get("path_ids", [])
                for i in range(len(path_list) - 1):
                    u, v = path_list[i], path_list[i+1]
                    penalty_edges.add((u, v))
                    penalty_edges.add((v, u))
                continue
            else:
                seen_paths.add(path_ids)
                routes.append(result)
            
            # Penalize edges in this path for next iteration
            path_list = result.get("path_ids", [])
            for i in range(len(path_list) - 1):
                u, v = path_list[i], path_list[i+1]
                penalty_edges.add((u, v))
                penalty_edges.add((v, u))
        
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



    def _load_gtfs_railway_info(self):
        """Populate railway info for Metro lines to support name mapping."""
        # Hardcoded map based on constants.py
        # This ensures we get "銀座線" -> "Ginza" mapping in finder.
        
        # Metro
        self.railways["odpt.Railway:TokyoMetro.Ginza"] = {"name_ja": "銀座線", "name_en": "Ginza Line"}
        self.railways["odpt.Railway:TokyoMetro.Marunouchi"] = {"name_ja": "丸ノ内線", "name_en": "Marunouchi Line"}
        self.railways["odpt.Railway:TokyoMetro.Hibiya"] = {"name_ja": "日比谷線", "name_en": "Hibiya Line"}
        self.railways["odpt.Railway:TokyoMetro.Tozai"] = {"name_ja": "東西線", "name_en": "Tozai Line"}
        self.railways["odpt.Railway:TokyoMetro.Chiyoda"] = {"name_ja": "千代田線", "name_en": "Chiyoda Line"}
        self.railways["odpt.Railway:TokyoMetro.Yurakucho"] = {"name_ja": "有楽町線", "name_en": "Yurakucho Line"}
        self.railways["odpt.Railway:TokyoMetro.Hanzomon"] = {"name_ja": "半蔵門線", "name_en": "Hanzomon Line"}
        self.railways["odpt.Railway:TokyoMetro.Namboku"] = {"name_ja": "南北線", "name_en": "Namboku Line"}
        self.railways["odpt.Railway:TokyoMetro.Fukutoshin"] = {"name_ja": "副都心線", "name_en": "Fukutoshin Line"}
        
        # Toei
        self.railways["odpt.Railway:Toei.Asakusa"] = {"name_ja": "浅草線", "name_en": "Asakusa Line"}
        self.railways["odpt.Railway:Toei.Mita"] = {"name_ja": "三田線", "name_en": "Mita Line"}
        self.railways["odpt.Railway:Toei.Shinjuku"] = {"name_ja": "新宿線", "name_en": "Shinjuku Line"}
        self.railways["odpt.Railway:Toei.Oedo"] = {"name_ja": "大江戸線", "name_en": "Oedo Line"}

    def _load_gtfs_stations_data(self) -> list:

        """Load Tokyo Metro stations from GTFS and return as list of ODPT-like objects."""
        gtfs_dir = os.path.join(os.path.dirname(__file__), "../../backend/data/metro_gtfs")
        if not os.path.exists(gtfs_dir):
            return []
            
        print("Loading GTFS stations...")
        
        # Metro Line Code Map
        metro_codes = {
            "G": "Ginza", "M": "Marunouchi", "m": "Marunouchi", "H": "Hibiya",
            "T": "Tozai", "C": "Chiyoda", "Y": "Yurakucho", "Z": "Hanzomon",
            "N": "Namboku", "F": "Fukutoshin", "A": "Asakusa", "I": "Mita", 
            "S": "Shinjuku", "E": "Oedo"
        }
        
        generated_stations = []
        
        try:
            with open(os.path.join(gtfs_dir, "stops.txt"), "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stop_code = row.get("stop_code")
                    stop_name = row["stop_name"]
                    
                    if not stop_code: continue
                    
                    # Infer railway
                    prefix = stop_code[0]
                    line_name = metro_codes.get(prefix)
                    
                    if line_name:
                        suffix = line_name
                        railway_id = f"odpt.Railway:TokyoMetro.{suffix}"
                        if prefix in ["A", "I", "S", "E"]:
                             railway_id = f"odpt.Railway:Toei.{suffix}"

                        # Create synthetic object
                        operator = "TokyoMetro" if prefix not in ["A", "I", "S", "E"] else "Toei"
                        station_id = f"gtfs.Station:{operator}.{suffix}.{stop_code}"
                        
                        generated_stations.append({
                            "owl:sameAs": station_id,
                            "dc:title": stop_name,
                            "odpt:railway": railway_id,
                            "odpt:stationTitle": {"ja": stop_name}
                        })
                        
        except Exception as e:
            print(f"Error parse GTFS stops: {e}")
            
        return generated_stations

    def _load_gtfs_edges(self):
        """Load Tokyo Metro GTFS data to enhance graph edges."""
        gtfs_dir = os.path.join(os.path.dirname(__file__), "../../backend/data/metro_gtfs")
        if not os.path.exists(gtfs_dir):
            return

        print("Loading GTFS edges...")
        from .constants import RAILWAY_JA_TO_EN
        
        # 1. Routes
        gtfs_route_to_odpt = {}
        try:
            with open(os.path.join(gtfs_dir, "routes.txt"), "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    route_name = row["route_long_name"]
                    suffix = RAILWAY_JA_TO_EN.get(route_name)
                    if suffix:
                        if "都営" in row.get("agency_id", "") or suffix in ["Asakusa", "Mita", "Shinjuku", "Oedo"]:
                             gtfs_route_to_odpt[row["route_id"]] = f"odpt.Railway:Toei.{suffix}"
                        else:
                             gtfs_route_to_odpt[row["route_id"]] = f"odpt.Railway:TokyoMetro.{suffix}"
        except Exception: pass

        # 2. Stops (ID -> Name)
        gtfs_stops = {}
        try:
            with open(os.path.join(gtfs_dir, "stops.txt"), "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    gtfs_stops[row["stop_id"]] = row["stop_name"]
        except Exception: pass

        # 3. Trips
        trip_route_map = {}
        try:
            with open(os.path.join(gtfs_dir, "trips.txt"), "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    trip_route_map[row["trip_id"]] = row["route_id"]
        except Exception: pass

        # 4. Times
        try:
            with open(os.path.join(gtfs_dir, "stop_times.txt"), "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                segment_times = defaultdict(list)
                
                # Group by trip
                trips_data = defaultdict(list)
                for row in reader:
                    trips_data[row["trip_id"]].append(row)
                
                for trip_id, stops in trips_data.items():
                    stops.sort(key=lambda x: int(x["stop_sequence"]))
                    route_id = trip_route_map.get(trip_id)
                    railway_id = gtfs_route_to_odpt.get(route_id)
                    if not railway_id: continue
                    
                    for i in range(len(stops) - 1):
                        s1, s2 = stops[i], stops[i+1]
                        name1 = gtfs_stops.get(s1["stop_id"])
                        name2 = gtfs_stops.get(s2["stop_id"])
                        if not name1 or not name2: continue
                        
                        try:
                            def ptime(t):
                                h,m,s = map(int, t.split(':'))
                                return h*60 + m + s/60
                            diff = ptime(s2["arrival_time"]) - ptime(s1["departure_time"])
                            if diff < 0: diff += 24*60
                            segment_times[(name1, name2, railway_id)].append(diff)
                        except: pass
                
                count = 0
                for (n1, n2, rid), times in segment_times.items():
                     ids1 = self.station_by_name.get(n1, [])
                     ids2 = self.station_by_name.get(n2, [])
                     
                     oid1 = next((i for i in ids1 if self.station_info[i]["railway"] == rid), None)
                     oid2 = next((i for i in ids2 if self.station_info[i]["railway"] == rid), None)
                     
                     if oid1 and oid2:
                         avg = sum(times)/len(times)
                         self._upsert_edge(oid1, oid2, avg, "ride", rid)
                         count += 1
                
                print(f"Updated {count} segments from GTFS.");
                
        except Exception as e:
            print(f"GTFS Edges Error: {e}")

    def _upsert_edge(self, u, v, time, type, railway):
        current_edges = self.edges[u]
        found = False
        for edge in current_edges:
            if edge["to"] == v and edge["type"] == type and edge.get("railway") == railway:
                edge["time"] = time 
                found = True
                break
        if not found:
            self.edges[u].append({
                "to": v,
                "time": time,
                "type": type,
                "railway": railway
            })


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


