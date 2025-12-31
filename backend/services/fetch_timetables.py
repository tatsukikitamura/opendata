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

load_dotenv(dotenv_path="../.env")

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
    
    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  Error fetching {railway_id}: {e}")
        return []


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
    
    # Get calendar
    calendar = train_data.get("odpt:calendar", "")
    if "Weekday" in calendar:
        weekday_type = "Weekday"
    elif "Saturday" in calendar:
        weekday_type = "Saturday"
    else:
        weekday_type = "Holiday"
        
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
    
    # Railways to fetch
    railways = [
        "odpt.Railway:JR-East.ChuoRapid",
        "odpt.Railway:JR-East.Yamanote",
        "odpt.Railway:JR-East.ChuoSobuLocal",
        "odpt.Railway:JR-East.SobuRapid",
        "odpt.Railway:JR-East.JobanRapid",
        "odpt.Railway:JR-East.JobanLocal",
        "odpt.Railway:JR-East.KeihinTohokuNegishi",
        "odpt.Railway:JR-East.SaikyoKawagoe",
        "odpt.Railway:JR-East.ShonanShinjuku",
        "odpt.Railway:JR-East.Tokaido",
        "odpt.Railway:JR-East.Yokosuka",
        "odpt.Railway:JR-East.Takasaki",
        "odpt.Railway:JR-East.Utsunomiya",
        "odpt.Railway:JR-East.Musashino",
        "odpt.Railway:JR-East.Keiyo",
        "odpt.Railway:JR-East.Nambu",
        "odpt.Railway:JR-East.Yokohama",
    ]
    
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
