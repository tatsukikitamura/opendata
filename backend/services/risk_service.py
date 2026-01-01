from datetime import datetime
from typing import Dict, List, Optional
from .constants import RAILWAY_JA_TO_EN

# Mock historical data: "RailwayName": { "Hour": RiskLevel }
# 0: Low, 1: Medium, 2: High
# Keys are short names (e.g., ChuoRapid) to match regardless of prefix
MOCK_RISK_DB = {
    "ChuoRapid": {
        # Morning rush
        7: 2, 8: 2, 9: 1,
        # Evening rush
        18: 1, 19: 2, 20: 1,
        # Late night
        23: 1
    },
    "SobuRapid": {
        8: 1, 9: 1, 19: 1
    },
    "Tokaido": {
        8: 2, 19: 1
    }
}

def get_route_risk(route: dict, departure_time: str) -> dict:
    """
    Calculate risk score for a route.
    Returns: { "score": int, "level": str, "reasons": List[str] }
    """
    try:
        dt = datetime.fromisoformat(departure_time)
        hour = dt.hour
    except:
        hour = 8 # Default to morning if parsing fails

    total_risk = 0
    max_risk_level = 0
    reasons = []

    # Analyze each segment
    railways_checked = set()
    
    segments = route.get("segments", [])
    for segment in segments:
        railway = segment.get("railway")
        if not railway:
            continue
            
        # Normalize to English short code
        railway_short = railway
        
        # 1. Check if it's Japanese name
        if railway in RAILWAY_JA_TO_EN:
            railway_short = RAILWAY_JA_TO_EN[railway]
        # 2. Check if it's full URI (odpt.Railway:...)
        elif ":" in railway:
             railway_short = railway.split(".")[-1].split(":")[-1]
            
        if railway_short in railways_checked:
            continue
            
        railways_checked.add(railway_short)
        
        # Check mock DB
        risk_map = MOCK_RISK_DB.get(railway_short, {})
        risk = risk_map.get(hour, 0)
        
        if risk > 0:
            total_risk += risk
            max_risk_level = max(max_risk_level, risk)
            
            level_str = "中" if risk == 1 else "高"
            reasons.append(f"{railway_short}線は{hour}時台に遅延傾向({level_str})")

    risk_level = "LOW"
    if max_risk_level == 2 or total_risk >= 3:
        risk_level = "HIGH"
    elif max_risk_level == 1 or total_risk >= 1:
        risk_level = "MEDIUM"

    return {
        "score": total_risk,
        "level": risk_level,
        "reasons": reasons
    }
