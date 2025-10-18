import os
from typing import AsyncGenerator
import asyncpg
from dotenv import load_dotenv


load_dotenv()
DB_URL = os.getenv("DB_URL")


# برای نگهداری اتصال های پایگاه داده به صورت استخر برای جلوگیری از کانکت های متداول
_pool: asyncpg.Pool | None = None

# اگر قبلا استخر ساخته نشده باشه اینجا ساخته میشه
async def init_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=10)

# این تابع اتصالات رو بعد انجام عملیات میبنده و منابع رو آزاد میکنه
async def close_pool():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None

"""
main file: با استفاده از این دو تا تابع اتصالات رو مدیریت میکنیم
"""



async def get_conn() -> AsyncGenerator[asyncpg.Connection, None]:
    if _pool is None:
        await init_pool()
    async with _pool.acquire() as conn:
        # acquire() یک اتصال از استخر میگیره و بعد از اتمام کار آزادش میکنه
        yield conn
