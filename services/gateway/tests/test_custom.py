"""Tests for custom alert webhook."""
from datetime import datetime

from app.normalizers.custom import normalize_custom_alert
from app.schemas.custom import CustomAlert


def test_normalize_custom_alert():
    alert = CustomAlert(
        source="business-service",
        severity="P1",
        labels={"service": "payment", "env": "prod"},
        annotations={"summary": "Payment gateway timeout"},
        started_at=datetime(2024, 1, 1, 12, 0, 0),
    )
    normalized = normalize_custom_alert(alert, tenant_id=1)
    assert normalized["tenant_id"] == 1
    assert normalized["source"] == "business-service"
    assert normalized["status"] == "firing"
    assert normalized["severity"] == "P1"
    assert len(normalized["fingerprint"]) == 64


def test_normalize_custom_alert_resolved():
    alert = CustomAlert(
        source="business-service",
        severity="P2",
        labels={"service": "payment"},
        started_at=datetime(2024, 1, 1, 12, 0, 0),
        resolved_at=datetime(2024, 1, 1, 12, 5, 0),
    )
    normalized = normalize_custom_alert(alert, tenant_id=1)
    assert normalized["status"] == "resolved"
    assert normalized["resolved_at"] is not None
