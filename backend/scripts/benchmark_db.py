"""
Benchmark PostgreSQL query performance.
Measures query times for common operations.
"""

import os
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

POSTGRES_URL = os.getenv("DATABASE_URL")
engine = create_engine(POSTGRES_URL)
Session = sessionmaker(bind=engine)


def benchmark(name: str, query: str, params: dict = None):
    """Run a query and measure time."""
    session = Session()
    try:
        start = time.time()
        result = session.execute(text(query), params or {})
        rows = result.fetchall()
        elapsed = time.time() - start
        print(f"{name}: {elapsed*1000:.1f}ms ({len(rows)} rows)")
        return elapsed
    finally:
        session.close()


def main():
    print("=" * 60)
    print("PostgreSQL Performance Benchmark")
    print("=" * 60)
    
    times = {}
    
    # 1. Simple count
    times['count_stations'] = benchmark(
        "COUNT stations",
        "SELECT COUNT(*) FROM stations"
    )
    
    # 2. Simple select
    times['select_10_stations'] = benchmark(
        "SELECT 10 stations",
        "SELECT * FROM stations LIMIT 10"
    )
    
    # 3. Name search (with index)
    times['search_by_name'] = benchmark(
        "Search station by name",
        "SELECT * FROM stations WHERE name_ja = :name",
        {"name": "東京"}
    )
    
    # 4. Route edges join
    times['route_edges'] = benchmark(
        "Route edges with stations",
        """SELECT e.*, s1.name_ja as from_name, s2.name_ja as to_name 
           FROM route_edges e
           LEFT JOIN stations s1 ON e.from_station_id = s1.id
           LEFT JOIN stations s2 ON e.to_station_id = s2.id
           LIMIT 100"""
    )
    
    # 5. Timetable query (large table)
    times['timetable_search'] = benchmark(
        "Search departures by station",
        """SELECT * FROM station_departures 
           WHERE station_name = :name AND weekday_type = :day
           ORDER BY departure_time
           LIMIT 50""",
        {"name": "東京", "day": "weekday"}
    )
    
    # 6. Train status (recent delays)
    times['recent_delays'] = benchmark(
        "Recent delays",
        """SELECT * FROM train_statuses 
           WHERE is_delayed = true 
           ORDER BY timestamp DESC 
           LIMIT 50"""
    )
    
    # 7. Connection test (just ping)
    start = time.time()
    session = Session()
    session.execute(text("SELECT 1"))
    session.close()
    times['connection'] = time.time() - start
    print(f"Connection overhead: {times['connection']*1000:.1f}ms")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    total = sum(times.values())
    print(f"Total time: {total*1000:.1f}ms")
    print(f"Average per query: {total/len(times)*1000:.1f}ms")
    
    if total > 1.0:
        print("\n⚠️ Queries are taking >1 second total - this is slow!")
        print("Possible causes: missing indexes, slow network, or DB plan limits")
    elif total > 0.5:
        print("\n⚡ Moderate performance - some room for optimization")
    else:
        print("\n✅ Good performance!")


if __name__ == "__main__":
    main()
