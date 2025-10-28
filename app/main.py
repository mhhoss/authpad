from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.user.routes import router as user_router
from app.db.connection import init_pool, close_pool
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    yield
    await close_pool()


app = FastAPI(
    title="AuthPad API",
    version="0.1.0",
    lifespan=lifespan
    )


app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/user", tags=["User Management"])
