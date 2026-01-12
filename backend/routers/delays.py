from fastapi import APIRouter, Depends
from typing import List
from services.risk import get_current_delays

router = APIRouter(
    prefix="/api/delays",
    tags=["Delays"]
)

@router.get("/current")
def get_current_delays_endpoint():
    """
    Get list of currently delayed railways.
    """
    return get_current_delays()


@router.get("/history")
def get_delay_history_endpoint(railway: str, limit: int = 20):
    """
    Get historical delay records for a specific railway.
    
    Args:
        railway (str): Railway short name or ID
        limit (int): Max records (default 20)
    """
    from services.risk import get_railway_delay_history
    return get_railway_delay_history(railway, limit)
