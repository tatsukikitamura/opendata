"""
Extract travel times from ODPT TrainTimetable data and store in DB.
"""

import os
import sys
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from collections import defaultdict
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base, StationInterval

load_dotenv(dotenv_path="../.env")

API_KEY = os.getenv("ODPT_ACCESS_TOKEN")
BASE_URL = "https://api-challenge.odpt.org/api/v4"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.db")


def get_db_session():
    """Create database session."""
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def fetch_train_timetables():
    """Fetch all JR-East train timetables from ODPT API."""
    print("Fetching train timetables from ODPT API...")
    
    all_timetables = []
    
    # Import railways from shared constants
    from services.constants import ALL_RAILWAYS
    all_railways = ALL_RAILWAYS
    
    for railway in all_railways:
        try:
            url = f"{BASE_URL}/odpt:TrainTimetable"
            params = {
                "odpt:railway": railway,
                "acl:consumerKey": API_KEY
            }
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            if data:
                all_timetables.extend(data)
                print(f"  -> {railway.split('.')[-1]}: {len(data)} timetables")
        except Exception as e:
            print(f"  -> {railway.split('.')[-1]}: Error - {e}")
    
    print(f"  -> Total: {len(all_timetables)} train timetables")
    return all_timetables


def parse_time(time_str):
    """Parse HH:MM to minutes since midnight."""
    if not time_str:
        return None
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


def extract_travel_times(timetables):
    """Extract segment travel times from train timetables."""
    print("Extracting segment travel times...")
    
    # Collect all travel times for each segment (key: (from, to, railway))
    segment_times = defaultdict(list)
    
    for train in timetables:
        railway_id = train.get("odpt:railway")
        railway_name = railway_id.split(".")[-1] if railway_id else ""
        stops = train.get("odpt:trainTimetableObject", [])
        
        for i in range(len(stops) - 1):
            s1 = stops[i]
            s2 = stops[i + 1]
            
            # Get departure/arrival times
            t1_str = s1.get("odpt:departureTime") or s1.get("odpt:arrivalTime")
            t2_str = s2.get("odpt:arrivalTime") or s2.get("odpt:departureTime") # Use arrival at next station
            
            t1 = parse_time(t1_str)
            t2 = parse_time(t2_str)
            
            if t1 is None or t2 is None:
                continue
            
            # Calculate travel time in minutes
            travel_time = t2 - t1
            if travel_time < 0:
                travel_time += 24 * 60  # Handle midnight crossing
            
            # Skip abnormal values
            if travel_time <= 0 or travel_time > 60:
                continue
            
            # Get station IDs -> simplified names
            from_id = s1.get("odpt:departureStation") or s1.get("odpt:arrivalStation")
            to_id = s2.get("odpt:arrivalStation") or s2.get("odpt:departureStation")
            
            if from_id and to_id:
                from_name = from_id.split(".")[-1]
                to_name = to_id.split(".")[-1]
                
                # Store by direction
                segment_times[(from_name, to_name, railway_name)].append(travel_time)
    
    print(f"  -> Found {len(segment_times)} unique segments")
    return segment_times


def save_to_db(segment_times):
    """Calculate averages and save to DB."""
    print("Saving to database...")
    session = get_db_session()
    
    # Clear existing data
    session.query(StationInterval).delete()
    
    count = 0
    for (from_station, to_station, railway_name), times in segment_times.items():
        avg_time = round(sum(times) / len(times), 2)
        
        record = StationInterval(
            from_station=from_station,
            to_station=to_station,
            railway_name=railway_name,
            time_minutes=avg_time
        )
        session.add(record)
        count += 1
    
    session.commit()
    print(f"  -> Saved {count} station intervals")
    session.close()


def main():
    if not API_KEY:
        print("ERROR: ODPT_ACCESS_TOKEN not set in .env file")
        return
    
    timetables = fetch_train_timetables()
    segment_times = extract_travel_times(timetables)
    save_to_db(segment_times)
    print("Done!")


if __name__ == "__main__":
    main()
