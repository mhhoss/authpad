import os
from typing import AsyncGenerator
import asyncpg
from dotenv import load_dotenv


load_dotenv()
DB_URL = os.getenv("DB_URL")


async def get_conn():
    return await asyncpg.connect(DB_URL)


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    conn = await get_conn()
    try:
        yield conn
    finally:
        await conn.close()