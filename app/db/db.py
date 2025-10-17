import os
from typing import AsyncGenerator
import asyncpg
from dotenv import load_dotenv


load_dotenv()
DB_URL = os.getenv("DB_URL")


async def get_conn():
    DB_URL = os.getenv("DB_URL")
    if not DB_URL:
        raise RuntimeError("DB_URL not found in enviroment variables!")
    return await asyncpg.connect(DB_URL)


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    conn = await get_conn()
    try:
        yield conn
    finally:
        await conn.close()