import time
import sys
import os
from sqlalchemy import select, func

# Add the backend directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.append(backend_dir)

from db.database import SessionLocal, engine
from db.models import TrainStatus

def profile_db_query():
    print(f"Connecting to: {engine.url}")
    print("Profiling DB Query in get_current_delays...")
    
    t0 = time.time()
    db = SessionLocal()
    t1 = time.time()
    print(f"SessionLocal(): {t1 - t0:.4f}s")
    
    try:
        t2 = time.time()
        # optimized query: use ID instead of timestamp
        latest_query = select(TrainStatus.timestamp).order_by(TrainStatus.id.desc()).limit(1)
        latest_ts = db.execute(latest_query).scalar()
        t3 = time.time()
        print(f"MAX(id) -> timestamp query: {t3 - t2:.4f}s")
        print(f"Latest timestamp: {latest_ts}")
        
        if latest_ts:
            t4 = time.time()
            query = select(TrainStatus).where(
                TrainStatus.timestamp == latest_ts,
                TrainStatus.is_delayed == True
            )
            records = db.execute(query).scalars().all()
            t5 = time.time()
            print(f"Fetch records query: {t5 - t4:.4f}s")
            print(f"Records found: {len(records)}")
            
    finally:
        db.close()

if __name__ == "__main__":
    profile_db_query()
