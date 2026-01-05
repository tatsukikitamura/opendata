"""
Collect train operation status from ODPT TrainInformation API.

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

# Load .env from project root
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# =============================================================================
# Configuration
# =============================================================================

ACCESS_TOKEN = os.environ.get("ODPT_ACCESS_TOKEN")
BASE_URL = "https://api-challenge.odpt.org/api/v4"
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "delays"

# Timezone
JST = ZoneInfo("Asia/Tokyo")


# =============================================================================
# Core Functions
# =============================================================================

def fetch_train_information() -> list:
    """
    Fetch train information from ODPT API.
    Returns list of train status records.
    """
    if not ACCESS_TOKEN:
        print("Error: ODPT_ACCESS_TOKEN not set")
        return []

    url = f"{BASE_URL}/odpt:TrainInformation"
    params = {"acl:consumerKey": ACCESS_TOKEN}
    
    print(f"Fetching: {url}")
    
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    
    data = resp.json()
    print(f"Fetched {len(data)} records")
    
    return data


def parse_train_status(raw_data: list) -> list:
    """
    Parse raw API response into cleaned records.
    """
    now_jst = datetime.datetime.now(JST)
    timestamp = now_jst.isoformat()
    
    records = []
    
    for item in raw_data:
        railway_id = item.get("odpt:railway", "")
        operator = item.get("odpt:operator", "")
        
        # Extract railway short name (e.g., "ChuoRapid" from "odpt.Railway:JR-East.ChuoRapid")
        railway_name = ""
        if railway_id:
            parts = railway_id.replace("odpt.Railway:", "").split(".")
            railway_name = parts[-1] if parts else ""
        
        # Handle status (can be dict or string)
        status_raw = item.get("odpt:trainInformationStatus", {})
        if isinstance(status_raw, dict):
            status = status_raw.get("ja", str(status_raw)) or ""
        else:
            status = str(status_raw) if status_raw else ""
        
        # Handle status text (can be dict or string)
        text_raw = item.get("odpt:trainInformationText", {})
        if isinstance(text_raw, dict):
            status_text = text_raw.get("ja", str(text_raw)) or ""
        else:
            status_text = str(text_raw) if text_raw else ""
        
        # Determine if delayed (not normal operation)
        is_delayed = "平常" not in status_text if status_text else False
        
        records.append({
            "timestamp": timestamp,
            "railway_id": railway_id,
            "railway_name": railway_name,
            "operator": operator,
            "status": status,
            "status_text": status_text,
            "is_delayed": is_delayed
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
    with open(filename, "a", encoding="utf-8") as f:
        entry = {
            "fetched_at": now_jst.isoformat(),
            "data": records
        }
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    # Count delayed records
    delayed_count = sum(1 for r in records if r["is_delayed"])
    print(f"Saved {len(records)} records ({delayed_count} delayed) to {filename}")


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
    
    # Fetch and process
    raw_data = fetch_train_information()
    records = parse_train_status(raw_data)
    save_jsonl(records)
    
    print("Done.")
