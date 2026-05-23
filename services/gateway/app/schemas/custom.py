"""Custom business alert schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CustomAlert(BaseModel):
    source: str = Field(description="Alert source identifier")
    severity: str = Field(default="P3")
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    started_at: datetime | None = None
    resolved_at: datetime | None = None


class CustomAlertBatch(BaseModel):
    alerts: list[CustomAlert]
