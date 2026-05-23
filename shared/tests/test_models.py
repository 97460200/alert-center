"""Tests for models."""
from shared.models import Tenant, TenantStatus, User, UserRole, Alert, AlertStatus, AlertSeverity


def test_tenant_model():
    tenant = Tenant(name="test-tenant", status=TenantStatus.ACTIVE)
    assert tenant.name == "test-tenant"
    assert tenant.status == TenantStatus.ACTIVE


def test_user_model():
    user = User(username="test-user", tenant_id=1, role=UserRole.ADMIN, password_hash="hashed")
    assert user.username == "test-user"
    assert user.role == UserRole.ADMIN


def test_alert_model():
    alert = Alert(
        tenant_id=1,
        fingerprint="abc123",
        source="prometheus",
        severity=AlertSeverity.P1,
        labels="{}",
        annotations="{}",
    )
    assert alert.fingerprint == "abc123"
    assert alert.status == AlertStatus.PENDING
    assert alert.severity == AlertSeverity.P1
