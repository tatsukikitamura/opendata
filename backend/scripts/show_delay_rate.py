import sys
from pathlib import Path
from sqlalchemy import func, case
from sqlalchemy.orm import Session

# Add project root and backend directory to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "backend"))

from backend.db.database import SessionLocal
from backend.db.models import DelayLog

def main():
    db = SessionLocal()
    try:
        print("Calculating delay rates (Delayed / Total)...")
        
        # 1. Total records
        total_count = db.query(func.count(DelayLog.id)).scalar()
        
        # 2. Total delayed records
        total_delayed = db.query(func.count(DelayLog.id)).filter(DelayLog.max_delay > 0).scalar()
        
        if total_count == 0:
            print("No data found in delay_logs.")
            return

        total_rate = (total_delayed / total_count) * 100
        print(f"Total: {total_delayed}/{total_count} ({total_rate:.2f}%)")
        print("-" * 40)
        
        # 3. Group by Route (using trip_id suffix as simplistic route code)
        # Note: SQLite doesn't have right() function by default, using substr
        # Assuming last character is route code
        
        # Fetch all needed fields to process in Python for simplicity and flexibility
        # (Given dataset size ~60k, this is acceptable)
        logs = db.query(DelayLog.trip_id, DelayLog.max_delay).all()
        
        route_stats = {}
        
        for trip_id, max_delay in logs:
            if not trip_id:
                continue
                
            # Extract route code (last character)
            route_code = trip_id[-1]
            if not route_code.isalpha():
                route_code = "Unknown"
            
            if route_code not in route_stats:
                route_stats[route_code] = {"total": 0, "delayed": 0}
            
            route_stats[route_code]["total"] += 1
            if max_delay > 0:
                route_stats[route_code]["delayed"] += 1
        
        # Sort by total count desc
        sorted_routes = sorted(route_stats.items(), key=lambda x: x[1]["total"], reverse=True)
        
        for route, stats in sorted_routes:
            total = stats["total"]
            delayed = stats["delayed"]
            rate = (delayed / total) * 100 if total > 0 else 0
            print(f"Route {route}: {delayed}/{total} ({rate:.2f}%)")

    finally:
        db.close()

if __name__ == "__main__":
    main()
