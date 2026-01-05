"""
Import train status data from JSONL files into the database.

Reads status_*.jsonl files and imports them into the train_statuses table.
"""
import json
import sys
from pathlib import Path
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from backend.db.database import SessionLocal, engine
from backend.db.models import Base, TrainStatus


def import_jsonl(file_path: Path, db: Session) -> int:
    """
    Import a single JSONL file into the database.
    Returns the number of records imported.
    """
    print(f"Importing {file_path.name}...")
    count = 0
    delayed_count = 0
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                data_list = record.get("data", [])
                
                for item in data_list:
                    status = TrainStatus(
                        timestamp=item.get("timestamp"),
                        railway_id=item.get("railway_id"),
                        railway_name=item.get("railway_name"),
                        operator=item.get("operator"),
                        status=item.get("status"),
                        status_text=item.get("status_text"),
                        is_delayed=item.get("is_delayed", False)
                    )
                    db.add(status)
                    count += 1
                    if item.get("is_delayed"):
                        delayed_count += 1
                        
            except json.JSONDecodeError:
                print(f"  Skipping invalid JSON line")
                continue
    
    db.commit()
    print(f"  Imported {count} records ({delayed_count} delayed)")
    return count


def main():
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    data_dir = Path(__file__).resolve().parent.parent.parent / "data" / "delays"
    print(f"Looking for data in {data_dir}")
    
    try:
        # Import all status_*.jsonl files (new format)
        jsonl_files = sorted(data_dir.glob("status_*.jsonl"))
        
        if not jsonl_files:
            print("No status_*.jsonl files found.")
            return
        
        total = 0
        for jsonl_file in jsonl_files:
            total += import_jsonl(jsonl_file, db)
        
        print(f"\nTotal: {total} records imported")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
