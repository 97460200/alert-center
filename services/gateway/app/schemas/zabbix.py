"""Zabbix webhook schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ZabbixAlert(BaseModel):
    event_id: str = Field(alias="eventId")
    host: str
    trigger_name: str = Field(alias="triggerName")
    severity: str
    status: str
    value: str
    datetime: datetime
    tags: dict[str, str] = Field(default_factory=dict)
