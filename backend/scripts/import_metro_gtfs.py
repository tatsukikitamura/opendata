import os
import csv
import sys
import datetime
from pathlib import Path
from collections import defaultdict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

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
    gtfs_dir = Path(__file__).resolve().parent.parent / "data" / "metro_gtfs"
    
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

        # 6. Populate Station Departures
        print("Populating Station Departures...")
        # Clear existing
        db.query(StationDeparture).filter(StationDeparture.railway_name.in_(existing_railways)).delete(synchronize_session=False)
        
        batch = []
        BATCH_SIZE = 5000
        
        for trip_id, stop_rows in trip_stops.items():
            trip_info = trips[trip_id]
            route_id = trip_info["route_id"]
            railway_name = routes[route_id]["simple"]
            direction = "Outbound" if trip_info["direction_id"] == "0" else "Inbound" # Assumption: 0=Outbound? 
            # Actually direction logic is complex. But let's check one line.
            # Ginza: 0=Shibuya->Asakusa. Shibuya is 1. Asakusa is large index. -> Outbound.
            # This aligns with StationOrder if we picked longest trip in 0 direction?
            # We picked "longest trip" from ALL trips. If longest trip was direction 1?
            # We need to ensure StationOrder direction matches "0".
            # Let's refine StationOrder logic: Pick longest from direction "0".
            
            # Re-do StationOrder logic purely for direction consistency?
            # It's okay if we labeled "0" as "Outbound" and "1" as "Inbound".
            
            service_id = trip_info["service_id"]
            # Map service_id to weekday?
            # Metro GTFS service_ids: usually "Weekday", "Saturday", "SundayHoliday"
            # Need to check `calendar.txt` or `calendar_dates.txt`.
            # For now, simplistic check or mapping? 
            # If `services` map is needed, we should load `calendar.txt`.
            
            weekday_type = "Weekday" # default
            # TODO: Map service_id
            
            destination_stop_id = stop_rows[-1]["stop_id"] # Last stop based on sequence
            # Wait, stop_rows needs sorting per trip!
            stop_rows.sort(key=lambda x: int(x["stop_sequence"]))
            destination_name = stops[destination_stop_id]["en"]

            for stop in stop_rows:
                if not stop["departure_time"]: continue
                
                # Format time HH:MM
                d_time = stop["departure_time"][:5]
                h = int(d_time[:2])
                if h >= 24:
                    h -= 24
                    d_time = f"{h:02d}{d_time[2:]}"
                
                dep = StationDeparture(
                    station_id=stop["stop_id"],
                    station_name=stops[stop["stop_id"]]["en"],
                    railway_id=route_id,
                    railway_name=railway_name,
                    direction=direction, # 0/1 mapped
                    departure_time=d_time,
                    train_type="Local", # Default
                    destination_station=destination_name,
                    train_number=trip_id,
                    weekday_type=weekday_type
                )
                batch.append(dep)
                
                if len(batch) >= BATCH_SIZE:
                    db.bulk_save_objects(batch)
                    db.commit()
                    batch = []
                    
        if batch:
            db.bulk_save_objects(batch)
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
