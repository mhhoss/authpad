from fastapi import FastAPI
from app.routers.auth_routes import router as auth_router
from app.routers.user_routes import router as user_router


app = FastAPI(
    title="AuthPad API",
    description="Secure authentication API with JWT, FastAPI, and PostgreSQL",
    version="0.1.0"
    )


app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/user")
