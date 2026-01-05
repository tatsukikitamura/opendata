import os
import csv
import sys
import datetime
from pathlib import Path
from collections import defaultdict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from db.models import StationDeparture, StationOrder, StationInterval
from db.database import Base, SessionLocal

# Helper to map complex Metro IDs to simple English names used in DB
# We align with constants.py RAILWAY_JA_TO_EN if possible, or create standard names.

RAILWAY_MAP = {
    "Ginza Line": "Ginza",
    "Marunouchi Line": "Marunouchi",
    "Hibiya Line": "Hibiya",
    "Tozai Line": "Tozai",
    "Chiyoda Line": "Chiyoda",
    "Yurakucho Line": "Yurakucho",
    "Hanzomon Line": "Hanzomon",
    "Namboku Line": "Namboku",
    "Fukutoshin Line": "Fukutoshin",
    # Toei? The GTFS has Toei lines too?
    # Yes, user's GTFS likely includes Toei if it's the specific file provided? 
    # Actually checking previous output for routes.txt showed "tokyometro" agency. 
    # If it's pure Metro, fine. Even better.
}

def load_metro_gtfs():
    gtfs_dir = Path(__file__).resolve().parent.parent.parent / "data" / "metro_gtfs"
    
    if not gtfs_dir.exists():
        print(f"GTFS directory not found: {gtfs_dir}")
        return

    print("Connecting to DB...")
    db = SessionLocal()

    try:
        # 1. Load Translations (Japanese -> English)
        print("Loading translations...")
        ja_to_en = {}
        with open(gtfs_dir / "translations.txt", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["language"] == "en" and row.get("field_value"):
                    ja_to_en[row["field_value"]] = row["translation"]

        # 2. Load Stops (ID -> Name EN)
        print("Loading stops...")
        stops = {} # ID -> {name_ja, name_en}
        with open(gtfs_dir / "stops.txt", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name_ja = row["stop_name"]
                name_en = ja_to_en.get(name_ja, name_ja)  # Fallback to JA if no EN
                stops[row["stop_id"]] = {"ja": name_ja, "en": name_en}

        # 3. Load Routes (ID -> Name EN)
        print("Loading routes...")
        routes = {} # ID -> {name_ja, name_en, simple_name}
        with open(gtfs_dir / "routes.txt", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name_ja = row["route_long_name"]
                name_en = ja_to_en.get(name_ja, name_ja)
                simple_en = RAILWAY_MAP.get(name_en, name_en.replace(" Line", ""))
                routes[row["route_id"]] = {"ja": name_ja, "en": name_en, "simple": simple_en}

        # 4. Load Trips (Trip ID -> Route ID, Service ID, Direction)
        print("Loading trips...")
        trips = {}
        route_trips = defaultdict(list)
        with open(gtfs_dir / "trips.txt", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                trips[row["trip_id"]] = row
                route_trips[row["route_id"]].append(row["trip_id"])

        # 5. Populate Station Orders (One per route)
        print("Populating Station Orders...")
        # Clear existing Metro orders? 
        # For safety, let's delete existing Metro lines from DB first?
        # Ideally yes, to avoid duplicates.
        existing_railways = set(r["simple"] for r in routes.values())
        db.query(StationOrder).filter(StationOrder.railway_name.in_(existing_railways)).delete(synchronize_session=False)
        db.commit()

        # Load Stop Times (Trip -> List[Stops])
        # We need to iterate stops to find longest sequence for station order
        print("Reading stop_times (may take a moment)...")
        trip_stops = defaultdict(list)
        with open(gtfs_dir / "stop_times.txt", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                trip_stops[row["trip_id"]].append(row)

        for route_id, trip_ids in route_trips.items():
            # Find longest trip to define station order
            longest_trip_id = max(trip_ids, key=lambda tid: len(trip_stops[tid]))
            ordered_stops = sorted(trip_stops[longest_trip_id], key=lambda x: int(x["stop_sequence"]))
            
            railway_name = routes[route_id]["simple"]
            
            for idx, stop in enumerate(ordered_stops):
                stop_info = stops[stop["stop_id"]]
                s_order = StationOrder(
                    railway_id=route_id, # Or use ODPT ID? DB uses simple name usually? 
                    railway_name=railway_name,
                    station_id=stop["stop_id"],
                    station_name=stop_info["en"], # Use English for DB consistency
                    station_index=idx
                )
                db.add(s_order)
        db.commit()



        # Build station index map for direction calculation
        # Key: (railway_name, station_id) -> index
        station_indices = {}
        # We can query from DB if we just inserted? 
        # But we haven't committed efficiently or we might want memory map.
        # Actually we iterated `ordered_stops` line 111.
        # Let's rebuild it here from routes/stops logic or just query DB?
        # Querying DB is safer as it is the "truth".
        all_orders = db.query(StationOrder).filter(StationOrder.railway_name.in_(existing_railways)).all()
        for o in all_orders:
            station_indices[(o.railway_name, o.station_id)] = o.station_index


        # 6. Populate Station Departures AND Calculate Intervals
        print("Populating Station Departures & Calculating Intervals...")
        
        # Clear existing Metro data
        db.query(StationDeparture).filter(StationDeparture.railway_name.in_(existing_railways)).delete(synchronize_session=False)
        db.query(StationInterval).filter(StationInterval.railway_name.in_(existing_railways)).delete(synchronize_session=False)
        
        batch = []
        BATCH_SIZE = 5000
        
        # Segments for interval calculation
        segment_data = defaultdict(list)
        
        for trip_id, stop_rows in trip_stops.items():
            trip_info = trips[trip_id]
            route_id = trip_info["route_id"]
            railway_name = routes[route_id]["simple"]
            
            # Sort stops by sequence
            stop_rows.sort(key=lambda x: int(x["stop_sequence"]))
            
            # 1. Determine Direction
            start_stop_id = stop_rows[0]["stop_id"]
            end_stop_id = stop_rows[-1]["stop_id"]
            
            start_idx = station_indices.get((railway_name, start_stop_id))
            end_idx = station_indices.get((railway_name, end_stop_id))
            
            if start_idx is not None and end_idx is not None:
                if end_idx > start_idx:
                    direction = "Outbound"
                else:
                    direction = "Inbound"
            else:
                # Fallback to GTFS direction_id if indices missing (shouldn't happen)
                direction = "Outbound" if trip_info["direction_id"] == "0" else "Inbound"
            
            # 2. Determine Service Types Based on GTFS calendar.txt
            # 0: Weekday (Mon-Fri)
            # 1: Weekend (Sat-Sun) -> Map to Saturday AND Holiday
            service_id = trip_info["service_id"]
            target_types = []
            
            if service_id == "0":
                target_types.append("Weekday")
            elif service_id == "1":
                target_types.append("Saturday")
                target_types.append("Holiday")
            else:
                # Fallback for unexpected IDs (using original logic just in case)
                if "Weekday" in service_id:
                    target_types.append("Weekday")
                if "Saturday" in service_id:
                    target_types.append("Saturday")
                if "Sunday" in service_id or "Holiday" in service_id:
                    target_types.append("Holiday")
            
            # Fallback if unmapped (e.g. unknown service id string)
            # Check previous behavior - it seemingly defaulted to Holiday for everything?
            # If target_types is empty, we must assign something.
            if not target_types:
                 # Try to infer? Or default to Holiday generally safe for "extra" trains?
                 # Or maybe default to Weekday?
                 # Given previous "Holiday" mass, assume Holiday fallback.
                 target_types.append("Holiday")

            # Identify destination
            destination_stop_id = stop_rows[-1]["stop_id"]
            destination_name = stops[destination_stop_id]["en"]

            # Store Departure Data (duplicate for each target type)
            for w_type in target_types:
                for i, stop in enumerate(stop_rows):
                    if not stop["departure_time"]: continue
                    
                    # Format time HH:MM
                    d_time_str = stop["departure_time"]
                    # Handle HH:MM:SS
                    if len(d_time_str) >= 5:
                        d_time = d_time_str[:5]
                    else:
                        d_time = d_time_str

                    # Hour adjustment
                    try:
                        h = int(d_time[:2])
                        if h >= 24:
                            h -= 24
                            d_time = f"{h:02d}{d_time[2:]}"
                    except:
                        pass
                    
                    status_name = stops[stop["stop_id"]]["en"]
                    
                    dep = StationDeparture(
                        station_id=stop["stop_id"],
                        station_name=status_name,
                        railway_id=route_id,
                        railway_name=railway_name,
                        direction=direction,
                        departure_time=d_time,
                        train_type="Local", # Default
                        destination_station=destination_name,
                        train_number=trip_id,
                        weekday_type=w_type
                    )
                    batch.append(dep)
                    
                    # Calculate Intervals (if not last stop)
                    if i < len(stop_rows) - 1:
                        next_stop = stop_rows[i+1]
                        t1_str = stop["departure_time"]
                        t2_str = next_stop["arrival_time"]
                        
                        if t1_str and t2_str:
                            try:
                                # Parse HH:MM:SS to minutes
                                def to_min(t_s):
                                    parts = t_s.split(":")
                                    h, m = int(parts[0]), int(parts[1])
                                    # seconds ignored for interval minute precision? Or keep float?
                                    # Usually detailed routing needs precision, but StationInterval assumes float minutes
                                    s = int(parts[2]) if len(parts) > 2 else 0
                                    return h * 60 + m + s/60.0
                                
                                t1 = to_min(t1_str)
                                t2 = to_min(t2_str)
                                
                                duration = t2 - t1
                                if duration > 0 and duration < 120: # Sanity check
                                    from_name = status_name
                                    to_name = stops[next_stop["stop_id"]]["en"]
                                    segment_data[(from_name, to_name, railway_name)].append(duration)
                            except:
                                pass
    
                    if len(batch) >= BATCH_SIZE:
                        db.bulk_save_objects(batch)
                        db.commit()
                        batch = []
                    
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
            
        # 7. Save Intervals
        print(f"Saving {len(segment_data)} intervals to database...")
        interval_batch = []
        for (from_name, to_name, r_name), times in segment_data.items():
            avg_time = sum(times) / len(times)
            rec = StationInterval(
                from_station=from_name,
                to_station=to_name,
                railway_name=r_name,
                time_minutes=avg_time
            )
            interval_batch.append(rec)
        
        if interval_batch:
            db.bulk_save_objects(interval_batch)
            db.commit()


        print("Done!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    load_metro_gtfs()
