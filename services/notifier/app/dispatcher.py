"""Notification dispatcher."""
from __future__ import annotations
import structlog
from typing import Any
from app.channels import CHANNEL_MAP, BaseChannel

logger = structlog.get_logger()

class NotificationDispatcher:
    async def dispatch(self, alert: dict[str, Any]) -> None:
        logger.info("notification_dispatch", fingerprint=alert.get("fingerprint"), severity=alert.get("severity"))

    def get_channel(self, channel_type: str, config: dict[str, Any]) -> BaseChannel:
        channel_class = CHANNEL_MAP.get(channel_type)
        if not channel_class:
            raise ValueError(f"Unknown channel type: {channel_type}")
        return channel_class(config)
