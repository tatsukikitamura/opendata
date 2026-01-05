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
from .constants import RAILWAY_JA_TO_EN


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
    total_risk = 0
    max_level = 0
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
                if stats["delayed"] > 0:
                    total_risk += stats["delayed"]
                    max_level = max(max_level, 2)
                    
                    rate_pct = (stats["delayed"] / stats["total"]) * 100
                    
                    # Get latest delay reason
                    latest_reason = stats.get("latest_reason", "")
                    reason_preview = latest_reason[:50] + "..." if len(latest_reason) > 50 else latest_reason
                    
                    reasons.append({
                        "railway": railway_short,
                        "rate": f"{stats['delayed']}/{stats['total']}件 ({rate_pct:.1f}%)",
                        "latest_reason": latest_reason,
                        "display": f"{railway_short}: {rate_pct:.1f}%の遅延リスク"
                    })
                # Skip adding "normal" reasons to keep output clean
        
        # Determine risk level
        if total_risk >= 5:
            level = "HIGH"
        elif total_risk >= 2:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        return {
            "score": total_risk,
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
    
    Returns:
        dict: {
            "total": int (total records),
            "delayed": int (delayed records),
            "latest_reason": str (most recent delay reason)
        }
    """
    # Query matching railway_name
    # Match both exact name and partial (e.g., "ChuoRapid" matches "JR-East.ChuoRapid")
    query = select(TrainStatus).where(
        TrainStatus.railway_name == railway_name
    )
    
    records = db.execute(query).scalars().all()
    
    total = len(records)
    delayed = sum(1 for r in records if r.is_delayed)
    
    # Get latest delay reason
    latest_reason = ""
    delayed_records = [r for r in records if r.is_delayed]
    if delayed_records:
        # Sort by timestamp descending
        delayed_records.sort(key=lambda r: r.timestamp or "", reverse=True)
        latest_reason = delayed_records[0].status_text or ""
    
    return {
        "total": total,
        "delayed": delayed,
        "latest_reason": latest_reason
    }


def get_current_delays() -> List[dict]:
    """
    Get list of currently delayed railways based on most recent data.
    
    Returns:
        List of dicts with railway info and delay reasons.
    """
    db = SessionLocal()
    
    try:
        # Get most recent timestamp
        latest_query = select(func.max(TrainStatus.timestamp))
        latest_ts = db.execute(latest_query).scalar()
        
        if not latest_ts:
            return []
        
        # Get all delayed records from latest fetch
        query = select(TrainStatus).where(
            TrainStatus.timestamp == latest_ts,
            TrainStatus.is_delayed == True
        )
        
        records = db.execute(query).scalars().all()
        
        return [
            {
                "railway_id": r.railway_id,
                "railway_name": r.railway_name,
                "operator": r.operator,
                "status": r.status,
                "status_text": r.status_text
            }
            for r in records
        ]
        
    finally:
        db.close()
