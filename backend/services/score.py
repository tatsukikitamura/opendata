
def calculate_route_scores(route: dict, all_routes: list) -> dict:
    """
    Calculate 3-axis scores for a route relative to other candidates.
    
    Axes:
    1. Speed (Fast): Relative to the fastest route in the set.
    2. Comfort (Easy): Inverse of crowd metrics.
    3. Reliability (Safe): Inverse of delay risk.
    
    Returns:
        dict: {
            "speed": float (0.0 - 5.0),
            "comfort": float (0.0 - 5.0),
            "reliability": float (0.0 - 5.0)
        }
    """
    scores = {
        "speed": 0.0,
        "comfort": 0.0,
        "reliability": 0.0
    }
    
    # 1. Speed Score
    # Relative to the minimum time in the candidate set
    times = []
    for r in all_routes:
        # Use total_time (theoretical) or actual difference if available
        # search.py adds 'theoretical_time' to segments, checking route level validity
        # search_route_with_times returns total_time in minutes usually
        t = r.get("total_time", 0)
        # If not at root, try summing segments? search_route_with_times usually puts total_time
        if not t and "segments" in r:
             # Calculate from arrival - departure if possible
             try:
                 fmt = "%H:%M"
                 dep = r["segments"][0]["departure_time"]
                 arr = r["segments"][-1]["arrival_time"]
                 
                 def p(s):
                     h, m = map(int, s.split(":"))
                     return h * 60 + m
                     
                 diff = p(arr) - p(dep)
                 if diff < 0: diff += 24 * 60
                 t = diff
             except:
                 t = 999
        
        if t > 0:
            times.append(t)
            
    if times:
        min_time = min(times)
        my_time = route.get("total_time", 0)
        
        # Fallback calculation if key missing
        if not my_time and "segments" in route:
             try:
                 dep = route["segments"][0]["departure_time"]
                 arr = route["segments"][-1]["arrival_time"]
                 def p(s): return int(s.split(":")[0])*60 + int(s.split(":")[1])
                 diff = p(arr) - p(dep)
                 if diff < 0: diff += 24 * 60
                 my_time = diff
             except:
                 my_time = 999

        if my_time > 0:
            # Score = 5.0 * (min / my)
            # Example: min=30, my=30 -> 5.0
            # Example: min=30, my=60 -> 2.5
            scores["speed"] = round(min(5.0, 5.0 * (min_time / my_time)), 1)
        else:
            scores["speed"] = 0.0
    else:
        scores["speed"] = 0.0

    # 2. Comfort Score
    # Based on crowd.score (average daily volume)
    # 0 -> 5.0
    # 200,000 -> 1.0 (Very crowded)
    crowd = route.get("crowd", {})
    volume = crowd.get("score", 0)
    
    # Linear scaling: 5.0 - (volume / 50000)
    # 50k -> 4.0
    # 100k -> 3.0
    # 200k -> 1.0
    comfort = 5.0 - (volume / 50000.0)
    scores["comfort"] = round(max(1.0, min(5.0, comfort)), 1)
    
    # 3. Reliability Score
    # Based on risk.score (number of delayed trains/incidents)
    # 0 -> 5.0
    # 1 -> 4.0
    # 5 -> 0.0
    risk = route.get("risk", {})
    risk_score = risk.get("score", 0) # This is a count of delay events
    
    reliability = 5.0 - (risk_score * 1.0)
    scores["reliability"] = round(max(1.0, min(5.0, reliability)), 1)
    
    return scores
