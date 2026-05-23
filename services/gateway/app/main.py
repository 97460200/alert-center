"""Gateway service main entry."""
from __future__ import annotations

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import custom, log, prometheus, zabbix

logger = structlog.get_logger()

app = FastAPI(
    title="Alert Center Gateway",
    description="Alert ingestion service",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(prometheus.router, prefix="/api/v1/webhook", tags=["prometheus"])
app.include_router(zabbix.router, prefix="/api/v1/webhook", tags=["zabbix"])
app.include_router(custom.router, prefix="/api/v1/webhook", tags=["custom"])
app.include_router(log.router, prefix="/api/v1/webhook", tags=["log"])


@app.on_event("startup")
async def startup():
    logger.info("gateway_starting", service=settings.service_name)


@app.on_event("shutdown")
async def shutdown():
    logger.info("gateway_stopping", service=settings.service_name)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.service_name}
