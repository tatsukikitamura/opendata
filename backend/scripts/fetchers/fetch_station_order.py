"""
Fetch station order data from ODPT API and store in database.
This enables accurate direction determination for route search.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Load .env from project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(os.path.join(BASE_DIR, ".env"))


API_KEY = os.getenv("ODPT_ACCESS_TOKEN")
BASE_URL = "https://api-challenge.odpt.org/api/v4"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.db")


def get_db_session():
    """Create database session."""
    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    # Create tables if not exist
    from db.models import Base, StationOrder
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return Session(), StationOrder


def fetch_railway_data(railway_id: str) -> dict:
    """Fetch railway data including station order."""
    url = f"{BASE_URL}/odpt:Railway"
    params = {
        "owl:sameAs": railway_id,
        "acl:consumerKey": API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data[0] if data else {}
    except Exception as e:
        print(f"  Error fetching {railway_id}: {e}")
        return {}




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


def main():
    if not API_KEY:
        print("ERROR: ODPT_ACCESS_TOKEN not set in .env file")
        return
    
    print("=" * 60)
    print("Station Order Fetcher")
    print("=" * 60)
    
    # Get database session
    session, StationOrder = get_db_session()
    
    # Clear existing data
    print("\nClearing existing station order data...")
    session.query(StationOrder).delete()
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
    
    total_stations = 0
    
    print("\nFetching station order data from ODPT API...")
    
    for railway_id in railways:
        railway_name = railway_id.split(".")[-1]
        data = fetch_railway_data(railway_id)
        
        if not data:
            print(f"  {railway_name}: No data")
            continue
        
        station_order = data.get("odpt:stationOrder", [])
        
        for station_data in station_order:
            station_id = station_data.get("odpt:station", "")
            station_name = station_id.split(".")[-1] if station_id else ""
            station_index = station_data.get("odpt:index", 0)
            
            record = StationOrder(
                railway_id=railway_id,
                railway_name=railway_name,
                station_id=station_id,
                station_name=station_name,
                station_index=station_index
            )
            session.add(record)
            total_stations += 1
        
        session.commit()
        print(f"  {railway_name}: {len(station_order)} stations")
    
    print(f"\n{'=' * 60}")
    print(f"Total: {total_stations} station order records saved to database")
    print(f"Database: {DB_PATH}")
    print(f"{'=' * 60}")
    
    # Show sample data
    print("\nSample station order (ChuoRapid):")
    samples = session.query(StationOrder).filter(
        StationOrder.railway_name == "ChuoRapid"
    ).order_by(StationOrder.station_index).limit(10).all()
    
    for s in samples:
        print(f"  {s.station_index}: {s.station_name}")
    
    session.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
