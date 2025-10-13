from fastapi import FastAPI
from app.auth import routes


app = FastAPI()
app.include_router(routes.router)

