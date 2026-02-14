from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncpg

from app.core.config import settings


_POOL: asyncpg.Pool | None = None


async def init_pool() -> None:
    '''Creates a connection pool with min/max size configuration'''
    global _POOL
    if _POOL is None:
        if not settings.DB_URL:
            raise RuntimeError("DB_URL is not configured")
        _POOL = await asyncpg.create_pool(
            settings.DB_URL,
            min_size=1,
            max_size=10,
            command_timeout=30
            )


async def close_pool() -> None:
    '''Close the database connection pool and cleanup resources'''
    global _POOL
    if _POOL is not None:
        await _POOL.close()
        _POOL = None


@asynccontextmanager
async def conn_ctx() -> AsyncGenerator[asyncpg.Connection, None]:
    '''
    Async context manager for obtaining a DB connection from the global pool.

    Use this outside of FastAPI dependency injection.
    '''
    if _POOL is None:
        await init_pool()
    async with _POOL.acquire() as conn:
        yield conn


async def get_conn() -> AsyncGenerator[asyncpg.Connection, None]:
    '''
    Get a database connection from the pool
    '''
    async with conn_ctx() as conn:
        yield conn


async def check_health() -> bool:
    '''Check if the database connection is responsive'''
    try:
        async with conn_ctx() as conn:
            test_result = await conn.fetchval("SELECT 1")
            return test_result == 1  # 1 means True
        
    except Exception:
        return False
    

def get_db_url():
    '''get db URL from sqlalchemy'''
    return settings.DB_URL