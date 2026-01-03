import requests
import os
import zipfile
import io
from pathlib import Path
from dotenv import load_dotenv

# Load .env explicitly
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

API_KEY = os.getenv("ODPT_ACCESS_TOKEN")
BASE_URL = "https://api.odpt.org/api/v4"
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "metro_gtfs"

def fetch_metro_gtfs():
    if not API_KEY:
        print("Error: ODPT_ACCESS_TOKEN not set")
        return

    file_url = f"{BASE_URL}/files/TokyoMetro/data/TokyoMetro-Train-GTFS.zip"
    params = {"acl:consumerKey": API_KEY}
    
    print(f"Downloading Tokyo Metro GTFS from {file_url}...")
    
    try:
        resp = requests.get(file_url, params=params, stream=True)
        resp.raise_for_status()
        
        # Create directory
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Extract
        print("Extracting to", DATA_DIR)
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            z.extractall(DATA_DIR)
            
        print("Done!")
        
        # List files
        print("Extracted files:")
        for f in DATA_DIR.glob("*"):
            print(f" - {f.name}")
            
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    fetch_metro_gtfs()
