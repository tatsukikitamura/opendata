
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
    # Hybrid Approach:
    # - Base: Absolute score based on volume (50000 -> 5.0, 250000 -> 1.0)
    # - If candidates >= 3: Calculate T-score (Deviation) and blend with Base
    
    # 2a. Calculate Base Absolute Score for all routes first
    base_comfort_scores = []
    
    for r in all_routes:
        crowd = r.get("crowd", {})
        volume = crowd.get("score", 0)
        
        # Absolute Logic
        # 0 - 50,000 -> 5.0 (Very Good)
        # 250,000 -> 1.0 (Very Bad)
        # Linear scaling
        if volume <= 50000:
            base_score = 5.0
        else:
            # Scale 50k - 250k to 5.0 - 1.0
            # 5.0 - ((vol - 50000) / 200000 * 4.0)
            base_score = 5.0 - ((volume - 50000) / 200000.0 * 4.0)
            
        base_comfort_scores.append(max(1.0, min(5.0, base_score)))

    # Find my index
    my_index = 0
    try:
        # Assuming all_routes is the same list object passed in, 
        # but to be safe, find by identity or some unique property if possible.
        # For now, simplistic approach: match by route object identity if possible,
        # or just re-calculate my specific base score.
        my_crowd = route.get("crowd", {})
        my_volume = my_crowd.get("score", 0)
        
        if my_volume <= 50000:
            my_base_score = 5.0
        else:
            my_base_score = 5.0 - ((my_volume - 50000) / 200000.0 * 4.0)
        my_base_score = max(1.0, min(5.0, my_base_score))
        
    except:
        my_base_score = 3.0 # Fallback

    # 2b. Apply Hybrid Logic
    if len(base_comfort_scores) >= 3:
        # Calculate Deviation (T-score)
        import statistics
        try:
            mean = statistics.mean(base_comfort_scores)
            stdev = statistics.stdev(base_comfort_scores)
            
            if stdev > 0:
                # T-score = 50 + 10 * (X - Mean) / SD
                # We want higher score = better
                t_score = 50 + 10 * (my_base_score - mean) / stdev
                
                # Map T-score to 1.0 - 5.0
                # T=50 (Mean) -> 3.0
                rel_score = 3.0 + (t_score - 50) / 10.0
                rel_score = max(1.0, min(5.0, rel_score))
                
                # Use Pure Relative Score as requested (Average = 3)
                scores["comfort"] = round(rel_score, 1)
            else:
                # All scores identical -> Average is 3.0
                scores["comfort"] = 3.0
        except:
             scores["comfort"] = 3.0
    else:
        # Few candidates, trust absolute score
        scores["comfort"] = round(my_base_score, 1)
    
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
