"""
Collect train operation status from ODPT TrainInformation API and GTFS-RT.

This script fetches train status data and saves it to daily JSONL files.
Focused on delay/incident information to calculate reliability scores.
"""
import os
import json
import datetime
import requests
from pathlib import Path
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to path to import models
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

try:
    from db.models import TrainStatus
except ImportError:
    # Fallback or better error handling if path is wrong
    print("Warning: Could not import db.models. DB functions will fail.")

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env")

# =============================================================================
# Configuration
# =============================================================================

ACCESS_TOKEN = os.environ.get("ODPT_ACCESS_TOKEN")
ACCESS_TOKEN_METRO = os.environ.get("ODPT_ACCESS_TOKEN_METRO") # Specific token for Metro

BASE_URL = "https://api-challenge.odpt.org/api/v4"
METRO_BASE_URL = "https://api.odpt.org/api/v4"  # Separate API for Metro/Toei
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "delays"

# GTFS-RT URLs
# Note: Metro requires authentication, Toei Public does not (but has limits/different content)
METRO_ALERT_URL = "https://api.odpt.org/api/v4/gtfs/realtime/tokyometro_odpt_train_alert"
TOEI_ALERT_URL = "https://api-public.odpt.org/api/v4/gtfs/realtime/toei_odpt_train_alert"
TOEI_TRIP_UPDATE_URL = "https://api-public.odpt.org/api/v4/gtfs/realtime/toei_odpt_train_trip_update"

# Timezone
JST = ZoneInfo("Asia/Tokyo")


# =============================================================================
# Core Functions
# =============================================================================

def fetch_train_information() -> list:
    """
    Fetch train information from ODPT JSON API (mainly for JR).
    Returns list of train status records.
    """
    if not ACCESS_TOKEN:
        print("Error: ODPT_ACCESS_TOKEN not set")
        return []

    url = f"{BASE_URL}/odpt:TrainInformation"
    params = {"acl:consumerKey": ACCESS_TOKEN}
    
    print(f"Fetching ODPT JSON (JR): {url}")
    
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        
        data = resp.json()
        print(f"Fetched {len(data)} records from ODPT JSON (JR)")
        return data
    except Exception as e:
        print(f"Failed to fetch ODPT JSON (JR): {e}")
        return []


def fetch_metro_train_information() -> list:
    """
    Fetch train information from ODPT JSON API for Metro and Toei.
    Uses METRO token to access api.odpt.org endpoint.
    Returns list of train status records.
    """
    token = ACCESS_TOKEN_METRO if ACCESS_TOKEN_METRO else ACCESS_TOKEN
    if not token:
        print("Error: No token available for Metro API")
        return []

    url = f"{METRO_BASE_URL}/odpt:TrainInformation"
    params = {"acl:consumerKey": token}
    
    print(f"Fetching ODPT JSON (Metro/Toei): {url}")
    
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        
        data = resp.json()
        # Filter to only include TokyoMetro and Toei
        filtered = [d for d in data if 'TokyoMetro' in d.get('odpt:operator', '') or 'Toei' in d.get('odpt:operator', '')]
        print(f"Fetched {len(filtered)} records from ODPT JSON (Metro/Toei)")
        return filtered
    except Exception as e:
        print(f"Failed to fetch ODPT JSON (Metro/Toei): {e}")
        return []


def fetch_gtfs_rt(url: str, token: str = None) -> gtfs_realtime_pb2.FeedMessage:
    """
    Fetch and parse GTFS-RT feed.
    
    Args:
        url: URL to fetch
        token: Access token to use. If None, uses default ACCESS_TOKEN. 
               Pass empty string to suppress token usage (for public APIs).
    """
    print(f"Fetching GTFS-RT: {url}")
    params = {}
    
    # Determine which token to use
    use_token = token if token is not None else ACCESS_TOKEN
    
    if use_token:
        params["acl:consumerKey"] = use_token
    
    try:
        resp = requests.get(url, params=params, timeout=30)
        # Even if 403, we might want to log it but not crash (handled by caller)
        resp.raise_for_status()
        
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(resp.content)
        print(f"Fetched {len(feed.entity)} entities from {url}")
        return feed
    except Exception as e:
        print(f"Failed to fetch GTFS-RT from {url}: {e}")
        return None


