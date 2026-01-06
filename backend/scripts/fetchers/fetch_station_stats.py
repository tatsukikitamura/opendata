import os
import requests
import json
from dotenv import load_dotenv

# Load .env
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
dotenv_path = os.path.join(base_dir, '.env')
if not os.path.exists(dotenv_path):
    dotenv_path = os.path.join(os.path.dirname(base_dir), '.env')
load_dotenv(dotenv_path)


API_KEY = os.getenv("ODPT_ACCESS_TOKEN")
STATION_API_URL = "https://api-challenge.odpt.org/api/v4/odpt:Station"
SURVEY_API_URL = "https://api-challenge.odpt.org/api/v4/odpt:PassengerSurvey"
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "station_stats.json")

OPERATORS = [
    "odpt.Operator:JR-East",
    "odpt.Operator:TokyoMetro",
    "odpt.Operator:Toei",
    "odpt.Operator:Keio",
    "odpt.Operator:Tokyu",
    "odpt.Operator:Odakyu",
    "odpt.Operator:Seibu",
    "odpt.Operator:Tobu",
    "odpt.Operator:Keisei",
    "odpt.Operator:Keikyu",
    "odpt.Operator:SagamiRailway",
    "odpt.Operator:Yurikamome",
    "odpt.Operator:TWR",
    "odpt.Operator:MIR"
]

def load_gtfs_translations():
    """
    Load translations from GTFS files to map English station names (from URNs) 
    to Japanese station names.
    """
    translator = {}
    
    paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "Toei-Train-GTFS", "translations.txt"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "metro_gtfs", "translations.txt")
    ]
    
    for p in paths:
        if not os.path.exists(p):
            print(f"Warning: GTFS translation file not found: {p}")
            continue
        try:
            with open(p, 'r', encoding='utf-8') as f:
                # Skip header
                next(f)
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 5:
                        # table_name, field_name, field_value, language, translation
                        table, field, value, lang, trans = parts[0], parts[1], parts[2], parts[3], parts[4]
                        
                        # We are interested in stop names translated to English.
                        # The 'field_value' is typically the Japanese name (e.g., 都庁前).
                        # The 'translation' is the English name (e.g., Tochomae).
                        if table == "stops" and field == "stop_name" and lang == "en":
                            # Normalize key: remove hyphens, lowercase
                            key = trans.replace("-", "").replace(" ", "").lower()
                            # Map English key to Japanese value
                            translator[key] = value
        except Exception as e:
            print(f"Warning: Failed to load translations from {p}: {e}")
            
    return translator

def fetch_data():
    if not API_KEY:
        print("Error: ODPT_ACCESS_TOKEN not set.")
        return

    # Load GTFS fallback map
    gtfs_map = load_gtfs_translations()
    print(f"Loaded {len(gtfs_map)} station name translations from GTFS.")

    station_map = {} # URN -> Japanese Name
    name_to_count = {} # Name -> Total Count

    for operator in OPERATORS:
        print(f"Processing {operator}...")
        
        # 1. Fetch Station Metadata
        params = {
            "odpt:operator": operator,
            "acl:consumerKey": API_KEY
        }
        
        try:
            res = requests.get(STATION_API_URL, params=params)
            # res.raise_for_status() # Don't crash if one fails
            if res.status_code == 200:
                stations = res.json()
                for s in stations:
                    urn = s.get("owl:sameAs")
                    title = s.get("odpt:stationTitle", {}).get("ja")
                    if urn and title:
                        station_map[urn] = title
        except Exception as e:
            print(f"  Failed to fetch stations for {operator}: {e}")
            continue

        # 2. Fetch Passenger Survey Data
        try:
            res = requests.get(SURVEY_API_URL, params=params)
            if res.status_code == 200:
                surveys = res.json()
                print(f"  Fetched {len(surveys)} survey records.")
                
                for survey in surveys:
                    # Get latest year data
                    objects = survey.get("odpt:passengerSurveyObject", [])
                    if not objects:
                        continue
                        
                    # Sort by year descending to ensure we get the latest
                    objects.sort(key=lambda x: x.get("odpt:surveyYear", 0), reverse=True)
                    latest = objects[0]
                    count = latest.get("odpt:passengerJourneys", 0)
                    
                    # Link to name via odpt:station list
                    station_urns = survey.get("odpt:station", [])
                    
                    found_name = None
                    for urn in station_urns:
                        if urn in station_map:
                            found_name = station_map[urn]
                            break
                    
                    # Fallback to GTFS map if API missed the station
                    if not found_name:
                         for urn in station_urns:
                            # Extract suffix: odpt.Station:Toei.Oedo.Tochomae -> Tochomae
                            parts = urn.split(".")
                            if len(parts) > 1:
                                suffix = parts[-1] 
                                clean = suffix.replace("-", "").replace(" ", "").lower()
                                if clean in gtfs_map:
                                    found_name = gtfs_map[clean]
                                    break

                    if found_name:
                        name_to_count[found_name] = name_to_count.get(found_name, 0) + count
        except Exception as e:
            print(f"  Failed to fetch survey for {operator}: {e}")

    # 3. Load Local Data (User provided Tokyo Metro / Toei data)
    local_file = os.path.join(os.path.dirname(OUTPUT_FILE), "tokyo-passenger.json")
    if os.path.exists(local_file):
        print(f"Loading local data from {local_file}...")
        try:
            with open(local_file, 'r', encoding='utf-8') as f:
                local_surveys = json.load(f)
            
            print(f"  Loaded {len(local_surveys)} local records.")
            
            for survey in local_surveys:
                objects = survey.get("odpt:passengerSurveyObject", [])
                if not objects:
                    continue
                
                # Sort by year descending
                objects.sort(key=lambda x: x.get("odpt:surveyYear", 0), reverse=True)
                latest = objects[0]
                count = latest.get("odpt:passengerJourneys", 0)
                
                station_urns = survey.get("odpt:station", [])
                
                found_name = None
                for urn in station_urns:
                    if urn in station_map:
                        found_name = station_map[urn]
                        break
                
                # GTFS Fallback
                if not found_name:
                    for urn in station_urns:
                        # Extract suffix
                        parts = urn.split(".")
                        if len(parts) > 1:
                            suffix = parts[-1] 
                            clean = suffix.replace("-", "").replace(" ", "").lower()
                            if clean in gtfs_map:
                                found_name = gtfs_map[clean]
                                break
                
                if found_name:
                    name_to_count[found_name] = name_to_count.get(found_name, 0) + count
        except Exception as e:
             print(f"  Failed to load local data: {e}")

    # 4. Save to JSON
    print(f"Mapped {len(name_to_count)} unique stations with passenger data.")
    
    # Sort for readability
    sorted_stats = dict(sorted(name_to_count.items(), key=lambda item: item[1], reverse=True))
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted_stats, f, indent=2, ensure_ascii=False)
        
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_data()
