import json
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select

# Add parent directory of backend to path (project root)
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db.database import SessionLocal, engine
from backend.db.models import Base, DelayLog

def import_jsonl(file_path: Path, db: Session):
    print(f"Importing {file_path}...")
    count = 0
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                # Structure: { "fetched_at": "...", "data": [ { "timestamp":..., "trip_id":... }, ... ] }
                
                data_list = record.get("data", [])
                for item in data_list:
                    # Optional: Check for duplicates (expensive for large datasets, skipping for now based on simplicity request)
                    # For a robust solution, we might want to check (trip_id, timestamp) existence.
                    
                    log = DelayLog(
                        timestamp=item.get("timestamp"),
                        trip_id=item.get("trip_id"),
                        route_id=item.get("route_id"),
                        max_delay=item.get("max_delay_seconds", 0),
                        vehicle_id=item.get("vehicle_id")
                    )
                    db.add(log)
                    count += 1
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line in {file_path}")
                continue
                
    db.commit()
    print(f"Imported {count} records from {file_path}")

def main():
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    data_dir = Path(__file__).resolve().parent.parent / "data" / "delays"
    print(f"Looking for data in {data_dir}")
    
    try:
        # Import all .jsonl files
        jsonl_files = sorted(data_dir.glob("*.jsonl"))
        
        if not jsonl_files:
            print("No .jsonl files found.")
            return

        for jsonl_file in jsonl_files:
             import_jsonl(jsonl_file, db)
             
    finally:
        db.close()

if __name__ == "__main__":
    main()
