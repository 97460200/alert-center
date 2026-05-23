"""Prometheus Alertmanager webhook schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PrometheusAlert(BaseModel):
    status: str
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    starts_at: datetime = Field(alias="startsAt")
    ends_at: datetime | None = Field(default=None, alias="endsAt")
    generator_url: str | None = Field(default=None, alias="generatorURL")
    fingerprint: str | None = None


class PrometheusWebhook(BaseModel):
    receiver: str
    status: str
    alerts: list[PrometheusAlert]
    group_labels: dict[str, str] = Field(default_factory=dict, alias="groupLabels")
    common_labels: dict[str, str] = Field(default_factory=dict, alias="commonLabels")
    common_annotations: dict[str, str] = Field(
        default_factory=dict, alias="commonAnnotations"
    )
    external_url: str = Field(alias="externalURL")
    version: str = "4"
    group_key: str = Field(alias="groupKey")
