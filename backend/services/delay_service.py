"""
GTFS-RT Delay Service - Fetches and aggregates route-level delays.

This service fetches real-time train delay information from GTFS-RT API
and provides route-level delay summaries with simple caching.
"""

import os
import time
import logging
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

logger = logging.getLogger(__name__)


# ==============================================================================
# Configuration
# ==============================================================================

API_KEY = os.getenv("ODPT_ACCESS_TOKEN")
CACHE_TTL_SECONDS = 60
MIN_DELAY_SECONDS = 60  # Only report delays >= 1 minute


# Import route code mappings from shared constants
from services.constants import (
    ROUTE_CODE_TO_RAILWAY,
    RAILWAY_TO_ROUTE_CODE,
    ROUTE_CODE_TO_DISPLAY_NAME,
    GTFS_RT_URL,
)



# ==============================================================================
# Cache
# ==============================================================================

@dataclass
class DelayCache:
    """Simple time-based cache for delay data."""
    data: Dict[str, int]
    timestamp: float
    
    def is_valid(self) -> bool:
        return time.time() - self.timestamp < CACHE_TTL_SECONDS


_cache: Optional[DelayCache] = None


# ==============================================================================
# Core Functions
# ==============================================================================

def _fetch_gtfs_rt() -> Optional[bytes]:
    """Fetch raw GTFS-RT data from API."""
    if not API_KEY:
        logger.warning("ODPT_ACCESS_TOKEN not set")
        return None
    
    try:
        response = requests.get(
            GTFS_RT_URL,
            params={"acl:consumerKey": API_KEY},
            timeout=10
        )
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logger.error(f"Failed to fetch GTFS-RT: {e}")
        return None


def _parse_delays(raw_data: bytes) -> Dict[str, List[int]]:
    """Parse GTFS-RT data and extract delays grouped by route code."""
    try:
        from google.transit import gtfs_realtime_pb2
    except ImportError:
        logger.error("gtfs-realtime-bindings not installed")
        return {}
    
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(raw_data)
    
    route_delays: Dict[str, List[int]] = {}
    
    for entity in feed.entity:
        if not entity.HasField('trip_update'):
            continue
        
        trip_update = entity.trip_update
        trip_id = trip_update.trip.trip_id
        
        if not trip_id:
            continue
        
        # Extract route code from trip_id suffix
        route_code = trip_id[-1] if trip_id[-1].isalpha() else None
        if not route_code:
            continue
        
        # Collect delays from stop time updates
        for stop_update in trip_update.stop_time_update:
            delay = 0
            if stop_update.HasField('arrival'):
                delay = stop_update.arrival.delay
            elif stop_update.HasField('departure'):
                delay = stop_update.departure.delay
            
            if delay > 0:
                if route_code not in route_delays:
                    route_delays[route_code] = []
                route_delays[route_code].append(delay)
    
    return route_delays


def _aggregate_delays(route_delays: Dict[str, List[int]]) -> Dict[str, int]:
    """Calculate average delay per route, filtering out minor delays."""
    result = {}
    
    for route_code, delays in route_delays.items():
        if not delays:
            continue
        
        avg_delay = sum(delays) // len(delays)
        if avg_delay >= MIN_DELAY_SECONDS:
            result[route_code] = avg_delay
    
    return result


# ==============================================================================
# Public API
# ==============================================================================

def get_route_delays() -> Dict[str, int]:
    """
    Get current delays for all routes.
    
    Returns:
        Dict mapping route code to average delay in seconds.
        Example: {"T": 180, "H": 240}
    """
    global _cache
    
    # Return cached data if still valid
    if _cache and _cache.is_valid():
        return _cache.data
    
    # Fetch and parse new data
    raw_data = _fetch_gtfs_rt()
    if not raw_data:
        return _cache.data if _cache else {}
    
    route_delays = _parse_delays(raw_data)
    aggregated = _aggregate_delays(route_delays)
    
    # Update cache
    _cache = DelayCache(data=aggregated, timestamp=time.time())
    
    return aggregated


def check_route_delay(railway_name: str) -> Optional[int]:
    """
    Check if a specific railway has delays.
    
    Args:
        railway_name: English railway name (e.g., "ChuoRapid", "Yamanote")
    
    Returns:
        Delay in seconds, or None if no significant delay.
    """
    delays = get_route_delays()
    route_code = RAILWAY_TO_ROUTE_CODE.get(railway_name)
    
    if route_code and route_code in delays:
        return delays[route_code]
    
    return None


def get_delay_summary() -> Dict[str, Dict]:
    """
    Get a human-readable summary of all current delays.
    
    Returns:
        Dict with display names as keys and delay info as values.
        Example: {"中央線快速": {"delay_seconds": 180, "delay_minutes": 3}}
    """
    delays = get_route_delays()
    
    summary = {}
    for code, delay_sec in delays.items():
        name = ROUTE_CODE_TO_DISPLAY_NAME.get(code, f"Route-{code}")
        summary[name] = {
            "route_code": code,
            "delay_seconds": delay_sec,
            "delay_minutes": delay_sec // 60
        }
    
    return summary
