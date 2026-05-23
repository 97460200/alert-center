"""Log alert webhook router."""
from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, Header

from app.dependencies import get_kafka_producer
from app.schemas.log import LogAlert
from shared.kafka import KafkaProducer
from shared.utils.fingerprint import generate_fingerprint

logger = structlog.get_logger()
router = APIRouter()


@router.post("/log/{tenant_id}")
async def receive_log_alert(
    tenant_id: int,
    payload: LogAlert,
    kafka_producer: KafkaProducer = Depends(get_kafka_producer),
    x_api_key: str = Header(...),
):
    logger.info("log_alert_received", tenant_id=tenant_id, source=payload.source)
    severity = payload.severity.upper()
    if severity not in ["P0", "P1", "P2", "P3", "P4"]:
        severity = "P3"
    labels = {"source": payload.source, **payload.labels}
    fingerprint = generate_fingerprint("log", labels)
    normalized = {
        "tenant_id": tenant_id,
        "source": "log",
        "fingerprint": fingerprint,
        "status": "firing",
        "severity": severity,
        "labels": labels,
        "annotations": {"message": payload.message, **payload.metadata},
        "started_at": payload.timestamp.isoformat(),
    }
    await kafka_producer.send_alert_raw(normalized, key=fingerprint)
    return {"status": "ok", "fingerprint": fingerprint}
