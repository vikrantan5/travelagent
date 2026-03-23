"""
Trip History Repository
Database operations for trip history
"""

from models.trip_history import TripHistory, TripHistoryCreate
from services.db_service import get_db_pool
from loguru import logger
from datetime import datetime
import uuid
from typing import List, Optional


async def create_trip_history(trip_data: TripHistoryCreate) -> TripHistory:
    """Create a new trip history entry"""
    pool = get_db_pool()
    
    trip_id = str(uuid.uuid4())
    created_at = datetime.utcnow()
    
    query = """
        INSERT INTO trip_history 
        (id, destination, start_date, end_date, duration, budget, budget_currency, travelers, trip_plan_id, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING id, destination, start_date, end_date, duration, budget, budget_currency, travelers, trip_plan_id, created_at
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            query,
            trip_id,
            trip_data.destination,
            trip_data.start_date,
            trip_data.end_date,
            trip_data.duration,
            trip_data.budget,
            trip_data.budget_currency,
            trip_data.travelers,
            trip_data.trip_plan_id,
            created_at
        )
        
        logger.info(f"Created trip history: {trip_id}")
        
        return TripHistory(
            id=row['id'],
            destination=row['destination'],
            start_date=row['start_date'],
            end_date=row['end_date'],
            duration=row['duration'],
            budget=row['budget'],
            budget_currency=row['budget_currency'],
            travelers=row['travelers'],
            trip_plan_id=row['trip_plan_id'],
            created_at=row['created_at']
        )


async def get_all_trip_history(limit: int = 50) -> List[TripHistory]:
    """Get all trip history entries"""
    pool = get_db_pool()
    
    query = """
        SELECT id, destination, start_date, end_date, duration, budget, budget_currency, travelers, trip_plan_id, created_at
        FROM trip_history
        ORDER BY created_at DESC
        LIMIT $1
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, limit)
        
        return [
            TripHistory(
                id=row['id'],
                destination=row['destination'],
                start_date=row['start_date'],
                end_date=row['end_date'],
                duration=row['duration'],
                budget=row['budget'],
                budget_currency=row['budget_currency'],
                travelers=row['travelers'],
                trip_plan_id=row['trip_plan_id'],
                created_at=row['created_at']
            )
            for row in rows
        ]


async def get_trip_history_by_id(trip_id: str) -> Optional[TripHistory]:
    """Get a specific trip history entry by ID"""
    pool = get_db_pool()
    
    query = """
        SELECT id, destination, start_date, end_date, duration, budget, budget_currency, travelers, trip_plan_id, created_at
        FROM trip_history
        WHERE id = $1
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, trip_id)
        
        if not row:
            return None
        
        return TripHistory(
            id=row['id'],
            destination=row['destination'],
            start_date=row['start_date'],
            end_date=row['end_date'],
            duration=row['duration'],
            budget=row['budget'],
            budget_currency=row['budget_currency'],
            travelers=row['travelers'],
            trip_plan_id=row['trip_plan_id'],
            created_at=row['created_at']
        )


async def delete_trip_history(trip_id: str) -> bool:
    """Delete a trip history entry"""
    pool = get_db_pool()
    
    query = "DELETE FROM trip_history WHERE id = $1"
    
    async with pool.acquire() as conn:
        result = await conn.execute(query, trip_id)
        logger.info(f"Deleted trip history: {trip_id}")
        return True
