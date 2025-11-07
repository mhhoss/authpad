import os
from typing import AsyncGenerator
import asyncpg
from dotenv import load_dotenv


load_dotenv()
DB_URL = os.getenv("DB_URL")

_POOL: asyncpg.Pool | None = None


async def init_pool() -> None:
    '''Creates a connection pool with min/max size configuration'''
    global _POOL
    if _POOL is None:
        _POOL = await asyncpg.create_pool(
            DB_URL,
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



async def get_conn() -> AsyncGenerator[asyncpg.Connection, None]:
    '''
    Get a database connection from the pool
    
    Yields:
        asyncpg.Connection: A database connection from the pool
    '''
    if _POOL is None:
        await init_pool()
    async with _POOL.acquire() as conn:
        yield conn



async def check_health() -> bool:
    '''Check if the database connection is responsive'''
    try:
        async with get_conn() as conn:
            test_result = await conn.fetchval("SELECT 1")
            return test_result == 1  # 1 means True
        
    except Exception:
        return False
    


def get_db_url():
    '''get db URL from sqlalchemy'''
    return DB_URL