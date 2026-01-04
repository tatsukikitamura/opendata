"""
Fetch train timetables from ODPT API and store in database.
Using TrainTimetable API allows capturing both departure and arrival times, 
ensuring terminal stations are recorded.
"""

import os
import sys
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.models import Base, StationDeparture


# Load .env from project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(BASE_DIR, ".env"))


API_KEY = os.getenv("ODPT_ACCESS_TOKEN")
BASE_URL = "https://api-challenge.odpt.org/api/v4"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.db")


def get_db_session():
    """Create database session."""
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session(), StationDeparture


def fetch_train_timetables(railway_id: str):
    """Fetch train timetables for a specific railway."""
    url = f"{BASE_URL}/odpt:TrainTimetable"
    params = {
        "odpt:railway": railway_id,
        "acl:consumerKey": API_KEY
    }
    
    all_trains = []
    
    # Split by calendar to avoid 1000 record limit per query
    # ChuoSobuLocal and others exceed 1000 daily.
    calendars = [
        "odpt.Calendar:Weekday", 
        "odpt.Calendar:Saturday", 
        "odpt.Calendar:SundayHoliday",
        "odpt.Calendar:SaturdayHoliday"
    ]
    

    for cal in calendars:
        params_cal = params.copy()
        params_cal["odpt:calendar"] = cal
        
        # Determine mapped types
        target_types = []
        if "Weekday" in cal:
            target_types.append("Weekday")
        elif "SaturdayHoliday" in cal: # Check specific compound first
            target_types.append("Saturday")
            target_types.append("Holiday")
        elif "Saturday" in cal:
            target_types.append("Saturday")
        elif "Holiday" in cal:
            target_types.append("Holiday")
        else:
            # Fallback
            target_types.append("Weekday")

        # Deduplicate types
        target_types = sorted(list(set(target_types)))
        
        try:
            response = requests.get(url, params=params_cal, timeout=60)
            if response.status_code == 200:
                data = response.json()
                if data:
                    # Inject type and duplicate if needed
                    for w_type in target_types:
                        for item in data:
                            new_item = item.copy()
                            new_item["_inferred_weekday_type"] = w_type
                            all_trains.append(new_item)
            else:
                 # Some lines might not support calendar filtering or return 404/400?
                 # Actually ODPT usually returns 200 [] or errors.
                 pass
        except Exception as e:
            print(f"  Error fetching {railway_id} ({cal}): {e}")
            
    # Also try without calendar if we got nothing? 
    # Or some lines don't use these specific calendars?
    # Majority of JR East lines use Weekday/SaturdayHoliday or Weekday/Saturday/SundayHoliday
    # If all_trains is empty, try fetch ALL (fallback)
    if not all_trains:
        try:
             response = requests.get(url, params=params, timeout=60)
             if response.status_code == 200:
                 all_trains = response.json()
        except Exception:
            pass

    return all_trains


