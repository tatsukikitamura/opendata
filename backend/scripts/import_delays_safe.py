"""
Import train status data from JSONL files into PostgreSQL,
avoiding duplicates based on timestamp + railway_id.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

import psycopg2
from psycopg2.extras import execute_values


def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not found")
        return
    
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    data_dir = Path(__file__).resolve().parent.parent / "data" / "delays"
    print(f"Looking for data in {data_dir}")
    
    # Get existing timestamps to avoid duplicates
    print("Loading existing records to check duplicates...")
    cur.execute("SELECT DISTINCT timestamp, railway_id FROM train_statuses")
    existing = set((row[0], row[1]) for row in cur.fetchall())
    print(f"Found {len(existing)} existing unique (timestamp, railway_id) pairs")
    
    # Process all JSONL files
    jsonl_files = sorted(data_dir.glob("status_*.jsonl"))
    if not jsonl_files:
        print("No status_*.jsonl files found.")
        return
    
    total_added = 0
    total_skipped = 0
    
    for jsonl_file in jsonl_files:
        print(f"\nProcessing {jsonl_file.name}...")
        records_to_insert = []
        
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    data_list = record.get("data", [])
                    
                    for item in data_list:
                        ts = item.get("timestamp")
                        railway_id = item.get("railway_id", "")
                        
                        # Skip if already exists
                        if (ts, railway_id) in existing:
                            total_skipped += 1
                            continue
                        
                        records_to_insert.append((
                            ts,
                            railway_id,
                            item.get("railway_name", ""),
                            item.get("operator", ""),
                            item.get("status", ""),
                            item.get("status_text", ""),
                            item.get("is_delayed", False)
                        ))
                        
                        # Add to existing set to prevent duplicates within files
                        existing.add((ts, railway_id))
                        
                except json.JSONDecodeError:
                    continue
        
        if records_to_insert:
            execute_values(
                cur,
                """INSERT INTO train_statuses 
                   (timestamp, railway_id, railway_name, operator, status, status_text, is_delayed)
                   VALUES %s""",
                records_to_insert
            )
            conn.commit()
            print(f"  Added {len(records_to_insert)} records")
            total_added += len(records_to_insert)
        else:
            print(f"  No new records to add")
    
    # Verify final count
    cur.execute("SELECT COUNT(*) FROM train_statuses")
    final_count = cur.fetchone()[0]
    
    print(f"\n{'='*50}")
    print(f"Total added: {total_added}")
    print(f"Total skipped (duplicates): {total_skipped}")
    print(f"Final record count: {final_count}")
    print(f"{'='*50}")
    
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
