from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.core.config import settings
from app.api.v1.deriv import router as deriv_router

app = FastAPI(title=settings.app_name)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(deriv_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.environment}