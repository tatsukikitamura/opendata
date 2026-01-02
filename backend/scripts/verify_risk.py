import sys
from pathlib import Path

# Add project root and backend directory to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "backend"))

from datetime import datetime
from backend.db.database import SessionLocal
from backend.db.models import DelayLog
from backend.services.risk_service import get_route_risk

def main():
    db = SessionLocal()
    try:
        # 1. Insert a fake delay record for CURRENT TIME to verify in App immediately
        now = datetime.now()
        test_time_iso = now.isoformat()
        
        # Ensure we have a clean ISO string (although existing data has offsets sometimes)
        # backend uses fromisoformat which handles standard formats.
        
        print(f"Inserting fake delay at {test_time_iso} (Current Time)...")
        fake_log = DelayLog(
            timestamp=test_time_iso,
            trip_id="TEST_TRIP_NOW_T", # Ends with T (ChuoRapid)
            route_id="TEST_ROUTE",
            max_delay=600, # 10 mins delay
            vehicle_id="TEST_VEHICLE_NOW"
        )
        db.add(fake_log)
        db.commit()
        
        # 2. Test get_route_risk for 09:30 with ChuoRapid route (should be HIGH)
        # Note: We use current time window, but we need to pass a route structure that has "ChuoRapid" railway
        test_departure = test_time_iso # Use exact same time
        print(f"Testing risk for departure at {test_departure}...")
        
        # Fake route structure using ChuoRapid (suffix T)
        test_route = {
            "segments": [
                {"railway": "odpt.Railway:JR-East.ChuoRapid"} 
            ]
        }
        
        risk = get_route_risk(test_route, test_departure)
        print("Risk Result:", risk)
        
        if risk["level"] == "HIGH" and risk["score"] > 0:
            print("SUCCESS: High risk detected for ChuoRapid (Suffix T).")
        else:
            print("FAILURE: High risk NOT detected for ChuoRapid.")
            
        # 3. Test for Yamanote (Suffix G) - Should be LOW even if Chuo is delayed
        print(f"Testing risk for Yamanote at {test_departure} (Should ignore T suffix delay)...")
        yamanote_route = {
            "segments": [
                {"railway": "odpt.Railway:JR-East.Yamanote"} 
            ]
        }
        risk_yamanote = get_route_risk(yamanote_route, test_departure)
        print("Risk Result Yamanote:", risk_yamanote)
        
        if risk_yamanote["level"] == "LOW":
             print("SUCCESS: Low risk correctly returned for Yamanote.")
        else:
             print("FAILURE: Unexpected risk detected on Yamanote.")
             
        # 4. Test time window (12:00) - Should be LOW
        safe_departure = "2026-01-01T12:00:00"
        print(f"Testing risk for departure at {safe_departure}...")
        
        risk_safe = get_route_risk({"segments": []}, safe_departure)
        print("Risk Result:", risk_safe)
        
        if risk_safe["level"] == "LOW":
             print("SUCCESS: Low risk correctly returned.")
        else:
             print("FAILURE: Unexpected risk detected.")

    finally:
        # Cleanup (optional, but good for repeatability)
        # db.query(DelayLog).filter(DelayLog.trip_id == "TEST_TRIP").delete()
        # db.commit()
        db.close()

if __name__ == "__main__":
    main()
