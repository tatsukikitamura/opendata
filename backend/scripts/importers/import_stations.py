import sys
import os
import requests
import csv
from pathlib import Path
from dotenv import load_dotenv

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from db.database import SessionLocal, engine
from db.models import Station, Railway
from services.constants import (
    ODPT_BASE_URL,
    ALL_OPERATORS,
    OPERATOR_TOKYO_METRO,
    OPERATOR_TOEI,
    GTFS_METRO_CODES,
    GTFS_TOEI_CODES,
    METRO_TOEI_RAILWAY_INFO
)


load_dotenv(dotenv_path=BASE_DIR.parent / ".env")
API_KEY = os.getenv("ODPT_ACCESS_TOKEN")


def import_railways(db):
    print("Importing Railways...")
    railway_map = {} # store for cross-ref

    # 1. Fetch from ODPT
    for operator in ALL_OPERATORS:
        print(f"  Fetching for {operator}...")
        try:
            url = f"{ODPT_BASE_URL}/odpt:Railway"
            params = {"odpt:operator": operator, "acl:consumerKey": API_KEY}
            res = requests.get(url, params=params)
            res.raise_for_status()
            data = res.json()
            
            for item in data:
                rid = item["owl:sameAs"]
                title = item.get("odpt:railwayTitle", {})
                
                # Check if we have better manual override for Metro/Toei
                name_ja = title.get("ja", item.get("dc:title"))
                name_en = title.get("en", "")
                
                if rid in METRO_TOEI_RAILWAY_INFO:
                    name_ja = METRO_TOEI_RAILWAY_INFO[rid]["name_ja"]
                    name_en = METRO_TOEI_RAILWAY_INFO[rid]["name_en"]

                railway = Railway(
                    id=rid,
                    name_ja=name_ja,
                    name_en=name_en,
                    operator_id=operator
                )
                db.merge(railway)
                railway_map[rid] = railway
                
        except Exception as e:
            print(f"  Error fetching railways for {operator}: {e}")

    db.commit()
    print("  Railways committed.")
    return railway_map

def import_stations(db):
    print("Importing Stations...")
    
    # 1. Fetch from ODPT (JR mostly)
    # We fetch for specific operators that work well with API
    # For Metro/Toei, API station data often lacks coordinates or correct linking in some contexts,
    # but let's fetch ALL from API first as base, then overlay GTFS for Metro/Toei if needed.
    # actually routing.py said "Metro/Toei seems to fail" or was incomplete.
    # Let's trust routing.py's legacy logic: Fetch JR from API.
    
    jr_stations_count = 0
    try:
        url = f"{ODPT_BASE_URL}/odpt:Station"
        params = {"odpt:operator": "odpt.Operator:JR-East", "acl:consumerKey": API_KEY}
        print("  Fetching JR-East Stations from API...")
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()
        
        for item in data:
            sid = item["owl:sameAs"]
            title = item.get("odpt:stationTitle", {})
            
            s = Station(
                id=sid,
                name_ja=title.get("ja", item.get("dc:title")),
                name_en=title.get("en"),
                railway_id=item.get("odpt:railway"),
                station_code=item.get("odpt:stationCode"),
                lat=item.get("geo:lat"),
                lon=item.get("geo:long")
            )
            db.merge(s)
            jr_stations_count += 1
            
    except Exception as e:
        print(f"  Error fetching JR stations: {e}")

    print(f"  Imported {jr_stations_count} JR stations.")
    
    # 2. Import GTFS (Metro / Toei)
    # This logic mimics routing.py _load_gtfs_stations_data
    gtfs_base = BASE_DIR / "data"
    gtfs_dirs = [
        {"path": gtfs_base / "metro_gtfs", "type": "Metro", "codes": GTFS_METRO_CODES, "op": "TokyoMetro"},
        {"path": gtfs_base / "Toei-Train-GTFS", "type": "Toei", "codes": GTFS_TOEI_CODES, "op": "Toei"}
    ]
    
    gtfs_count = 0
    for g in gtfs_dirs:
        path = g["path"]
        if not path.exists():
            print(f"  Skipping {g['type']} (not found at {path})")
            continue
            
        print(f"  Loading {g['type']} from GTFS...")
        
        # Load translations
        translations = {}
        trans_file = path / "translations.txt"
        if trans_file.exists():
            with open(trans_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("table_name") == "stops" and row.get("field_name") == "stop_name":
                        if row.get("language") == "en":
                            translations[row.get("field_value")] = row.get("translation")
        
        # Load stations
        stops_file = path / "stops.txt"
        if stops_file.exists():
            with open(stops_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stop_code = row.get("stop_code")
                    stop_name = row["stop_name"]
                    if not stop_code: continue
                    
                    stop_name_en = translations.get(stop_name, stop_name) # Fallback
                    
                    # Infer railway
                    prefix = stop_code[0]
                    suffix = g["codes"].get(prefix)
                    
                    # Fallback check (sometimes data is mixed?)
                    if not suffix:
                        if prefix in GTFS_METRO_CODES: 
                            suffix = GTFS_METRO_CODES[prefix]
                            op_prefix = "TokyoMetro"
                        elif prefix in GTFS_TOEI_CODES:
                            suffix = GTFS_TOEI_CODES[prefix]
                            op_prefix = "Toei"
                        else:
                            continue
                    else:
                        op_prefix = g["op"]
                        
                    railway_id = f"odpt.Railway:{op_prefix}.{suffix}"
                    station_id = f"gtfs.Station:{op_prefix}.{suffix}.{stop_code}"
                    
                    s = Station(
                        id=station_id,
                        name_ja=stop_name,
                        name_en=stop_name_en,
                        railway_id=railway_id,
                        station_code=stop_code,
                        lat=float(row.get("stop_lat", 0) or 0),
                        lon=float(row.get("stop_lon", 0) or 0)
                    )
                    db.merge(s)
                    gtfs_count += 1
                    
    db.commit()
    print(f"  Imported {gtfs_count} GTFS stations.")

def main():
    if not API_KEY:
        print("Error: ODPT_ACCESS_TOKEN not found.")
        return

    db = SessionLocal()
    try:
        import_railways(db)
        import_stations(db)
        print("Station import complete.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