def parse_train_status(raw_data: list) -> list:
    """
    Parse raw ODPT JSON API response into cleaned records.
    """
    now_jst = datetime.datetime.now(JST)
    timestamp = now_jst.isoformat()
    
    records = []
    
    for item in raw_data:
        railway_id = item.get("odpt:railway", "")
        operator = item.get("odpt:operator", "")
        
        # Extract railway short name
        railway_name = ""
        if railway_id:
            parts = railway_id.replace("odpt.Railway:", "").split(".")
            railway_name = parts[-1] if parts else ""
        
        # Handle status
        status_raw = item.get("odpt:trainInformationStatus", {})
        if isinstance(status_raw, dict):
            status = status_raw.get("ja", str(status_raw)) or ""
        else:
            status = str(status_raw) if status_raw else ""
        
        # Handle status text
        text_raw = item.get("odpt:trainInformationText", {})
        if isinstance(text_raw, dict):
            status_text = text_raw.get("ja", str(text_raw)) or ""
        else:
            status_text = str(text_raw) if text_raw else ""
        
        # Determine if delayed
        is_delayed = "平常" not in status_text if status_text else False
        
        records.append({
            "timestamp": timestamp,
            "railway_id": railway_id,
            "railway_name": railway_name,
            "operator": operator,
            "status": status,
            "status_text": status_text,
            "is_delayed": is_delayed,
            "source": "ODPT_JSON"
        })
    
    return records


def parse_alerts(feed: gtfs_realtime_pb2.FeedMessage, operator_prefix: str) -> list:
    """
    Parse GTFS-RT Alerts into TrainStatus records.
    """
    if not feed:
        return []
    
    now_jst = datetime.datetime.now(JST)
    timestamp = now_jst.isoformat()
    records = []
    
    for entity in feed.entity:
        if not entity.HasField("alert"):
            continue
            
        alert = entity.alert
        
        # Extract text
        header_text = ""
        description_text = ""
        
        for trans in alert.header_text.translation:
            if trans.language == "ja":
                header_text = trans.text
                break
        if not header_text and alert.header_text.translation:
             header_text = alert.header_text.translation[0].text
             
        for trans in alert.description_text.translation:
            if trans.language == "ja":
                description_text = trans.text
                break
        
        status_text = f"{header_text}: {description_text}" if description_text else header_text
        
        # Find informed entities (routes)
        for informed in alert.informed_entity:
            if informed.route_id:
                # e.g. "odpt.Railway:TokyoMetro.Ginza" -> "Ginza"
                railway_id = informed.route_id
                parts = railway_id.replace("odpt.Railway:", "").split(".")
                railway_name = parts[-1] if parts else ""
                
                # Check operator prefix if needed to filter mixed feeds (usually feeds are operator specific)
                
                records.append({
                    "timestamp": timestamp,
                    "railway_id": railway_id,
                    "railway_name": railway_name,
                    "operator": operator_prefix, # Approximated
                    "status": "Service Alert",
                    "status_text": status_text,
                    "is_delayed": True, # Alerts usually mean something is wrong
                    "source": "GTFS_ALERT"
                })
    
    return records


def parse_trip_updates(feed: gtfs_realtime_pb2.FeedMessage, operator_prefix: str) -> list:
    """
    Parse GTFS-RT TripUpdates to detect delays.
    Aggregates delay info by route.
    """
    if not feed:
        return []
    
    now_jst = datetime.datetime.now(JST)
    timestamp = now_jst.isoformat()
    
    # Map: route_id -> {max_delay: int, delayed_trips: int, total_trips: int}
    route_stats = {}
    
    DELAY_THRESHOLD_SEC = 300 # 5 minutes
    
    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue
            
        tu = entity.trip_update
        route_id = tu.trip.route_id
        
        if not route_id:
            # Try to infer or log
            # print(f"Missing route_id for trip {tu.trip.trip_id}")
            continue
        
        if route_id not in route_stats:
            route_stats[route_id] = {"max_delay": 0, "delayed_trips": 0, "total_trips": 0}
            
        stats = route_stats[route_id]
        stats["total_trips"] += 1
        
        # Check delay in StopTimeUpdates
        trip_max_delay = 0
        for stu in tu.stop_time_update:
            if stu.HasField("arrival"):
                trip_max_delay = max(trip_max_delay, stu.arrival.delay)
            if stu.HasField("departure"):
                trip_max_delay = max(trip_max_delay, stu.departure.delay)
        
        stats["max_delay"] = max(stats["max_delay"], trip_max_delay)
        if trip_max_delay >= DELAY_THRESHOLD_SEC:
            stats["delayed_trips"] += 1
            
    # Convert to records
    records = []
    for route_id, stats in route_stats.items():
        if not route_id:
            continue
            
        parts = route_id.replace("odpt.Railway:", "").split(".")
        railway_name = parts[-1] if parts else ""
        
        is_delayed = stats["delayed_trips"] > 0
        
        status_text = "平常運転"
        if is_delayed:
            max_min = stats["max_delay"] // 60
            status_text = f"最大{max_min}分の遅れが発生しています"
            
        records.append({
            "timestamp": timestamp,
            "railway_id": route_id,
            "railway_name": railway_name,
            "operator": operator_prefix,
            "status": "Delay Info" if is_delayed else "Normal",
            "status_text": status_text,
            "is_delayed": is_delayed,
            "source": "GTFS_TRIP_UPDATE"
        })
        
    return records


