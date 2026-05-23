"""Custom alert normalizer."""
from __future__ import annotations

from datetime import datetime

from app.schemas.custom import CustomAlert
from shared.utils.fingerprint import generate_fingerprint


def normalize_custom_alert(alert: CustomAlert, tenant_id: int) -> dict:
    severity = alert.severity.upper()
    if severity not in ["P0", "P1", "P2", "P3", "P4"]:
        severity = "P3"
    fingerprint = generate_fingerprint(alert.source, alert.labels)
    status = "resolved" if alert.resolved_at else "firing"
    return {
        "tenant_id": tenant_id,
        "source": alert.source,
        "fingerprint": fingerprint,
        "status": status,
        "severity": severity,
        "labels": alert.labels,
        "annotations": alert.annotations,
        "started_at": (alert.started_at or datetime.now()).isoformat(),
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
    }
