"""
Payment Repository
Handles user payment status and premium tracking
"""

from loguru import logger
from services.db_service import get_db_pool
from models.payment import UserPlannerStatus
from datetime import datetime, timezone


async def get_user_planner_status(user_id: str) -> UserPlannerStatus:
    """
    Get user's planner status (free usage, premium status, etc.)
    
    Args:
        user_id: User ID
        
    Returns:
        UserPlannerStatus with user's current status
    """
    pool = get_db_pool()
    
    async with pool.acquire() as conn:
        # Check if user exists in user_planner_status table
        row = await conn.fetchrow(
            """
            SELECT user_id, has_used_free_planner, total_planners_created, is_premium
            FROM user_planner_status
            WHERE user_id = $1
            """,
            user_id,
        )
        
        if row:
            return UserPlannerStatus(
                user_id=row["user_id"],
                has_used_free_planner=row["has_used_free_planner"],
                total_planners_created=row["total_planners_created"],
                is_premium=row["is_premium"],
            )
        else:
            # Create new user status entry
            await conn.execute(
                """
                INSERT INTO user_planner_status 
                (user_id, has_used_free_planner, total_planners_created, is_premium, created_at)
                VALUES ($1, $2, $3, $4, $5)
                """,
                user_id,
                False,
                0,
                False,
                datetime.now(timezone.utc),
            )
            
            return UserPlannerStatus(
                user_id=user_id,
                has_used_free_planner=False,
                total_planners_created=0,
                is_premium=False,
            )


async def update_user_premium_status(user_id: str, is_premium: bool) -> None:
    """
    Update user's premium status
    
    Args:
        user_id: User ID
        is_premium: Premium status to set
    """
    pool = get_db_pool()
    
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO user_planner_status 
            (user_id, has_used_free_planner, total_planners_created, is_premium, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                is_premium = $4,
                updated_at = $6
            """,
            user_id,
            False,
            0,
            is_premium,
            datetime.now(timezone.utc),
            datetime.now(timezone.utc),
        )
    
    logger.info(f"Updated premium status for user {user_id} to {is_premium}")


async def increment_planner_count(user_id: str) -> None:
    """
    Increment user's planner creation count and mark free planner as used
    
    Args:
        user_id: User ID
    """
    pool = get_db_pool()
    
    async with pool.acquire() as conn:
        # Get current status
        status = await get_user_planner_status(user_id)
        
        # Update count and free planner status
        await conn.execute(
            """
            UPDATE user_planner_status 
            SET 
                total_planners_created = total_planners_created + 1,
                has_used_free_planner = true,
                updated_at = $2
            WHERE user_id = $1
            """,
            user_id,
            datetime.now(timezone.utc),
        )
    
    logger.info(f"Incremented planner count for user {user_id}")
