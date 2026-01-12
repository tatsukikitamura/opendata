"""
Risk Service - Calculate delay risk for routes based on historical train status data.

Uses TrainStatus records from odpt:TrainInformation API to calculate
the probability of delays for each railway line.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import TrainStatus
from .constants import RAILWAY_JA_TO_EN, RAILWAY_EN_TO_JA, METRO_TOEI_RAILWAY_INFO

# Cache for current delays (avoid repeated DB queries)
_current_delays_cache = None
_current_delays_cache_time = None
CACHE_TTL_SECONDS = 300  # Cache valid for 300 seconds (5 minutes)


def get_route_risk(route: dict, departure_time: str) -> dict:
    """
    Calculate risk score based on historical delay data.
    
    Args:
        route: Route dict with segments containing railway info
        departure_time: ISO format departure time
    
    Returns:
        dict: {
            "score": int (number of delay incidents),
            "level": str ("LOW", "MEDIUM", "HIGH"),
            "reasons": list[str] (delay reasons for display)
        }
    """
    db = SessionLocal()
    max_delay_rate = 0.0  # Track highest delay rate across all railways
    reasons = []
    
    try:
        railways_checked = set()
        segments = route.get("segments", [])
        
        for segment in segments:
            railway = segment.get("railway")
            if not railway:
                continue
            
            # Normalize to English short code (e.g., "ChuoRapid")
            railway_short = _normalize_railway_name(railway)
            
            if railway_short in railways_checked:
                continue
            railways_checked.add(railway_short)
            
            # Query train status for this railway
            stats = _get_railway_stats(db, railway_short)
            
            if stats["total"] > 0:
                rate_pct = (stats["delayed"] / stats["total"]) * 100
                max_delay_rate = max(max_delay_rate, rate_pct)
                
                if stats["delayed"] > 0:
                    # Get latest delay reason
                    latest_reason = stats.get("latest_reason", "")
                    
                    # Resolve Japanese Name for display
                    # 1. Try EN -> JA (for JR short codes)
                    display_name = RAILWAY_EN_TO_JA.get(railway_short, railway_short)
                    
                    # 2. If it looks like an ID or we have info for it (Metro/Toei often normalized to short code though)
                    # Note: _normalize_railway_name returns English short code for JR, but suffixes for others.
                    # Let's try to map back if needed.
                    # Actually, _normalize_railway_name implementation:
                    # - JR: "odpt.Railway:JR-East.ChuoRapid" -> "ChuoRapid" -> "中央線快速" (via RAILWAY_EN_TO_JA)
                    # - Metro: "odpt.Railway:TokyoMetro.Ginza" -> "Ginza"
                    # - Toei: "odpt.Railway:Toei.Asakusa" -> "Asakusa"
                    
                    # Check if the short code is in our constants values to find key, or direct map?
                    # RAILWAY_EN_TO_JA handles JR short codes.
                    # For Metro/Toei, we might need a mapping from "Ginza" to "銀座線".
                    # Let's add a helper or extend RAILWAY_EN_TO_JA in constants? 
                    # For now, let's look at METRO_TOEI_RAILWAY_INFO.
                    
                    found_ja = False
                    if display_name == railway_short: # Not found in JR map
                         for k, v in METRO_TOEI_RAILWAY_INFO.items():
                             if k.endswith(f".{railway_short}"):
                                 display_name = v["name_ja"]
                                 found_ja = True
                                 break
                    
                    reasons.append({
                        "id": railway_short,
                        "railway": display_name,
                        "rate": f"{stats['delayed']}/{stats['total']}件 ({rate_pct:.1f}%)",
                        "latest_reason": latest_reason,
                        "display": f"{display_name}: {rate_pct:.1f}%の遅延リスク"
                    })
                # Skip adding "normal" reasons to keep output clean
        
        # Check for current real-time delays
        current_delays_data = get_current_delays()
        current_delays = current_delays_data["delays"]
        current_delayed_railways = {d["railway_name_en"] for d in current_delays}
        
        has_current_delay = bool(railways_checked & current_delayed_railways)
        
        # Determine risk level based on probability
        # Priority: current delay > delay rate percentage
        if has_current_delay:
            level = "HIGH"
        elif max_delay_rate >= 5.0:  # 5%以上
            level = "HIGH"
        elif max_delay_rate >= 2.0:   # 2%以上
            level = "MEDIUM"
        else:
            level = "LOW"
        
        return {
            "score": round(max_delay_rate, 1),
            "level": level,
            "reasons": reasons
        }
        
    finally:
        db.close()


def get_railway_delay_history(railway_name: str, limit: int = 20) -> List[dict]:
    """
    Get historical delay records for a specific railway.
    
    Args:
        railway_name (str): Short name (e.g. "ChuoRapid") or full ID
        limit (int): Max records to return
    
    Returns:
        List[dict]: List of delay records
    """
    db = SessionLocal()
    try:
        # Normalize name if needed (simple check)
        # If passed "odpt.Railway:..." extract the short part common in our DB usage?
        # The DB stores `railway_name` as what we call normalized name (e.g. "ChuoRapid" or "Ginza") 
        # OR sometimes the full ID depending on how we imported.
        # Let's check `_get_railway_stats` logic:
        # simple_name = railway_name.split(".")[-1] if "." in railway_name else railway_name
        
        simple_name = railway_name.split(".")[-1] if "." in railway_name else railway_name
        
        query = select(TrainStatus).where(
            TrainStatus.railway_name == simple_name,
            TrainStatus.is_delayed == True
        ).order_by(TrainStatus.timestamp.desc()).limit(limit)
        
        records = db.execute(query).scalars().all()
        
        results = []
        for r in records:
            results.append({
                "timestamp": r.timestamp,
                "status": r.status,
                "status_text": r.status_text,
                "railway_name": r.railway_name
            })
            
        return results
    finally:
        db.close()


def _normalize_railway_name(railway: str) -> str:
    """
    Convert railway identifier to short English name.
    
    Examples:
        "中央線快速" -> "ChuoRapid"
        "odpt.Railway:JR-East.ChuoRapid" -> "ChuoRapid"
    """
    # Try Japanese to English mapping first
    if railway in RAILWAY_JA_TO_EN:
        return RAILWAY_JA_TO_EN[railway]
    
    # Extract from ODPT URI format
    if ":" in railway or "." in railway:
        # "odpt.Railway:JR-East.ChuoRapid" -> "ChuoRapid"
        parts = railway.replace("odpt.Railway:", "").split(".")
        return parts[-1] if parts else railway
    
    return railway


# Cache for railway stats (avoid repeated expensive queries)
_railway_stats_cache = {}
_railway_stats_cache_time = None
STATS_CACHE_TTL_SECONDS = 300  # Cache valid for 5 minutes (historical data doesn't change often)


def _get_railway_stats(db: Session, railway_name: str) -> dict:
    """
    Get delay statistics for a railway using SQL aggregation.
    Results are cached for STATS_CACHE_TTL_SECONDS.
    
    Returns:
        dict: {
            "total": int,  # Total number of observations
            "delayed": int,  # Number of delayed records
            "latest_reason": str
        }
    """
    global _railway_stats_cache, _railway_stats_cache_time
    
    # Check cache
    now = datetime.now()
    if _railway_stats_cache_time is not None:
        if (now - _railway_stats_cache_time).total_seconds() < STATS_CACHE_TTL_SECONDS:
            if railway_name in _railway_stats_cache:
                return _railway_stats_cache[railway_name]
    else:
        # Reset cache if expired
        _railway_stats_cache = {}
        _railway_stats_cache_time = now
    
    # Handle full ID (odpt.Railway:JR-East.Tokaido) -> Tokaido
    simple_name = railway_name.split(".")[-1] if "." in railway_name else railway_name
    
    # Use SQL aggregation instead of fetching all records
    # Count total records
    total_query = select(func.count()).select_from(TrainStatus).where(
        TrainStatus.railway_name == simple_name
    )
    total_count = db.execute(total_query).scalar() or 0
    
    if total_count == 0:
        result = {"total": 0, "delayed": 0, "latest_reason": ""}
        _railway_stats_cache[railway_name] = result
        return result
    
    # Count delayed records
    delayed_query = select(func.count()).select_from(TrainStatus).where(
        TrainStatus.railway_name == simple_name,
        TrainStatus.is_delayed == True
    )
    delayed_count = db.execute(delayed_query).scalar() or 0
    
    # Get latest reason (only if there are delays)
    latest_reason = ""
    if delayed_count > 0:
        reason_query = select(TrainStatus.status_text).where(
            TrainStatus.railway_name == simple_name,
            TrainStatus.is_delayed == True
        ).order_by(TrainStatus.timestamp.desc()).limit(1)
        latest_reason = db.execute(reason_query).scalar() or ""
    
    result = {
        "total": total_count,
        "delayed": delayed_count,
        "latest_reason": latest_reason
    }
    
    # Save to cache
    _railway_stats_cache[railway_name] = result
    _railway_stats_cache_time = now
    
    return result


def get_current_delays() -> dict:
    """
    Get list of currently delayed railways based on most recent data.
    Results are cached for CACHE_TTL_SECONDS to improve performance.
    
    Returns:
        dict: {
            "updated_at": str (ISO timestamp),
            "delays": List[dict]
        }
    """
    global _current_delays_cache, _current_delays_cache_time
    
    # Check cache
    now = datetime.now()
    if _current_delays_cache is not None and _current_delays_cache_time is not None:
        if (now - _current_delays_cache_time).total_seconds() < CACHE_TTL_SECONDS:
            return _current_delays_cache
    
    db = SessionLocal()
    
    try:
        # Get most recent timestamp efficiently
        # Optimizing: func.max() can be slow on large tables if not optimized by DB.
        # ORDER BY timestamp DESC LIMIT 1 is often faster with an index.
        latest_query = select(TrainStatus.timestamp).order_by(TrainStatus.timestamp.desc()).limit(1)
        latest_ts = db.execute(latest_query).scalar()
        
        if not latest_ts:
            return {"updated_at": None, "delays": []}
        
        # Get all delayed records from latest fetch
        query = select(TrainStatus).where(
            TrainStatus.timestamp == latest_ts,
            TrainStatus.is_delayed == True
        )
        
        records = db.execute(query).scalars().all()
        
        # Import mappings and major railways list
        from .constants import RAILWAY_EN_TO_JA, METRO_TOEI_RAILWAY_INFO, ALL_RAILWAYS
        
        results = []
        for r in records:
            # Filter for major railways only
            if r.railway_id not in ALL_RAILWAYS:
                continue

            # Determine Japanese name
            # 1. Try EN -> JA map (for JR)
            ja_name = RAILWAY_EN_TO_JA.get(r.railway_name, r.railway_name)
            
            # 2. If it is full ID (Metro/Toei), try that map
            if r.railway_id in METRO_TOEI_RAILWAY_INFO:
                ja_name = METRO_TOEI_RAILWAY_INFO[r.railway_id]["name_ja"]
            
            results.append({
                "railway_id": r.railway_id,
                "railway_name": ja_name, # Return JA name as primary name for display
                "railway_name_en": r.railway_name,
                "operator": r.operator,
                "status": r.status,
                "status_text": r.status_text,
                "timestamp": r.timestamp
            })
        
        # Save to cache
        result = {"updated_at": latest_ts, "delays": results}
        _current_delays_cache = result
        _current_delays_cache_time = datetime.now()
        
        return result
        
    finally:
        db.close()
