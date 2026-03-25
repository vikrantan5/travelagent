import os
import ssl
import asyncpg
from typing import Any, AsyncGenerator, Dict, Optional
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from loguru import logger


# -----------------------------
# DATABASE URL FIX
# -----------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "")

RAW_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://"
    )

logger.info(f"Using DATABASE_URL: {DATABASE_URL}")

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None
_db_pool: Optional[asyncpg.Pool] = None


# -----------------------------
# DB POOL (asyncpg)
# -----------------------------
def get_db_pool() -> asyncpg.Pool:
    """Get the asyncpg connection pool for direct queries"""
    global _db_pool
    if _db_pool is None:
        raise RuntimeError("Database pool not initialized. Call initialize_db_pool() first.")
    return _db_pool


# -----------------------------
# DB INITIALIZATION
# -----------------------------
async def initialize_db_pool(pool_size: int = 5, max_overflow: int = 10) -> None:
    global _engine, _session_factory, _db_pool

    if _engine is not None:
        return

    logger.info("Initializing Supabase connection (PgBouncer safe)")

    try:
        # SSL context for Supabase
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # -------------------------------------------------------
        # asyncpg pool
        # -------------------------------------------------------
        logger.info("Creating asyncpg connection pool")
        _db_pool = await asyncpg.create_pool(
            RAW_URL,
            min_size=2,
            max_size=pool_size,
            ssl=ssl_context,
            command_timeout=60,
            statement_cache_size=0,
            server_settings={
                'jit': 'off'
            }
        )

        # Test connection
        async with _db_pool.acquire() as conn:
            await conn.execute("SELECT 1")
        logger.info("Asyncpg pool created successfully")

        # -------------------------------------------------------
        # SQLAlchemy engine
        # -------------------------------------------------------
        _engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            future=True,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
                "prepared_statement_name_func": None,
                "ssl": ssl_context,
                "timeout": 30,
                "server_settings": {
                    "jit": "off",
                    "application_name": "tripcraft_app"
                }
            }
        )

        _session_factory = async_sessionmaker(
            _engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        logger.info("🔥 Database connected successfully via Supabase Pooler!")

    except Exception as e:
        logger.error(f"❌ Failed to initialize DB pool: {e}")
        raise


# -----------------------------
# CLOSE DB
# -----------------------------
async def close_db_pool() -> None:
    global _engine, _db_pool

    if _db_pool is not None:
        logger.info("Closing asyncpg pool")
        await _db_pool.close()
        _db_pool = None

    if _engine is not None:
        logger.info("Closing SQLAlchemy engine")
        await _engine.dispose()
        _engine = None


# -----------------------------
# GET SESSION
# -----------------------------
@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    if _session_factory is None:
        await initialize_db_pool()

    session: AsyncSession = _session_factory()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Session error: {e}")
        raise
    finally:
        await session.close()


# -----------------------------
# RAW QUERY EXECUTION
# -----------------------------
async def execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> list:
    async with get_db_session() as session:
        try:
            result = await session.execute(text(query), params or {})
            try:
                return result.fetchall()
            except Exception:
                return []
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            raise