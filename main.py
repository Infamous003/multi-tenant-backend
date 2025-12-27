from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.db import wait_for_db
from app.core.logging import get_logger
from app.api.routers import tenants

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()
    yield


app = FastAPI(app_name=settings.APP_NAME, lifespan=lifespan)

app.include_router(
    prefix="/api/v1",
    router=tenants.router,
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Multi-Tenant Backend Service"}