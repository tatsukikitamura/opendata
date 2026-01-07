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
