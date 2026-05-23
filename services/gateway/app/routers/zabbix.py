"""Zabbix webhook router."""
from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, Header

from app.dependencies import get_kafka_producer
from app.schemas.zabbix import ZabbixAlert
from shared.kafka import KafkaProducer
from shared.utils.fingerprint import generate_fingerprint

logger = structlog.get_logger()
router = APIRouter()

SEVERITY_MAP = {
    "Disaster": "P0",
    "High": "P1",
    "Average": "P2",
    "Warning": "P3",
    "Not classified": "P4",
}


@router.post("/zabbix/{tenant_id}")
async def receive_zabbix_webhook(
    tenant_id: int,
    payload: ZabbixAlert,
    kafka_producer: KafkaProducer = Depends(get_kafka_producer),
    x_api_key: str = Header(...),
):
    logger.info("zabbix_webhook_received", tenant_id=tenant_id, host=payload.host)
    severity = SEVERITY_MAP.get(payload.severity, "P3")
    labels = {"host": payload.host, "trigger": payload.trigger_name, **payload.tags}
    fingerprint = generate_fingerprint("zabbix", labels)
    normalized = {
        "tenant_id": tenant_id,
        "source": "zabbix",
        "fingerprint": fingerprint,
        "status": "firing" if payload.value == "1" else "resolved",
        "severity": severity,
        "labels": labels,
        "annotations": {"trigger_name": payload.trigger_name, "event_id": payload.event_id},
        "started_at": payload.datetime.isoformat(),
    }
    await kafka_producer.send_alert_raw(normalized, key=fingerprint)
    return {"status": "ok", "fingerprint": fingerprint}
