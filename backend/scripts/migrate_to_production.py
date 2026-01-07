"""
Migrate data from local SQLite to production PostgreSQL.
Transfers: station_departures, station_orders, station_intervals
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Source: Local SQLite
SQLITE_PATH = Path(__file__).resolve().parent.parent / "data.db"
sqlite_engine = create_engine(f"sqlite:///{SQLITE_PATH}")
SqliteSession = sessionmaker(bind=sqlite_engine)

# Target: Production PostgreSQL
POSTGRES_URL = os.getenv("DATABASE_URL")
if not POSTGRES_URL:
    print("ERROR: DATABASE_URL not found in .env")
    sys.exit(1)

postgres_engine = create_engine(POSTGRES_URL)
PostgresSession = sessionmaker(bind=postgres_engine)

BATCH_SIZE = 5000  # Insert in batches to avoid memory issues


def migrate_table(table_name: str, columns: list[str], truncate_first: bool = True):
    """Migrate a single table from SQLite to PostgreSQL."""
    print(f"\n{'='*60}")
    print(f"Migrating: {table_name}")
    print(f"{'='*60}")
    
    sqlite_session = SqliteSession()
    postgres_session = PostgresSession()
    
    try:
        # Get count from source
        source_count = sqlite_session.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar()
        print(f"Source records: {source_count:,}")
        
        if source_count == 0:
            print("No records to migrate.")
            return
        
        # Truncate target table if requested
        if truncate_first:
            print("Truncating target table...")
            postgres_session.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
            postgres_session.commit()
        
        # Read all data from SQLite
        print("Reading from SQLite...")
        columns_str = ", ".join(columns)
        rows = sqlite_session.execute(
            text(f"SELECT {columns_str} FROM {table_name}")
        ).fetchall()
        
        # Insert in batches
        total_inserted = 0
        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i:i + BATCH_SIZE]
            
            # Build INSERT statement with placeholders
            placeholders = ", ".join([f":{col}" for col in columns])
            insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # Convert rows to dicts
            batch_dicts = [dict(zip(columns, row)) for row in batch]
            
            postgres_session.execute(text(insert_sql), batch_dicts)
            postgres_session.commit()
            
            total_inserted += len(batch)
            print(f"  Inserted: {total_inserted:,} / {source_count:,} ({100*total_inserted/source_count:.1f}%)")
        
        # Verify
        target_count = postgres_session.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar()
        print(f"Target records after migration: {target_count:,}")
        
        if target_count == source_count:
            print(f"✅ {table_name} migration successful!")
        else:
            print(f"⚠️ Count mismatch! Source: {source_count}, Target: {target_count}")
            
    finally:
        sqlite_session.close()
        postgres_session.close()


def main():
    print("=" * 60)
    print("Data Migration: SQLite -> PostgreSQL")
    print("=" * 60)
    
    # Migrate station_orders
    migrate_table(
        "station_orders",
        ["id", "railway_id", "railway_name", "station_id", "station_name", "station_index"]
    )
    
    # Migrate station_intervals
    migrate_table(
        "station_intervals",
        ["id", "from_station", "to_station", "railway_name", "time_minutes"]
    )
    
    # Migrate station_departures (largest table)
    migrate_table(
        "station_departures",
        ["id", "station_id", "station_name", "railway_id", "railway_name", 
         "direction", "departure_time", "train_type", "destination_station", 
         "train_number", "weekday_type"]
    )
    
    print("\n" + "=" * 60)
    print("Migration complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
