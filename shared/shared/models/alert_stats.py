"""Alert stats model."""
from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.models.base import Base


class AlertStats(Base):
    __tablename__ = "alert_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stat_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(2), nullable=False)
    total_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    resolved_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_resolve_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notify_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dedup_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
