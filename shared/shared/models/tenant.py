"""Tenant model."""
from __future__ import annotations

import enum

from sqlalchemy import Boolean, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models.base import Base, TimestampMixin


class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[TenantStatus] = mapped_column(Enum(TenantStatus), default=TenantStatus.ACTIVE, nullable=False)
    config: Mapped[str | None] = mapped_column(Text, nullable=True)

    users: Mapped[list[User]] = relationship(back_populates="tenant", lazy="selectin")
    alerts: Mapped[list[Alert]] = relationship(back_populates="tenant", lazy="selectin")
    rules: Mapped[list[AlertRule]] = relationship(back_populates="tenant", lazy="selectin")
    routes: Mapped[list[RoutePolicy]] = relationship(back_populates="tenant", lazy="selectin")
    channels: Mapped[list[NotifyChannel]] = relationship(back_populates="tenant", lazy="selectin")
    silences: Mapped[list[SilencePolicy]] = relationship(back_populates="tenant", lazy="selectin")
