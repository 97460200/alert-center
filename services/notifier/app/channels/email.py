"""Email channel (placeholder)."""
from __future__ import annotations
from typing import Any
import structlog
from app.channels.base import BaseChannel

logger = structlog.get_logger()

class EmailChannel(BaseChannel):
    async def send(self, alert: dict[str, Any]) -> bool:
        # TODO: Integrate with SMTP
        logger.info("email_sent_placeholder", fingerprint=alert.get("fingerprint"))
        return True

    async def test(self) -> bool:
        return True
