"""Route policy model."""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models.base import Base, TimestampMixin


class RoutePolicy(Base, TimestampMixin):
    __tablename__ = "route_policies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    match_labels: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    targets: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    channel_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tenant: Mapped[Tenant] = relationship(back_populates="routes", lazy="selectin")
