from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(app_name=settings.APP_NAME)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Multi-Tenant Backend Service"}