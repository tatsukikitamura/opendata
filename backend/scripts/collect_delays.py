import os
import requests
import json
import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

from google.transit import gtfs_realtime_pb2

# Configuration
GTFS_RT_URL = "https://api-challenge.odpt.org/api/v4/gtfs/realtime/jreast_odpt_train_trip_update"
ACCESS_TOKEN = os.environ.get("ODPT_ACCESS_TOKEN")
# Save data relative to this script: backend/scripts/../data/delays -> backend/data/delays
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "delays"

def fetch_gtfs_rt():
    """Fetch GTFS-RT TripUpdate data and return as cleaned JSON list."""
    if not ACCESS_TOKEN:
        print("Error: ODPT_ACCESS_TOKEN not set")
        return None

    try:
        url = f"{GTFS_RT_URL}?acl:consumerKey={ACCESS_TOKEN}"
        print(f"Fetching: {url}")
        
        resp = requests.get(url)
        resp.raise_for_status()
        
        # Parse GTFS-RT protobuf
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(resp.content)
        
        timestamp = datetime.datetime.now().isoformat()
        cleaned_data = []
        
        for entity in feed.entity:
            if not entity.HasField("trip_update"):
                continue
                
            trip_update = entity.trip_update
            trip = trip_update.trip
            
            # Extract max delay for this trip
            max_delay = 0
            for update in trip_update.stop_time_update:
                delay = 0
                if update.HasField("arrival") and update.arrival.HasField("delay"):
                    delay = update.arrival.delay
                elif update.HasField("departure") and update.departure.HasField("delay"):
                    delay = update.departure.delay
                
                if delay > max_delay:
                    max_delay = delay
            
            # Serialize protobuf objects to dict for JSON storage
            cleaned_data.append({
                "timestamp": timestamp,
                "trip_id": trip.trip_id,
                "route_id": trip.route_id,
                "max_delay_seconds": max_delay,
                "vehicle_id": trip_update.vehicle.id if trip_update.HasField("vehicle") else None
            })

        return cleaned_data

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


# ... existing code ...

# Load .env for local development
load_dotenv()

from google.transit import gtfs_realtime_pb2


# ... existing fetch_gtfs_rt ...

from zoneinfo import ZoneInfo

# ...

def save_json(data):
    """Save data to daily JSON Lines file."""
    if not data:
        print("No data to save.")
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Use JST for daily filename
    jst = ZoneInfo("Asia/Tokyo")
    now_jst = datetime.datetime.now(jst)
    today = now_jst.strftime("%Y%m%d")
    filename = DATA_DIR / f"delay_{today}.jsonl"
    
    with open(filename, "a", encoding="utf-8") as f:
        # Save as one JSON object per line (JSON Lines)
        record = {
            "fetched_at": now_jst.isoformat(),
            "data": data
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    print(f"Appended {len(data)} records to {filename}")

if __name__ == "__main__":
    # Skip during late night (01:30 - 04:00 JST)
    jst = ZoneInfo("Asia/Tokyo")
    now_jst = datetime.datetime.now(jst)
    current_time = now_jst.time()
    
    skip_start = datetime.datetime.strptime("01:30", "%H:%M").time()
    skip_end = datetime.datetime.strptime("04:00", "%H:%M").time()
    
    if skip_start <= current_time <= skip_end:
        print(f"Skipping execution during late night maintenance window (01:30 - 04:00 JST). Current JST: {current_time}")
        exit(0)
        
    print(f"Starting collection at {now_jst}")
    data = fetch_gtfs_rt()
    save_json(data)
