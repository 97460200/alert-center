"""Log alert schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LogAlert(BaseModel):
    source: str
    message: str
    severity: str = Field(default="P3")
    labels: dict[str, str] = Field(default_factory=dict)
    timestamp: datetime
    metadata: dict[str, str] = Field(default_factory=dict)
