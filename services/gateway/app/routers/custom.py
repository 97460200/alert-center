"""Custom business alert webhook router."""
from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, Header

from app.dependencies import get_kafka_producer
from app.normalizers.custom import normalize_custom_alert
from app.schemas.custom import CustomAlert, CustomAlertBatch
from shared.kafka import KafkaProducer

logger = structlog.get_logger()
router = APIRouter()


@router.post("/custom/{tenant_id}")
async def receive_custom_alert(
    tenant_id: int,
    payload: CustomAlert,
    kafka_producer: KafkaProducer = Depends(get_kafka_producer),
    x_api_key: str = Header(...),
):
    logger.info("custom_alert_received", tenant_id=tenant_id, source=payload.source)
    normalized = normalize_custom_alert(payload, tenant_id)
    await kafka_producer.send_alert_raw(normalized, key=normalized["fingerprint"])
    return {"status": "ok", "fingerprint": normalized["fingerprint"]}


@router.post("/custom/{tenant_id}/batch")
async def receive_custom_alert_batch(
    tenant_id: int,
    payload: CustomAlertBatch,
    kafka_producer: KafkaProducer = Depends(get_kafka_producer),
    x_api_key: str = Header(...),
):
    logger.info(
        "custom_alert_batch_received",
        tenant_id=tenant_id,
        alert_count=len(payload.alerts),
    )
    fingerprints = []
    for alert in payload.alerts:
        normalized = normalize_custom_alert(alert, tenant_id)
        await kafka_producer.send_alert_raw(normalized, key=normalized["fingerprint"])
        fingerprints.append(normalized["fingerprint"])
    return {
        "status": "ok",
        "alerts_received": len(payload.alerts),
        "fingerprints": fingerprints,
    }
