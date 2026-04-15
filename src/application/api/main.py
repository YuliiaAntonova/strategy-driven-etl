from __future__ import annotations

from fastapi import FastAPI

from src.application.api.routes.health import router as health_router
from src.application.api.routes.tasks import router as tasks_router

app = FastAPI(title="Strategy-Driven ETL Agent API")
app.include_router(health_router)
app.include_router(tasks_router, prefix="/api")
