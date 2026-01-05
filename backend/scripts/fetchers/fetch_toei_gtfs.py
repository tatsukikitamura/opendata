"""
Fetch and extract Toei Subway GTFS data.
"""
import os
import requests
import zipfile
import io
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")
ACCESS_TOKEN = os.environ.get("ODPT_ACCESS_TOKEN")

# URL provided by user
GTFS_URL = f"https://api.odpt.org/api/v4/files/Toei/data/Toei-Train-GTFS.zip?acl:consumerKey={ACCESS_TOKEN}"
TARGET_DIR = Path(__file__).parent.parent.parent / "data" / "toei_gtfs"

def main():
    if not ACCESS_TOKEN:
        print("Error: ODPT_ACCESS_TOKEN not set")
        return

    print(f"Downloading Toei GTFS from {GTFS_URL.replace(ACCESS_TOKEN, '***')}...")
    
    try:
        resp = requests.get(GTFS_URL)
        resp.raise_for_status()
        
        print("Download complete. Extracting...")
        if not TARGET_DIR.exists():
            TARGET_DIR.mkdir(parents=True)
            
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            zf.extractall(TARGET_DIR)
            
        print(f"Extracted to {TARGET_DIR}")
        
        # Verify contents
        files = list(TARGET_DIR.glob("*"))
        print(f"Files: {[f.name for f in files]}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
