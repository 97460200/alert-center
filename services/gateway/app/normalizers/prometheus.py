"""Prometheus alert normalizer."""
from __future__ import annotations

from app.schemas.prometheus import PrometheusAlert
from shared.utils.fingerprint import generate_fingerprint


def normalize_prometheus_alert(alert: PrometheusAlert, tenant_id: int) -> dict:
    status_map = {"firing": "firing", "resolved": "resolved"}
    internal_status = status_map.get(alert.status, "pending")
    severity = alert.labels.get("severity", "P3")
    if severity not in ["P0", "P1", "P2", "P3", "P4"]:
        severity = "P3"
    fingerprint = generate_fingerprint("prometheus", alert.labels)
    return {
        "tenant_id": tenant_id,
        "source": "prometheus",
        "fingerprint": fingerprint,
        "status": internal_status,
        "severity": severity,
        "labels": alert.labels,
        "annotations": alert.annotations,
        "started_at": alert.starts_at.isoformat(),
        "resolved_at": alert.ends_at.isoformat() if alert.ends_at else None,
        "raw": {
            "generator_url": alert.generator_url,
            "prometheus_fingerprint": alert.fingerprint,
        },
    }
