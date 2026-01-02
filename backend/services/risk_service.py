from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import select, and_, exists
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import DelayLog
from .constants import RAILWAY_JA_TO_EN

def is_delay_in_range(db: Session, route_id: str, target_hour: int) -> bool:
    """
    Check if there are any delay logs for the route within target_hour +/- 1.
    """
    # Simple hours matching. We check for logs where ISO timestamp hour matches.
    # Note: Storing timestamp as String in ISO format makes this slightly inefficient for hour extraction in SQL.
    # However, for simplicity as requested:
    # We will fetch potentially relevant records or use Python logic if dataset is small, 
    # OR we rely on SQLite's strftime if available. 
    # Let's try to use partial string match or range if possible, but given the format "YYYY-MM-DDTHH:MM:SS..."
    # we can construct a query.
    # Actually, simpler approach for SQLite:
    # Get all records for the route (assuming not huge) or iterate.
    # BETTER: Use SQLite's strftime('%H', timestamp)
    
    # Target hours: (h-1), h, (h+1) handling 24h wrap-around
    hours_to_check = set([
        (target_hour - 1) % 24,
        target_hour,
        (target_hour + 1) % 24
    ])
    
    # Create formatted strings for Like query might be hard due to date part.
    # Let's use SQLite function
    query = select(DelayLog).where(
        and_(
            DelayLog.route_id == route_id,
            DelayLog.max_delay > 0
        )
    )
    
    # Execute and filter in python for safety/portability with current simple schema
    # (Since we imported ~15000 records, fetching all for a route is cheap enough)
    logs = db.execute(query).scalars().all()
    
    for log in logs:
        try:
            dt = datetime.fromisoformat(log.timestamp)
            if dt.hour in hours_to_check:
                return True
        except ValueError:
            continue
            
    return False




from .constants import RAILWAY_JA_TO_EN, RAILWAY_TO_ROUTE_CODE

def get_route_risk(route: dict, departure_time: str) -> dict:
    """
    Calculate risk score based on real DB data, using trip_id suffix matching for specific lines.
    """
    try:
        dt = datetime.fromisoformat(departure_time)
        target_hour = dt.hour
    except:
        target_hour = datetime.now().hour

    db = SessionLocal()
    total_risk = 0
    max_level = 0
    reasons = []

    try:
        hours_to_check = set([
            (target_hour - 1) % 24,
            target_hour,
            (target_hour + 1) % 24
        ])
        
        railways_checked = set()
        segments = route.get("segments", [])
        
        for segment in segments:
            railway = segment.get("railway")
            if not railway:
                continue

            # Normalize to English short code (e.g., "ChuoRapid")
            railway_short = railway
            if railway in RAILWAY_JA_TO_EN:
                railway_short = RAILWAY_JA_TO_EN[railway]
            elif ":" in railway:
                 railway_short = railway.split(".")[-1].split(":")[-1]
            
            if railway_short in railways_checked:
                continue
            railways_checked.add(railway_short)

            # Get route code suffix (e.g., "T" for ChuoRapid)
            suffix = RAILWAY_TO_ROUTE_CODE.get(railway_short)
            
            if not suffix:
                # If we can't identify the line suffix, skip specific check
                continue

            # Fetch records for this specific line (trip_id ends with suffix)
            query = select(DelayLog).where(
                and_(
                     DelayLog.trip_id.like(f"%{suffix}"),
                     DelayLog.max_delay > 0
                )
            )
            logs = db.execute(query).scalars().all()
            
            line_delay_count = 0
            line_details = []
            
            for log in logs:
                try:
                    log_dt = datetime.fromisoformat(log.timestamp)
                    if log_dt.hour in hours_to_check:
                        line_delay_count += 1
                        line_details.append({
                            "timestamp": log_dt.strftime("%H:%M:%S"), # Just time part
                            "delay_min": log.max_delay // 60
                        })
                except:
                    continue
            
            if line_delay_count > 0:
                total_risk += line_delay_count
                max_level = max(max_level, 2)
                
                # Sort by time
                line_details.sort(key=lambda x: x["timestamp"])
                
                # Format specific details
                detail_strs = [f"{d['timestamp']} (約{d['delay_min']}分)" for d in line_details[:3]] # Limit to 3 samples
                if len(line_details) > 3:
                     detail_strs.append("...")
                     
                reasons.append(f"{railway_short}: {line_delay_count}件の遅延実績 [{', '.join(detail_strs)}]")
                
                # Also store raw details if needed by frontend (requires schema change? 
                # or just packing into extra field. Let's keep 'reasons' as string for now for compatibility, 
                # but maybe add 'delay_events' list)
                
        level = "LOW"
        if max_level > 0:
            level = "HIGH"
            
        return {
            "score": total_risk,
            "level": level,
            "reasons": reasons
        }
        level = "LOW"
        if max_level > 0:
            level = "HIGH"
            
        return {
            "score": total_risk,
            "level": level,
            "reasons": reasons
        }
        
    finally:
        db.close()

