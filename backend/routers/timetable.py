
"""
Timetable API router.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import StationDeparture
from typing import List, Optional

router = APIRouter()


@router.get("/departures")
def get_departures(
    station: Optional[str] = Query(None, description="Station name (e.g., Tokyo)"),
    railway: Optional[str] = Query(None, description="Railway name (e.g., ChuoRapid)"),
    time: Optional[str] = Query(None, description="Time after (HH:MM)"),
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get station departures from database.
    This is useful for debugging timetable data.
    """
    query = db.query(StationDeparture)
    
    if station:
        query = query.filter(StationDeparture.station_name.ilike(f"%{station}%"))
    if railway:
        query = query.filter(StationDeparture.railway_name.ilike(f"%{railway}%"))
    if time:
        query = query.filter(StationDeparture.departure_time >= time)
        
    departures = query.order_by(StationDeparture.departure_time).limit(limit).all()
    
    return [
        {
            "time": d.departure_time,
            "station": d.station_name,
            "railway": d.railway_name,
            "type": d.train_type,
            "destination": d.destination_station,
            "train_number": d.train_number,
            "direction": d.direction
        }
        for d in departures
    ]
