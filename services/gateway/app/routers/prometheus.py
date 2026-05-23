"""Prometheus Alertmanager webhook router."""
from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, Header

from app.dependencies import get_kafka_producer
from app.normalizers.prometheus import normalize_prometheus_alert
from app.schemas.prometheus import PrometheusWebhook
from shared.kafka import KafkaProducer

logger = structlog.get_logger()
router = APIRouter()


@router.post("/prometheus/{tenant_id}")
async def receive_prometheus_webhook(
    tenant_id: int,
    payload: PrometheusWebhook,
    kafka_producer: KafkaProducer = Depends(get_kafka_producer),
    x_api_key: str | None = Header(default=None),
):
    logger.info(
        "prometheus_webhook_received",
        tenant_id=tenant_id,
        alert_count=len(payload.alerts),
    )
    for alert in payload.alerts:
        normalized = normalize_prometheus_alert(alert, tenant_id)
        await kafka_producer.send_alert_raw(normalized, key=normalized["fingerprint"])
    return {"status": "ok", "alerts_received": len(payload.alerts)}
