from fastapi import FastAPI
from fastapi.responses import RedirectResponse, Response
from fastapi.openapi.docs import get_swagger_ui_html
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


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.get("/docs", include_in_schema=False)
async def swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
    )


app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/users", tags=["User Management"])
app.include_router(user_router, prefix="/user", tags=["User Management (Legacy)"])
