import sys
import os
import requests
import csv
import statistics
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from db.database import SessionLocal, engine
from db.models import Station, Railway, RouteEdge, StationInterval
from services.constants import (
    ODPT_BASE_URL,
    ALL_OPERATORS,
    RAILWAY_JA_TO_EN
)

load_dotenv(dotenv_path=BASE_DIR.parent / ".env")
API_KEY = os.getenv("ODPT_ACCESS_TOKEN")

def import_jr_edges(db):
    print("Importing JR Edges...")
    
    # Load travel times from DB
    travel_times = {}
    intervals = db.query(StationInterval).all()
    for inv in intervals:
        travel_times[(inv.from_station, inv.to_station)] = inv.time_minutes
    print(f"  Loaded {len(travel_times)} known intervals.")
    
    # Determine which railways to process (JR Only here ideally, but logic works for any with order)
    # Filter for JR operators
    target_operators = ["odpt.Operator:JR-East"]
    
    edge_count = 0
    
    for operator in target_operators:
        try:
            url = f"{ODPT_BASE_URL}/odpt:Railway"
            params = {"odpt:operator": operator, "acl:consumerKey": API_KEY}
            res = requests.get(url, params=params)
            res.raise_for_status()
            data = res.json()
            
            for railway in data:
                railway_id = railway["owl:sameAs"]
                station_order = railway.get("odpt:stationOrder", [])
                
                # Sort by index just in case
                station_order.sort(key=lambda x: x.get("odpt:index", 0))
                
                stations = [s["odpt:station"] for s in station_order]
                
                for i in range(len(stations) - 1):
                    s1 = stations[i]
                    s2 = stations[i+1]
                    
                    # Look up time
                    s1_simple = s1.split(".")[-1]
                    s2_simple = s2.split(".")[-1]
                    
                    time_fwd = travel_times.get((s1_simple, s2_simple), 3.0)
                    time_bwd = travel_times.get((s2_simple, s1_simple), 3.0)
                    
                    # Add edges
                    db.merge(RouteEdge(id=None, from_station_id=s1, to_station_id=s2, time_minutes=time_fwd, railway_id=railway_id, type="ride"))
                    db.merge(RouteEdge(id=None, from_station_id=s2, to_station_id=s1, time_minutes=time_bwd, railway_id=railway_id, type="ride"))
                    edge_count += 2
                    
        except Exception as e:
            print(f"  Error processing {operator}: {e}")
            
    db.commit()
    print(f"  Imported {edge_count} JR edges.")

