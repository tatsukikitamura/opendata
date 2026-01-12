"""
AI-related Pydantic models for request/response validation.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class RouteSegment(BaseModel):
    """A single segment of a route."""
    railway: Optional[str] = None
    from_station: Optional[str] = None
    to_station: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None


class DiagnosisRequest(BaseModel):
    """Request body for AI delay risk diagnosis."""
    segments: List[Dict[str, Any]]
    risk: Optional[Dict[str, Any]] = None
    crowd: Optional[Dict[str, Any]] = None
    venue_warnings: Optional[Dict[str, Any]] = None
    delay_warnings: Optional[List[Dict[str, Any]]] = None


class DiagnosisResponse(BaseModel):
    """Response from AI delay risk diagnosis."""
    diagnosis: str
    model: str = "gpt-4o-mini"
