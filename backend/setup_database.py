#!/usr/bin/env python3
"""
Database Setup Script for TripCraft AI
Run this script to set up all required database tables
"""

import asyncio
import asyncpg
import os
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Load environment variables    
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def run_migration(conn, migration_file: Path):
    """Run a single migration file"""
    try:
        logger.info(f"Running migration: {migration_file.name}")
        sql = migration_file.read_text()
        await conn.execute(sql)
        logger.info(f"✅ Migration completed: {migration_file.name}")
        return True
    except Exception as e:
        logger.error(f"❌ Migration failed ({migration_file.name}): {str(e)}")
        return False

async def setup_database():
    """Set up all database tables"""
    if not DATABASE_URL:
        logger.error("DATABASE_URL not found in environment variables")
        return False
    
    try:
        logger.info("Connecting to database...")
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("✅ Connected to database")
        
        # Get migrations directory
        migrations_dir = Path(__file__).parent / "migrations"
        
        if not migrations_dir.exists():
            logger.error(f"Migrations directory not found: {migrations_dir}")
            return False
        
        # Get all SQL files
        migration_files = sorted(migrations_dir.glob("*.sql"))
        
        if not migration_files:
            logger.warning("No migration files found")
            return True
        
        logger.info(f"Found {len(migration_files)} migration(s)")
        
        # Run each migration
        success_count = 0
        for migration_file in migration_files:
            if await run_migration(conn, migration_file):
                success_count += 1
        
        await conn.close()
        
        logger.info(f"{'='*50}")
        logger.info(f"Database setup completed!")
        logger.info(f"Successful migrations: {success_count}/{len(migration_files)}")
        logger.info(f"{'='*50}")
        
        return success_count == len(migration_files)
        
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting database setup...")
    success = asyncio.run(setup_database())
    
    if success:
        logger.info("🎉 Database is ready!")
        exit(0)
    else:
        logger.error("❌ Database setup failed")
        exit(1)
