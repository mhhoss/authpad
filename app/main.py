from fastapi import FastAPI
from app.auth import routes as auth_router
from app.db import db


async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(
    title="AuthPad API",
    description="Secure authentication API with JWT, FastAPI, and PostgreSQL",
    version="0.1.0",
    lifespan=lifespan
    )

app.include_router(auth_router, prefix="/auth")