def import_gtfs_edges(db):
    print("Importing GTFS Edges...")
    
    gtfs_base = BASE_DIR / "data"
    gtfs_dirs = [
        {"path": gtfs_base / "metro_gtfs", "type": "Metro"},
        {"path": gtfs_base / "Toei-Train-GTFS", "type": "Toei"}
    ]
    
    # We need to map GTFS route_id to ODPT Railway ID
    # And map GTFS stop_id to ODPT Station ID
    # This involves some heuristic matching as seen in routing.py
    
    # Pre-load all stations in DB to help mapping? 
    # Actually, import_stations logic created IDs like "gtfs.Station:TokyoMetro.Ginza.G01"
    # We need to reconstruct these IDs from GTFS data.
    
    count = 0
    
    for g in gtfs_dirs:
        gtfs_dir = g["path"]
        if not gtfs_dir.exists(): continue
        
        print(f"  Processing {g['type']}...")
        
        # 0. Load Stops (stop_id -> stop_code)
        stop_id_map = {} # stop_id -> stop_code
        try:
            with open(gtfs_dir / "stops.txt", "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("stop_code"):
                         stop_id_map[row["stop_id"]] = row["stop_code"]
        except Exception: pass

        # 1. Routes (GTFS route_id -> ODPT Railway ID)
        route_map = {}

        try:
            with open(gtfs_dir / "routes.txt", "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    route_name = row["route_long_name"]
                    suffix = RAILWAY_JA_TO_EN.get(route_name)
                    if suffix:
                        if "都営" in row.get("agency_id", "") or suffix in ["Asakusa", "Mita", "Shinjuku", "Oedo"]:
                             route_map[row["route_id"]] = f"odpt.Railway:Toei.{suffix}"
                        else:
                             route_map[row["route_id"]] = f"odpt.Railway:TokyoMetro.{suffix}"
        except Exception as e:
            print(f"    Error reading routes: {e}")
            continue

        # 2. Trips (trip_id -> route_id)
        trip_map = {}
        try:
            with open(gtfs_dir / "trips.txt", "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    trip_map[row["trip_id"]] = row["route_id"]
        except Exception: pass

        # 3. Stop Times (Calculate intervals)
        segment_times = defaultdict(list)
        try:
            with open(gtfs_dir / "stop_times.txt", "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                # Group by trip
                trips_data = defaultdict(list)
                for row in reader:
                    trips_data[row["trip_id"]].append(row)
                
            for trip_id, stops in trips_data.items():
                stops.sort(key=lambda x: int(x["stop_sequence"]))
                route_id = trip_map.get(trip_id)
                railway_id = route_map.get(route_id)
                if not railway_id: continue
                
                # Determine Operator prefix for Station ID construction
                op_prefix = "TokyoMetro" if "TokyoMetro" in railway_id else "Toei"
                line_suffix = railway_id.split(".")[-1]
                
                for i in range(len(stops) - 1):
                    s1 = stops[i]
                    s2 = stops[i+1]
                    
                    code1 = stop_id_map.get(s1["stop_id"])
                    code2 = stop_id_map.get(s2["stop_id"])
                    
                    if not code1 or not code2: continue

                    # Construct Station ID
                    sid1 = f"gtfs.Station:{op_prefix}.{line_suffix}.{code1}"
                    sid2 = f"gtfs.Station:{op_prefix}.{line_suffix}.{code2}"
                    
                    try:
                        def ptime(t):
                            h,m,s = map(int, t.split(':'))
                            return h*60 + m + s/60
                        diff = ptime(s2["arrival_time"]) - ptime(s1["departure_time"])
                        if diff < 0: diff += 24*60
                        segment_times[(sid1, sid2, railway_id)].append(diff)
                    except: pass
            
            # Average and Insert
            for (u, v, rid), times in segment_times.items():
                avg = statistics.mean(times)
                db.merge(RouteEdge(id=None, from_station_id=u, to_station_id=v, time_minutes=avg, railway_id=rid, type="ride"))
                count += 1
                
        except Exception as e:
            print(f"    Error processing stop_times: {e}")

    db.commit()
    print(f"  Imported {count} GTFS edges.")

def import_transfers(db):
    print("Importing Transfers...")
    stations = db.query(Station).all()
    by_name = defaultdict(list)
    for s in stations:
        by_name[s.name_ja].append(s.id)
    
    count = 0
    for name, ids in by_name.items():
        if len(ids) > 1:
            for i, s1 in enumerate(ids):
                for s2 in ids[i+1:]:
                    # Transfer time = 5 mins default? 
                    # routing.py used 0 mins (theoretical). Let's stick to 0 for now.
                    # Or maybe 5 to be realistic? "Theoretical fastest" usually assumes 0 or small constant.
                    # routing.py: `transfer_buffer` passed in query. Base edge was 0.
                    time = 0
                    
                    db.merge(RouteEdge(id=None, from_station_id=s1, to_station_id=s2, time_minutes=time, railway_id=None, type="transfer"))
                    db.merge(RouteEdge(id=None, from_station_id=s2, to_station_id=s1, time_minutes=time, railway_id=None, type="transfer"))
                    count += 2
                    
    db.commit()
    print(f"  Imported {count} transfer edges.")
    
def main():
    if not API_KEY:
        print("Error: ODPT_ACCESS_TOKEN not found.")
        return

    # Clear existing edges??
    # db.query(RouteEdge).delete() # Might be dangerous if we want to run incrementally, but simpler.
    
    db = SessionLocal()
    try:
        # Clear table first to avoid duplicates (since we use auto-inc ID, merge logic is tricky without unique constraints)
        print("Clearing RouteEdge table...")
        db.query(RouteEdge).delete()
        db.commit()
        
        import_jr_edges(db)
        import_gtfs_edges(db)
        import_transfers(db)
        print("Edge import complete.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
