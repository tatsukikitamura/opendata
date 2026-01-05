import os
import requests
import json
from dotenv import load_dotenv

# Load .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path)

API_KEY = os.getenv("ODPT_ACCESS_TOKEN")
STATION_API_URL = "https://api-challenge.odpt.org/api/v4/odpt:Station"
SURVEY_API_URL = "https://api-challenge.odpt.org/api/v4/odpt:PassengerSurvey"
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "station_stats.json")

def fetch_data():
    if not API_KEY:
        print("Error: ODPT_ACCESS_TOKEN not set.")
        return

    # 1. Fetch Station Metadata (URN -> Name mapping)
    print("Fetching Station metadata...")
    station_map = {} # URN -> Japanese Name
    
    params = {
        "odpt:operator": "odpt.Operator:JR-East",
        "acl:consumerKey": API_KEY
    }
    
    try:
        res = requests.get(STATION_API_URL, params=params)
        res.raise_for_status()
        stations = res.json()
        print(f"Fetched {len(stations)} stations.")
        
        for s in stations:
            urn = s.get("owl:sameAs")
            title = s.get("odpt:stationTitle", {}).get("ja")
            if urn and title:
                station_map[urn] = title
                
    except Exception as e:
        print(f"Failed to fetch stations: {e}")
        return

    # 2. Fetch Passenger Survey Data
    print("Fetching Passenger Survey data...")
    name_to_count = {} # Name -> Max Count
    
    try:
        res = requests.get(SURVEY_API_URL, params=params)
        res.raise_for_status()
        surveys = res.json()
        print(f"Fetched {len(surveys)} survey records.")
        
        for survey in surveys:
            # Get latest year data
            objects = survey.get("odpt:passengerSurveyObject", [])
            if not objects:
                continue
                
            # Sort by year descending
            objects.sort(key=lambda x: x.get("odpt:surveyYear", 0), reverse=True)
            latest = objects[0]
            count = latest.get("odpt:passengerJourneys", 0)
            
            # Link to name via odpt:station list
            station_urns = survey.get("odpt:station", [])
            
            # Find the Japanese name for this survey record
            # (A survey record might be linked to multiple URNs representing the same physical station on different lines)
            # We just need one valid name match.
            found_name = None
            for urn in station_urns:
                if urn in station_map:
                    found_name = station_map[urn]
                    break
            
            if found_name:
                # Store the count. If duplicate names exist (rare for this dataset structure?), take max?
                # Actually, the structure suggests 1 survey record = 1 station.
                name_to_count[found_name] = count
                
    except Exception as e:
        print(f"Failed to fetch survey: {e}")
        return

    # 3. Save to JSON
    print(f"Mapped {len(name_to_count)} stations with passenger data.")
    
    # Sort for readability
    sorted_stats = dict(sorted(name_to_count.items(), key=lambda item: item[1], reverse=True))
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted_stats, f, indent=2, ensure_ascii=False)
        
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_data()
