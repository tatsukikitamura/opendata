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
    return Session()




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
                # Use owl:sameAs as primary ID
                rid = r.get("owl:sameAs") or r.get("odpt:railway")
                op = r.get("odpt:operator", "")
                
                if not rid: 
                    continue

                if operator in op or "JR-East" in rid:
                     railways.append(rid)
            
            railways = [r for r in railways if "Shinkansen" not in r]
            return sorted(list(set(railways)))
        else:
            print(f"Error fetching railways: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching railways: {e}")
        return []


def fetch_train_timetables():
    """Fetch all JR-East train timetables from ODPT API."""
    print("Fetching train timetables from ODPT API...")
    
    all_timetables = []
    

    # Import railways dynamically
    target_operators = [
        "odpt.Operator:JR-East",
        "odpt.Operator:TokyoMetro",
        "odpt.Operator:Toei"
    ]
    
    all_railways = []
    for op in target_operators:
        print(f"  Fetching railway list for {op}...")
        op_railways = fetch_all_railways(op)
        all_railways.extend(op_railways)
    
    # Dedup
    all_railways = sorted(list(set(all_railways)))
    
    if not all_railways:
        print("No railways found.")
        return []

    print(f"Total Target Railways: {len(all_railways)} lines")
    
    for railway in all_railways:
        try:
            url = f"{BASE_URL}/odpt:TrainTimetable"
            params = {
                "odpt:railway": railway,
                "acl:consumerKey": API_KEY
            }
            # Limit to Weekday to save time? Or fetch all?
            # extract_travel_times is for EDGE WEIGHTS (average). 
            # A single calendar is enough for average.
            # But earlier logic fetched EVERYTHING for storage. 
            # extract usually fetches again? No, it used requests.
            # Wait, fetch_timetables.py STORES to DB.
            # extract_travel_times.py FETCHES AGAIN?
            # Yes, line 32: def fetch_train_timetables().
            # It seems extract_travel_times fetches independently. It doesn't use DB.
            # Optimally, it SHOULD use DB or utilize the fact that we just fetched them.
            # But reusing the code is safer to avoid rewriting logic.
            # I will just update the list.
            
            # Optimization: Just fetch Weekday for edge weights.
            params["odpt:calendar"] = "odpt.Calendar:Weekday"
            
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
            
            if not t1_str or not t2_str:
                continue

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
