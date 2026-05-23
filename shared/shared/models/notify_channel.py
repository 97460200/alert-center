"""Notify channel model."""
from __future__ import annotations

import enum

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models.base import Base, TimestampMixin


class ChannelType(str, enum.Enum):
    DINGTALK = "dingtalk"
    WECHAT = "wechat"
    FEISHU = "feishu"
    SMS = "sms"
    PHONE = "phone"
    EMAIL = "email"
    WEBHOOK = "webhook"


class NotifyChannel(Base, TimestampMixin):
    __tablename__ = "notify_channels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[ChannelType] = mapped_column(Enum(ChannelType), nullable=False)
    config: Mapped[str] = mapped_column(Text, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tenant: Mapped[Tenant] = relationship(back_populates="channels", lazy="selectin")
