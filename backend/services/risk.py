"""
Risk Service - Calculate delay risk for routes based on historical train status data.

Uses TrainStatus records from odpt:TrainInformation API to calculate
the probability of delays for each railway line.
"""
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import TrainStatus
from .constants import RAILWAY_JA_TO_EN, RAILWAY_EN_TO_JA, METRO_TOEI_RAILWAY_INFO


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
                        "railway": display_name,
                        "rate": f"{stats['delayed']}/{stats['total']}件 ({rate_pct:.1f}%)",
                        "latest_reason": latest_reason,
                        "display": f"{display_name}: {rate_pct:.1f}%の遅延リスク"
                    })
                # Skip adding "normal" reasons to keep output clean
        
        # Check for current real-time delays
        current_delays_data = get_current_delays()
        current_delays = current_delays_data["delays"]
        current_delayed_railways = {d["railway_name"] for d in current_delays}
        
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


def _get_railway_stats(db: Session, railway_name: str) -> dict:
    """
    Get delay statistics for a railway.
    Groups continuous delay records into single events to avoid over-counting.
    
    Returns:
        dict: {
            "total_checks": int,  # Total number of observations
            "delay_events": int,  # Number of distinct delay events
            "latest_reason": str
        }
    """
    # Query matching railway_name
    # Handle full ID (odpt.Railway:JR-East.Tokaido) -> Tokaido
    simple_name = railway_name.split(".")[-1] if "." in railway_name else railway_name
    
    query = select(TrainStatus).where(
        TrainStatus.railway_name == simple_name
    ).order_by(TrainStatus.timestamp)
    
    records = db.execute(query).scalars().all()
    
    total_checks = len(records)
    if total_checks == 0:
        return {"total": 0, "delayed": 0, "latest_reason": ""}

    # Calculate distinct delay events
    delay_events = 0
    last_delay_time = None
    latest_reason = ""
    
    # Threshold to consider as same event (e.g., 60 minutes)
    SAME_EVENT_THRESHOLD_MIN = 60
    
    from datetime import datetime, timedelta
    
    delayed_records = [r for r in records if r.is_delayed]
    
    for r in delayed_records:
        # Update latest reason
        if r.status_text:
            latest_reason = r.status_text
            
        try:
            # Parse timestamp (ISO format)
            # Handle potential Z suffix or offset
            ts_str = r.timestamp.replace("Z", "+00:00")
            current_time = datetime.fromisoformat(ts_str)
            
            if last_delay_time is None:
                # First delay found
                delay_events += 1
                last_delay_time = current_time
            else:
                # Check time difference
                diff = current_time - last_delay_time
                if diff.total_seconds() / 60 > SAME_EVENT_THRESHOLD_MIN:
                    # New event
                    delay_events += 1
                    last_delay_time = current_time
                else:
                    # Continuation of same event, just update time
                    last_delay_time = current_time
                    
        except ValueError:
            continue
            
    return {
        "total": total_checks,
        "delayed": delay_events,
        "latest_reason": latest_reason
    }


def get_current_delays() -> dict:
    """
    Get list of currently delayed railways based on most recent data.
    
    Returns:
        dict: {
            "updated_at": str (ISO timestamp),
            "delays": List[dict]
        }
    """
    db = SessionLocal()
    
    try:
        # Get most recent timestamp
        latest_query = select(func.max(TrainStatus.timestamp))
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
            
        return {"updated_at": latest_ts, "delays": results}
        
    finally:
        db.close()
