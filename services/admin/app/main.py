"""Admin service main entry."""
from __future__ import annotations

import structlog

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import alerts, channels, rules, routes, silences, stats, tenants

logger = structlog.get_logger()

app = FastAPI(
    title="Alert Center Admin API",
    description="Admin API for Alert Center",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(rules.router, prefix="/api/v1/rules", tags=["rules"])
app.include_router(routes.router, prefix="/api/v1/routes", tags=["routes"])
app.include_router(channels.router, prefix="/api/v1/channels", tags=["channels"])
app.include_router(silences.router, prefix="/api/v1/silences", tags=["silences"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["stats"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["tenants"])


@app.on_event("startup")
async def startup():
    logger.info("admin_starting", service=settings.service_name)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.service_name}
