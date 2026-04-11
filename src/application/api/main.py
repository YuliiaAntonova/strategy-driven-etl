from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.application.api.routes.health import router as health_router
from src.application.api.routes.tasks import router as tasks_router
from src.application.api.routes.pipelines import router as pipelines_router

app = FastAPI(title="Strategy-Driven ETL Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(tasks_router, prefix="/api")
app.include_router(pipelines_router, prefix="/api")