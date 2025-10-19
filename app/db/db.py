import os
from typing import AsyncGenerator
import asyncpg
from dotenv import load_dotenv


load_dotenv()
DB_URL = os.getenv("DB_URL")


# برای نگهداری اتصال های پایگاه داده به صورت استخر برای جلوگیری از کانکت های متداول
_POOL: asyncpg.Pool | None = None

# اگر قبلا استخر ساخته نشده باشه اینجا ساخته میشه
async def init_pool() -> None:
    global _POOL
    if _POOL is None:
        _POOL = await asyncpg.create_pool(DB_URL, min_size=1, max_size=10)

# این تابع اتصالات رو بعد انجام عملیات میبنده و منابع رو آزاد میکنه
async def close_pool() -> None:
    global _POOL
    if _POOL is not None:
        await _POOL.close()
        _POOL = None

"""
main file: با استفاده از این دو تا تابع اتصالات رو مدیریت میکنیم
"""



async def get_conn() -> AsyncGenerator[asyncpg.Connection, None]:
    if _POOL is None:
        await init_pool()
    async with _POOL.acquire() as conn:
        # acquire() یک اتصال از استخر میگیره و بعد از اتمام کار آزادش میکنه
        yield conn
