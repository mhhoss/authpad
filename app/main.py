from contextlib import asynccontextmanager
from fastapi import FastAPI, lifespan
from app.routers.auth_routes import router as auth_router
from app.routers.user_routes import router as user_router
from app.db.db import init_pool, close_pool
from contextlib import asynccontextmanager


app = FastAPI(
    title="AuthPad API",
    version="0.1.0",
    lifespan=lifespan
    )


app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/user")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    yield
    await close_pool()