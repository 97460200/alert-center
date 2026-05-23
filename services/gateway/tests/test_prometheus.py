"""Tests for Prometheus webhook."""
from datetime import datetime

from app.normalizers.prometheus import normalize_prometheus_alert
from app.schemas.prometheus import PrometheusAlert, PrometheusWebhook


def test_normalize_prometheus_alert():
    alert = PrometheusAlert(
        status="firing",
        labels={"alertname": "HighCPU", "service": "api", "severity": "P1"},
        annotations={"summary": "CPU usage is high"},
        startsAt=datetime(2024, 1, 1, 12, 0, 0),
        endsAt=None,
        generatorURL="http://prometheus:9090/graph",
        fingerprint="abc123",
    )
    normalized = normalize_prometheus_alert(alert, tenant_id=1)
    assert normalized["tenant_id"] == 1
    assert normalized["source"] == "prometheus"
    assert normalized["status"] == "firing"
    assert normalized["severity"] == "P1"
    assert normalized["labels"]["alertname"] == "HighCPU"
    assert len(normalized["fingerprint"]) == 64


def test_normalize_prometheus_alert_resolved():
    alert = PrometheusAlert(
        status="resolved",
        labels={"alertname": "HighCPU", "service": "api"},
        annotations={"summary": "CPU usage is back to normal"},
        startsAt=datetime(2024, 1, 1, 12, 0, 0),
        endsAt=datetime(2024, 1, 1, 12, 5, 0),
    )
    normalized = normalize_prometheus_alert(alert, tenant_id=1)
    assert normalized["status"] == "resolved"
    assert normalized["resolved_at"] is not None
