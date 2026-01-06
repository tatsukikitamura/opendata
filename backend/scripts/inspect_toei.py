import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

TOEI_TRIP_UPDATE_URL = "https://api-public.odpt.org/api/v4/gtfs/realtime/toei_odpt_train_trip_update"

def inspect_feed():
    print(f"Fetching {TOEI_TRIP_UPDATE_URL}...")
    try:
        resp = requests.get(TOEI_TRIP_UPDATE_URL, timeout=10)
        resp.raise_for_status()
        
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(resp.content)
        print(f"Entities: {len(feed.entity)}")
        
        if len(feed.entity) > 0:
            print("\n--- Sample Entity (Raw string) ---")
            print(feed.entity[0])
            
            print("\n--- Sample Entity (Dict) ---")
            # Convert to dict to see fields that might be defaulted/hidden in str
            print(MessageToDict(feed.entity[0]))
            
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    inspect_feed()
