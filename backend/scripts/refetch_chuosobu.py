import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.fetch_timetables import get_db_session, fetch_train_timetables, parse_train_timetable
from db.models import StationDeparture

def refetch_chuosobu():
    print("Force re-fetching Chuo-Sobu Local timetable...")
    
    # Target only ChuoSobuLocal
    target_railway = "odpt.Railway:JR-East.ChuoSobuLocal"
    railway_name = "ChuoSobuLocal"
    
    session, _ = get_db_session()
    
    try:
        # 1. Clear existing data for ChuoSobuLocal ONLY
        print(f"Clearing existing data for {railway_name}...")
        deleted = session.query(StationDeparture).filter(StationDeparture.railway_name == railway_name).delete()
        print(f"Deleted {deleted} records.")
        session.commit()
        
        # 2. Fetch new data (Split by Calendar to avoid 1000 limit)
        calendars = [
            "odpt.Calendar:Weekday",
            "odpt.Calendar:Saturday",
            "odpt.Calendar:SundayHoliday",
            "odpt.Calendar:SaturdayHoliday"
        ]
        
        # Verify valid calendars. Usually: Weekday, SaturdayHoliday (some lines), or Saturday, SundayHoliday.
        # Let's try separate.
        
        all_trains = []
        
        # Helper to fetch with params
        import requests
        URL = "https://api-challenge.odpt.org/api/v4/odpt:TrainTimetable"
        API_KEY = os.environ.get("ODPT_ACCESS_TOKEN") # Need to load environment
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
        API_KEY = os.environ.get("ODPT_ACCESS_TOKEN")

        for cal in calendars:
            print(f"Fetching {cal}...")
            params = {
                "odpt:railway": target_railway,
                "odpt:calendar": cal,
                "acl:consumerKey": API_KEY
            }
            res = requests.get(URL, params=params)
            if res.status_code == 200:
                data = res.json()
                print(f"  Got {len(data)} records for {cal}")
                all_trains.extend(data)
            else:
                print(f"  Failed {cal}: {res.status_code} {res.text[:100]}")

        print(f"Total unique trains fetched: {len(all_trains)}")
        
        # 3. Parse and Insert
        railway_records = 0
        for train in all_trains:
            records = parse_train_timetable(train)
            for rec in records:
                db_record = StationDeparture(**rec)
                session.add(db_record)
                railway_records += 1
        
        session.commit()
        print(f"Inserted {railway_records} records.")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    refetch_chuosobu()