def save_jsonl(records: list):
    """
    Save records to daily JSONL file.
    """
    if not records:
        print("No records to save.")
        return
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    now_jst = datetime.datetime.now(JST)
    today = now_jst.strftime("%Y%m%d")
    filename = DATA_DIR / f"status_{today}.jsonl"
    
    # Save as JSON Lines (one record per line)
    # We strip the 'source' field before saving to match DB schema? 
    # Or strict validation? Let's check models. 
    # Models have extra fields tolerated usually or we can keep it for debugging if JSON.
    # The importer uses: timestamp, railway_id, railway_name, operator, status, status_text, is_delayed
    # 'source' will be ignored by importer if not in model, which is fine.
    
    with open(filename, "a", encoding="utf-8") as f:
        entry = {
            "fetched_at": now_jst.isoformat(),
            "data": records
        }
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    # Count delayed records
    delayed_count = sum(1 for r in records if r["is_delayed"])
    print(f"Saved {len(records)} records ({delayed_count} delayed) to {filename}")

    print(f"Saved {len(records)} records ({delayed_count} delayed) to {filename}")


def save_to_db(records: list):
    """
    Save records to PostgreSQL database.
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not set. Skipping DB insertion.")
        return

    if not records:
        return

    # Handle 'postgres://' for SQLAlchemy compatibility (Fly.io/Heroku style, just in case)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    print(f"Connecting to DB...")
    
    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        count = 0
        for r in records:
            # Create TrainStatus object
            status = TrainStatus(
                timestamp=r["timestamp"],
                railway_id=r["railway_id"],
                railway_name=r["railway_name"],
                operator=r["operator"],
                status=r["status"],
                status_text=r["status_text"],
                is_delayed=r["is_delayed"]
            )
            session.add(status)
            count += 1
        
        session.commit()
        print(f"Successfully inserted {count} records to DB.")
    except Exception as e:
        print(f"Failed to insert to DB: {e}")
    finally:
        if 'session' in locals():
            session.close()
# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    # Skip during late night (01:30 - 04:00 JST)
    now_jst = datetime.datetime.now(JST)
    current_time = now_jst.time()
    
    skip_start = datetime.time(1, 30)
    skip_end = datetime.time(4, 0)
    
    if skip_start <= current_time <= skip_end:
        print(f"Skipping execution during late night window (01:30 - 04:00 JST). Current: {current_time}")
        exit(0)
    
    print(f"Starting collection at {now_jst}")
    
    all_records = []
    
    # 1. Fetch ODPT JSON (JR, etc)
    json_data = fetch_train_information()
    all_records.extend(parse_train_status(json_data))
    
    # 2. Fetch Metro/Toei JSON API (always returns all lines including normal operation)
    metro_json_data = fetch_metro_train_information()
    all_records.extend(parse_train_status(metro_json_data))
    
    # 3. Fetch Metro Alert (GTFS-RT) - only contains alerts during incidents
    # Skipped now since we have JSON API data above
    # metro_token = ACCESS_TOKEN_METRO if ACCESS_TOKEN_METRO else ACCESS_TOKEN
    # metro_feed = fetch_gtfs_rt(METRO_ALERT_URL, token=metro_token)
    # metro_records = parse_alerts(metro_feed, "odpt.Operator:TokyoMetro")
    # print(f"Parsed {len(metro_records)} Metro alert records")
    # all_records.extend(metro_records)
    
    # 3. Fetch Toei Alert (Public)
    # If standard URL fails (403), try public. Test script showed Public worked for TripUpdate.
    # Alert might be empty but accessible.
    toei_alert_feed = fetch_gtfs_rt(TOEI_ALERT_URL, token="") # Empty string to suppress token
    toei_alert_records = parse_alerts(toei_alert_feed, "odpt.Operator:Toei")
    print(f"Parsed {len(toei_alert_records)} Toei alert records")
    all_records.extend(toei_alert_records)
    
    # 4. Fetch Toei TripUpdate
    toei_tu_feed = fetch_gtfs_rt(TOEI_TRIP_UPDATE_URL, token="") # Empty string to suppress token
    toei_tu_records = parse_trip_updates(toei_tu_feed, "odpt.Operator:Toei")
    print(f"Parsed {len(toei_tu_records)} Toei delay records from TripUpdate")
    
    # Merge Toei: Prefer Alert over TripUpdate if duplicate for same line?
    # Logic: If Alert exists for a line, use it. If not, use TripUpdate info.
    
    existing_railways = {r["railway_id"] for r in all_records}
    
    for r in toei_tu_records:
        if r["railway_id"] not in existing_railways:
            all_records.append(r)
        else:
            # If already exists (e.g. from Alert), do we update?
            # Alerts are usually more descriptive ("Suspended"). TripUpdate is just "5 min delay".
            # Keep Alert.
            pass

    save_jsonl(all_records)
    save_to_db(all_records)
    
    print("Done.")
