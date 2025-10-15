from fastapi import FastAPI
from app.auth import routes as auth_router


app = FastAPI()
app.include_router(auth_router, prefix="/auth")