def parse_train_timetable(train_data: dict) -> list:
    """Parse a train timetable into multiple station departure records."""
    departures = []
    
    railway_id = train_data.get("odpt:railway", "")
    railway_name = railway_id.split(".")[-1] if railway_id else ""
    
    # Get direction
    rail_direction = train_data.get("odpt:railDirection", "")
    if "Outbound" in rail_direction or "OuterLoop" in rail_direction:
        direction = "Outbound"
    elif "Inbound" in rail_direction or "InnerLoop" in rail_direction:
        direction = "Inbound"
    else:
        direction = "Inbound"
    
    # Get calendar - now using the inferred type from fetch_train_timetables
    weekday_type = train_data.get("_inferred_weekday_type", "Unknown")
        
    train_number = train_data.get("odpt:trainNumber", "")
    train_type = train_data.get("odpt:trainType", "")
    if ":" in train_type:
        train_type = train_type.split(".")[-1]
        
    destination_list = train_data.get("odpt:destinationStation", [])
    if destination_list:
        dest_id = destination_list[-1]
        dest_name = dest_id.split(".")[-1]
    else:
        dest_name = ""
        
    # Process each stop
    stops = train_data.get("odpt:trainTimetableObject", [])
    
    for stop in stops:
        # Station info
        station_id = stop.get("odpt:departureStation") or stop.get("odpt:arrivalStation")
        if not station_id:
            continue
            
        station_name = station_id.split(".")[-1]
        
        # Time info
        departure_time = stop.get("odpt:departureTime")
        arrival_time = stop.get("odpt:arrivalTime")
        
        # Determine effective "time" for the record
        # For intermediate stations, use departure time
        # For terminal station, use arrival time (so we can query arrival)
        
        effective_time = departure_time
        if not effective_time:
            effective_time = arrival_time
            
        if not effective_time:
            continue
            
        departures.append({
            "station_id": station_id,
            "station_name": station_name,
            "railway_id": railway_id,
            "railway_name": railway_name,
            "direction": direction,
            "departure_time": effective_time, # Can be arrival time for terminal
            "train_type": train_type,
            "destination_station": dest_name,
            "train_number": train_number,
            "weekday_type": weekday_type
        })
        
    return departures




def fetch_all_railways(operator="odpt.Operator:JR-East"):
    """Fetch all railways for a specific operator."""
    url = f"{BASE_URL}/odpt:Railway"
    params = {
        #"odpt:operator": operator, # Filter might not work on API side
        "acl:consumerKey": API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()

            # Filter in python
            railways = []
            for r in data:
                # Use owl:sameAs as primary ID, fallback to odpt:railway
                rid = r.get("owl:sameAs") or r.get("odpt:railway")
                op = r.get("odpt:operator", "")
                
                if not rid:
                    continue
                    
                # Check operator (if provided) or prefix
                if operator in op or "JR-East" in rid:
                     railways.append(rid)
            
            # Filter out Shinkansen
            railways = [r for r in railways if "Shinkansen" not in r]
            return sorted(list(set(railways)))
        else:
            print(f"Error fetching railways: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching railways: {e}")
        return []


def main():
    if not API_KEY:
        print("ERROR: ODPT_ACCESS_TOKEN not set in .env file")
        return
    
    print("=" * 60)
    print("Train Timetable Fetcher (Source: odpt:TrainTimetable)")
    print("=" * 60)
    
    session, StationDeparture = get_db_session()
    
    # Clear existing data
    print("\nClearing existing timetable data...")
    session.query(StationDeparture).delete()
    session.commit()
    

    # Fetch railways dynamically
    print("\nFetching railway list from API...")
    target_operators = [
        "odpt.Operator:JR-East",
        "odpt.Operator:TokyoMetro",
        "odpt.Operator:Toei"
    ]
    
    railways = []
    for op in target_operators:
        print(f"  Fetching {op}...")
        op_railways = fetch_all_railways(op)
        railways.extend(op_railways)
        print(f"    -> Found {len(op_railways)} lines")
    
    # Dedup and sort
    railways = sorted(list(set(railways)))
    
    if not railways:
        print("No railways found. Exiting.")
        return

    print(f"Total Target Railways: {len(railways)} lines")
    
    total_records = 0
    
    print("\nFetching train timetables from ODPT API...")
    
    for railway in railways:
        railway_name = railway.split(".")[-1]
        trains = fetch_train_timetables(railway)
        
        if not trains:
            print(f"  {railway_name}: No data")
            continue
        
        railway_records = 0
        
        for train in trains:
            records = parse_train_timetable(train)
            
            for rec in records:
                db_record = StationDeparture(**rec)
                session.add(db_record)
                railway_records += 1
                
        session.commit()
        total_records += railway_records
        print(f"  {railway_name}: {len(trains)} trains, {railway_records} records")
    
    print(f"\n{'=' * 60}")
    print(f"Total: {total_records} records saved to database")
    print(f"{'=' * 60}")
    
    session.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
