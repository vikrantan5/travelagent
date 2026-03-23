"""
Trip History Database Model
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid


class TripHistory(BaseModel):
    """Trip history model for storing past trips"""
    id: str
    destination: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: int
    budget: Optional[float] = None
    budget_currency: Optional[str] = "USD"
    travelers: int = 1
    trip_plan_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TripHistoryCreate(BaseModel):
    """Model for creating trip history entry"""
    destination: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: int
    budget: Optional[float] = None
    budget_currency: Optional[str] = "USD"
    travelers: int = 1
    trip_plan_id: str


class TripHistoryResponse(BaseModel):
    """Response model for trip history"""
    id: str
    destination: str
    start_date: Optional[str]
    end_date: Optional[str]
    duration: int
    budget: Optional[float]
    budget_currency: str
    travelers: int
    trip_plan_id: str
    created_at: str
    has_plan: bool = False
