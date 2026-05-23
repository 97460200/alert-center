"""Alert schemas for Admin API."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: str
    tenant_id: int
    fingerprint: str
    status: str
    source: str
    severity: str
    labels: str
    annotations: str
    dedup_count: int
    notification_count: int
    started_at: datetime
    resolved_at: datetime | None
    assignee: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    items: list[AlertResponse]
    total: int
    page: int
    page_size: int


class AlertAcknowledgeRequest(BaseModel):
    assignee: int | None = None


class AlertResolveRequest(BaseModel):
    reason: str | None = None
