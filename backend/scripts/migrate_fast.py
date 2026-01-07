"""
Fast migration using PostgreSQL COPY command.
Only migrates station_departures (orders and intervals already done).
"""

import os
import sys
import csv
import io
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

import sqlite3
import psycopg2

# Source: Local SQLite
SQLITE_PATH = Path(__file__).resolve().parent.parent / "data.db"

# Target: Production PostgreSQL
POSTGRES_URL = os.getenv("DATABASE_URL")
if not POSTGRES_URL:
    print("ERROR: DATABASE_URL not found")
    sys.exit(1)


def migrate_departures():
    print("=" * 60)
    print("Fast Migration: station_departures via COPY")
    print("=" * 60)
    
    # Connect to SQLite
    print("Connecting to SQLite...")
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_cur = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    print("Connecting to PostgreSQL...")
    pg_conn = psycopg2.connect(POSTGRES_URL)
    pg_cur = pg_conn.cursor()
    
    try:
        # Get source count
        sqlite_cur.execute("SELECT COUNT(*) FROM station_departures")
        source_count = sqlite_cur.fetchone()[0]
        print(f"Source records: {source_count:,}")
        
        # Truncate target
        print("Truncating target table...")
        pg_cur.execute("TRUNCATE TABLE station_departures RESTART IDENTITY CASCADE")
        pg_conn.commit()
        
        # Read all data from SQLite
        print("Reading from SQLite...")
        columns = ["id", "station_id", "station_name", "railway_id", "railway_name",
                   "direction", "departure_time", "train_type", "destination_station",
                   "train_number", "weekday_type"]
        
        sqlite_cur.execute(f"SELECT {', '.join(columns)} FROM station_departures")
        rows = sqlite_cur.fetchall()
        print(f"Loaded {len(rows):,} rows")
        
        # Create CSV in memory
        print("Creating CSV buffer...")
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerows(rows)
        buffer.seek(0)
        
        # Use COPY to bulk load
        print("Executing COPY command...")
        pg_cur.copy_expert(
            f"COPY station_departures ({', '.join(columns)}) FROM STDIN WITH CSV",
            buffer
        )
        pg_conn.commit()
        
        # Verify
        pg_cur.execute("SELECT COUNT(*) FROM station_departures")
        target_count = pg_cur.fetchone()[0]
        print(f"Target records: {target_count:,}")
        
        if target_count == source_count:
            print("✅ Migration successful!")
        else:
            print(f"⚠️ Count mismatch! Source: {source_count}, Target: {target_count}")
            
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    migrate_departures()
