"""
Profile each step of the search API to find bottlenecks.
"""

import time
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from db.database import SessionLocal
from services.routing import get_graph, initialize_graph
from services.timetable.core import search_route_with_times
from services.risk import get_route_risk, get_current_delays
from services.fare_scraper import FareScraper


def profile():
    print("=" * 50)
    print("Performance Profiling - Search API")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # 1. Graph initialization
        start = time.time()
        initialize_graph()
        graph = get_graph()
        print(f"1. Graph init: {(time.time()-start)*1000:.0f}ms")

        # 2. Find routes
        start = time.time()
        routes = graph.find_routes("千葉", "東京", limit=3)
        print(f"2. find_routes: {(time.time()-start)*1000:.0f}ms ({len(routes)} routes)")

        if not routes:
            print("No routes found!")
            return
            
        route = routes[0]
        
        # 3. Timetable search
        start = time.time()
        timed = search_route_with_times(db, route, "08:00", "Weekday")
        print(f"3. search_route_with_times: {(time.time()-start)*1000:.0f}ms")
        
        # 4. Get current delays
        start = time.time()
        delays = get_current_delays()
        print(f"4. get_current_delays: {(time.time()-start)*1000:.0f}ms ({len(delays.get('delays', []))} delays)")
        
        # 5. Get route risk
        start = time.time()
        risk = get_route_risk(route, "2026-01-07T08:00")
        print(f"5. get_route_risk: {(time.time()-start)*1000:.0f}ms")
        
        # 6. Fare scraper
        start = time.time()
        fare = FareScraper.get_fare("千葉", "東京")
        print(f"6. FareScraper: {(time.time()-start)*1000:.0f}ms")
        
    finally:
        db.close()
    
    print("=" * 50)
    print("Done!")


if __name__ == "__main__":
    profile()
