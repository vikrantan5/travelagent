"""
Trip History Repository
Database operations for trip history
"""

from models.trip_history import TripHistory, TripHistoryCreate
from services.db_service import get_db_session
from loguru import logger
from datetime import datetime
import uuid
from typing import List, Optional
from sqlalchemy import text


async def create_trip_history(trip_data: TripHistoryCreate) -> TripHistory:
    """Create a new trip history entry"""
    trip_id = str(uuid.uuid4())
    created_at = datetime.utcnow()
    
    query = """
        INSERT INTO trip_history 
        (id, destination, start_date, end_date, duration, budget, budget_currency, travelers, trip_plan_id, created_at)
        VALUES (:id, :destination, :start_date, :end_date, :duration, :budget, :budget_currency, :travelers, :trip_plan_id, :created_at)
        RETURNING id, destination, start_date, end_date, duration, budget, budget_currency, travelers, trip_plan_id, created_at
    """
    
    async with get_db_session() as session:
        result = await session.execute(
            text(query),
            {
                "id": trip_id,
                "destination": trip_data.destination,
                "start_date": trip_data.start_date,
                "end_date": trip_data.end_date,
                "duration": trip_data.duration,
                "budget": trip_data.budget,
                "budget_currency": trip_data.budget_currency,
                "travelers": trip_data.travelers,
                "trip_plan_id": trip_data.trip_plan_id,
                "created_at": created_at
            }
        )
        await session.commit()
        row = result.fetchone()
        
        logger.info(f"Created trip history: {trip_id}")
        
        return TripHistory(
            id=row[0],
            destination=row[1],
            start_date=row[2],
            end_date=row[3],
            duration=row[4],
            budget=row[5],
            budget_currency=row[6],
            travelers=row[7],
            trip_plan_id=row[8],
            created_at=row[9]
        )




async def get_all_trip_history(limit: int = 50) -> List[TripHistory]:
    """Get all trip history entries"""
    query = """
        SELECT id, destination, start_date, end_date, duration, budget, budget_currency, travelers, trip_plan_id, created_at
        FROM trip_history
        ORDER BY created_at DESC
        LIMIT :limit
    """
    
    async with get_db_session() as session:
        result = await session.execute(text(query), {"limit": limit})
        rows = result.fetchall()
        
        return [
            TripHistory(
                id=row[0],
                destination=row[1],
                start_date=row[2],
                end_date=row[3],
                duration=row[4],
                budget=row[5],
                budget_currency=row[6],
                travelers=row[7],
                trip_plan_id=row[8],
                created_at=row[9]
            )
            for row in rows
        ]


async def get_trip_history_by_id(trip_id: str) -> Optional[TripHistory]:
    """Get a specific trip history entry by ID"""
    query = """
        SELECT id, destination, start_date, end_date, duration, budget, budget_currency, travelers, trip_plan_id, created_at
        FROM trip_history
        WHERE id = :trip_id
    """
    
    async with get_db_session() as session:
        result = await session.execute(text(query), {"trip_id": trip_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        return TripHistory(
            id=row[0],
            destination=row[1],
            start_date=row[2],
            end_date=row[3],
            duration=row[4],
            budget=row[5],
            budget_currency=row[6],
            travelers=row[7],
            trip_plan_id=row[8],
            created_at=row[9]
        )


async def delete_trip_history(trip_id: str) -> bool:
    """Delete a trip history entry"""
    query = "DELETE FROM trip_history WHERE id = :trip_id"
    
    async with get_db_session() as session:
        await session.execute(text(query), {"trip_id": trip_id})
        await session.commit()
        logger.info(f"Deleted trip history: {trip_id}")
        return True
