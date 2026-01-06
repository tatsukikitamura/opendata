import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from google.transit import gtfs_realtime_pb2

load_dotenv(Path(__file__).parent.parent.parent / ".env")
ACCESS_TOKEN = os.environ.get("ODPT_ACCESS_TOKEN")

# Try api-challenge for Metro
METRO_ALERT_URL_CHALLENGE = "https://api-challenge.odpt.org/api/v4/gtfs/realtime/tokyometro_odpt_train_alert"
# Try api-public for Toei Alert
TOEI_ALERT_URL_PUBLIC = "https://api-public.odpt.org/api/v4/gtfs/realtime/toei_odpt_train_alert"

def fetch_feed(url):
    print(f"Fetching {url}...")
    params = {"acl:consumerKey": ACCESS_TOKEN}
    try:
        resp = requests.get(url, params=params, timeout=10)
        # Check if 403/404 without raising immediately to show error
        if resp.status_code != 200:
            print(f"  Failed with status: {resp.status_code}")
            return None
            
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(resp.content)
        print(f"  Success. Entities: {len(feed.entity)}")
        return feed
    except Exception as e:
        print(f"  Exception: {e}")
        return None

print("Testing Metro Alert (Challenge)...")
fetch_feed(METRO_ALERT_URL_CHALLENGE)

print("\nTesting Toei Alert (Public)...")
fetch_feed(TOEI_ALERT_URL_PUBLIC)
