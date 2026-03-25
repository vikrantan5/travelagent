#!/usr/bin/env python3
"""
Migration script to fix the error_message column size in plan_tasks table.
This increases the VARCHAR limit from 500 to 2000 characters.

Run this script after deploying the code changes to update the database schema.
"""

import asyncio
import os
from loguru import logger
from sqlalchemy import text
from services.db_service import initialize_db_pool, get_db_session, close_db_pool


async def run_migration():
    """Run the database migration to increase error_message column size."""
    
    logger.info("Starting migration: Increasing error_message column size")
    
    try:
        # Initialize database connection
        await initialize_db_pool()
        logger.info("Database connection initialized")
        
        # SQL to alter the column
        alter_sql = """
        ALTER TABLE plan_tasks 
        ALTER COLUMN error_message TYPE VARCHAR(2000);
        """
        
        async with get_db_session() as session:
            logger.info("Executing ALTER TABLE statement...")
            await session.execute(text(alter_sql))
            await session.commit()
            logger.info("✅ Migration completed successfully!")
            logger.info("error_message column size increased from VARCHAR(500) to VARCHAR(2000)")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise
    finally:
        await close_db_pool()
        logger.info("Database connection closed")


if __name__ == "__main__":
    asyncio.run(run_migration())
