"""Alert model."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models.base import Base, TimestampMixin


class AlertStatus(str, enum.Enum):
    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"
    SILENCED = "silenced"
    ACKNOWLEDGED = "acknowledged"


class AlertSeverity(str, enum.Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class AlertSource(str, enum.Enum):
    PROMETHEUS = "prometheus"
    ZABBIX = "zabbix"
    BUSINESS = "business"
    LOG = "log"
    RULE = "rule"


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    def __init__(self, **kwargs):
        kwargs.setdefault("status", AlertStatus.PENDING)
        super().__init__(**kwargs)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus), default=AlertStatus.PENDING, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity), default=AlertSeverity.P3, nullable=False, index=True)
    labels: Mapped[dict] = mapped_column(Text, nullable=False, default=dict)  # JSON stored as Text for compatibility
    annotations: Mapped[dict] = mapped_column(Text, nullable=False, default=dict)
    rule_id: Mapped[int | None] = mapped_column(ForeignKey("alert_rules.id"), nullable=True)
    assignee: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    dedup_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notification_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_notified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    tenant: Mapped[Tenant] = relationship(back_populates="alerts", lazy="selectin")
    events: Mapped[list[AlertEvent]] = relationship(back_populates="alert", lazy="selectin")

    __table_args__ = (
        Index("ix_alerts_tenant_status", "tenant_id", "status"),
        Index("ix_alerts_tenant_severity", "tenant_id", "severity"),
        Index("ix_alerts_tenant_started", "tenant_id", "started_at"),
    )
