"""
Import Toei Subway GTFS data into station_departures table.
Based on import_metro_gtfs.py
"""
import os
import csv
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from db.models import Base, StationDeparture, StationOrder, StationInterval

# Configure paths
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

BASE_DIR = Path(__file__).parent.parent.parent
GTFS_DIR = BASE_DIR / "data" / "Toei-Train-GTFS"

# Mapping: GTFS route_id -> ODPT Railway Name suffix
# e.g. "Asakusa" -> "odpt.Railway:Toei.Asakusa"
ROUTE_MAP = {
    "Asakusa": "Asakusa",
    "Mita": "Mita",
    "Shinjuku": "Shinjuku",
    "Oedo": "Oedo",
    "Arakawa": "Arakawa", # Toden
    "Nippori-Toneri": "NipporiToneri"
}

def main():
    print("=== Importing Toei GTFS Data ===")
    
    if not GTFS_DIR.exists():
        print(f"Error: Directory not found: {GTFS_DIR}")
        return

    db = SessionLocal()
    
    try:
        # 1. Load Translations first
        translations = {}
        trans_file = GTFS_DIR / "translations.txt"
        if trans_file.exists():
            print("Loading translations...")
            with open(trans_file, encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('table_name') == 'stops' and row.get('field_name') == 'stop_name' and row.get('language') == 'en':
                        translations[row['field_value']] = row['translation']

        # 2. Load Stops
        print("Loading stops...")
        stops = {} # stop_id -> {name, name_en, code}
        with open(GTFS_DIR / "stops.txt", encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['stop_name']
                stops[row['stop_id']] = {
                    "name": name,
                    "name_en": translations.get(name, name),
                    "code": row.get('stop_code', '')
                }

        # 3. Load Routes
        print("Loading routes...")
        routes = {} # route_id -> railway_name_suffix
        with open(GTFS_DIR / "routes.txt", encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Toei GTFS route_id might be "Asakusa" or similar
                # Or sometimes numeric. Let's check route_long_name or short_name
                rid = row['route_id']
                name = row['route_long_name'] # e.g. "浅草線"
                
                # Map Japanese name to Suffix
                suffix = None
                if "浅草" in name: suffix = "Asakusa"
                elif "三田" in name: suffix = "Mita"
                elif "新宿" in name: suffix = "Shinjuku"
                elif "大江戸" in name: suffix = "Oedo"
                elif "荒川" in name: suffix = "Arakawa"
                elif "舎人" in name: suffix = "NipporiToneri"
                
                if suffix:
                    routes[rid] = suffix

        # 4. Load Trips
        print("Loading trips...")
        trips = {} # trip_id -> {route_id, service_id, headsign, direction}
        trip_service_ids = set()
        
        with open(GTFS_DIR / "trips.txt", encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tid = row['trip_id']
                rid = row['route_id']
                if rid in routes:
                    trips[tid] = {
                        "route_id": rid,
                        "service_id": row['service_id'],
                        "headsign": row.get('trip_headsign', ''),
                        "direction": row.get('direction_id', '0')
                    }
                    trip_service_ids.add(row['service_id'])

        # 5. Determine Calendars (Weekday/Saturday/Holiday)
        print("Determining calendars...")
        service_types = {} # service_id -> "Weekday" | "Saturday" | "Holiday"
        
        # Check calendar.txt
        cal_path = GTFS_DIR / "calendar.txt"
        if cal_path.exists():
            with open(cal_path, encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sid = row['service_id']
                    if sid not in trip_service_ids: continue
                    
                    # Logic: if saturday=1 -> Saturday, sunday=1 -> Holiday, else Weekday
                    # Simplistic but usually works for Japanese GTFS
                    if row['sunday'] == '1':
                        service_types[sid] = "Holiday"
                    elif row['saturday'] == '1':
                        service_types[sid] = "Saturday"
                    elif row['monday'] == '1':
                        service_types[sid] = "Weekday"
        
        # Also check calendar_dates.txt if needed (skip for now for simplicity, usually calendar.txt covers base schedule)

        # 6. Process Stop Times
        print("Reading stop_times (may take a moment)...")
        
        # Prepare batch insert
        departures = []
        
        # Clear existing Toei data
        existing_railways = ["Asakusa", "Mita", "Shinjuku", "Oedo", "Arakawa", "NipporiToneri"]
        print(f"Clearing existing data for: {existing_railways}")
        db.query(StationDeparture).filter(StationDeparture.railway_name.in_(existing_railways)).delete(synchronize_session=False)
        db.commit()
        
        count = 0
        with open(GTFS_DIR / "stop_times.txt", encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tid = row['trip_id']
                if tid not in trips: continue
                
                trip = trips[tid]
                service_id = trip['service_id']
                weekday_type = service_types.get(service_id, "Weekday")
                
                # We only need departure times
                dep_time = row['departure_time']
                if not dep_time: continue
                
                # Fix > 24:00 times (GTFS allows 25:00 etc)
                h, m, s = map(int, dep_time.split(':'))
                if h >= 24:
                    h -= 24
                    dep_time = f"{h:02d}:{m:02d}" # Drop seconds for DB format
                else:
                    dep_time = f"{h:02d}:{m:02d}"
                
                stop_id = row['stop_id']
                stop_info = stops.get(stop_id, {})
                station_name = stop_info.get('name_en', '') # Store English name in station_name field
                
                # Railway Name (simple suffix)
                railway_suffix = routes[trip['route_id']]
                
                rec = StationDeparture(
                    station_id=stop_id,
                    station_name=station_name, # Storing English name!
                    railway_name=railway_suffix,
                    train_number=tid, # Use trip_id as train_number
                    departure_time=dep_time,
                    destination_station=trip['headsign'], # Use headsign
                    train_type="Local", # GTFS doesn't always have easy type mapping, assume Local
                    weekday_type=weekday_type,
                    direction=trip['direction'] # 0 or 1
                )
                departures.append(rec)
                
                count += 1
                
                # Calculate Intervals
                # Need access to next stop. The loop is iterating trips, but we are streaming rows from stop_times.txt one by one?
                # Ah, CSV dictreader iterates rows sequentially. GTFS stop_times are usually ordered by trip_id and stop_sequence.
                # BUT relying on row order is risky if file is not sorted.
                # import_metro_gtfs.py loaded all stop_times into memory (trip_stops dict).
                # To calculate intervals reliably, we should do the same or buffer per trip.
                
                # Let's switch implementation to buffer stops per trip like metro importer.
                # However, Toei file might be large. 5M bytes is small. 120k records.
                # Memory is fine.
            
            # Switch to memory loading approach completely for interval calculation support
            pass 
            
        # --- RE-IMPLEMENTATION with Memory Loading ---
        print("Reading stop_times into memory for interval calculation...")
        trip_stops = defaultdict(list)
        with open(GTFS_DIR / "stop_times.txt", encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                trip_stops[row['trip_id']].append(row)

        print("Processing trips and calculating intervals...")
        batch = []
        segment_data = defaultdict(list)
        count = 0
        
        for tid, rows in trip_stops.items():
            if tid not in trips: continue
            
            trip = trips[tid]
            service_id = trip['service_id']
            weekday_type = service_types.get(service_id, "Weekday")
            railway_suffix = routes[trip['route_id']]
            
            # Sort by sequence
            rows.sort(key=lambda x: int(x['stop_sequence']))
            
            for i, row in enumerate(rows):
                # Departure Info
                dep_time_str = row['departure_time']
                if not dep_time_str: continue
                
                # Fix > 24:00
                h, m, s = map(int, dep_time_str.split(':'))
                if h >= 24:
                    h_fixed = h - 24
                    dep_time = f"{h_fixed:02d}:{m:02d}"
                else:
                    dep_time = f"{h:02d}:{m:02d}"

                stop_id = row['stop_id']
                station_name = stops.get(stop_id, {}).get('name', '')
                station_name_en = stops.get(stop_id, {}).get('name_en', station_name)
                
                rec = StationDeparture(
                    station_id=stop_id,
                    station_name=station_name_en, # English
                    railway_name=railway_suffix,
                    train_number=tid,
                    departure_time=dep_time,
                    destination_station=trip['headsign'],
                    train_type="Local",
                    weekday_type=weekday_type,
                    direction=trip['direction']
                )
                batch.append(rec)
                
                # Interval Calculation (to next stop)
                if i < len(rows) - 1:
                    next_row = rows[i+1]
                    t1_str = row['departure_time']
                    t2_str = next_row['arrival_time']
                    
                    try:
                        def to_minutes(t_s):
                            h, m, s = map(int, t_s.split(':'))
                            return h * 60 + m + s/60.0
                        
                        t1 = to_minutes(t1_str)
                        t2 = to_minutes(t2_str)
                        duration = t2 - t1
                        
                        if duration > 0 and duration < 120:
                            next_id = next_row['stop_id']
                            to_name_en = stops.get(next_id, {}).get('name_en', '')
                            if station_name_en and to_name_en:
                                segment_data[(station_name_en, to_name_en, railway_suffix)].append(duration)
                    except:
                        pass

                count += 1
                if len(batch) >= 10000:
                    db.bulk_save_objects(batch)
                    db.commit()
                    batch = []
                    print(f"Processed {count} departures...")

        if batch:
            db.bulk_save_objects(batch)
            db.commit()
            
        print(f"Imported {count} departures.")
        
        # Save Intervals
        print(f"Saving {len(segment_data)} intervals...")
        db.query(StationInterval).filter(StationInterval.railway_name.in_(existing_railways)).delete(synchronize_session=False)
        db.commit()
        
        interval_batch = []
        for (f_name, t_name, r_name), times in segment_data.items():
            avg_time = sum(times) / len(times)
            rec = StationInterval(
                from_station=f_name,
                to_station=t_name,
                railway_name=r_name,
                time_minutes=avg_time
            )
            interval_batch.append(rec)
            
        if interval_batch:
            db.bulk_save_objects(interval_batch)
            db.commit()

        print(f"Total {len(interval_batch)} intervals saved.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()
        print("Done!")

if __name__ == "__main__":
    main()
