"""Generic webhook channel."""
from __future__ import annotations
from typing import Any
import httpx
import structlog
from app.channels.base import BaseChannel

logger = structlog.get_logger()

class WebhookChannel(BaseChannel):
    async def send(self, alert: dict[str, Any]) -> bool:
        url = self.config.get("url")
        headers = self.config.get("headers", {})
        timeout = self.config.get("timeout", 10)
        if not url:
            logger.error("webhook_missing_url")
            return False
        payload = {
            "fingerprint": alert.get("fingerprint"),
            "source": alert.get("source"),
            "severity": alert.get("severity"),
            "status": alert.get("status"),
            "labels": alert.get("labels"),
            "annotations": alert.get("annotations"),
            "started_at": alert.get("started_at"),
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=timeout)
                if response.status_code < 400:
                    logger.info("webhook_sent", url=url, status=response.status_code)
                    return True
                logger.error("webhook_failed", url=url, status=response.status_code)
                return False
        except Exception as e:
            logger.error("webhook_error", url=url, error=str(e))
            return False

    async def test(self) -> bool:
        return await self.send({"severity": "P3", "status": "test", "labels": {"test": "true"}, "annotations": {"summary": "Test"}, "source": "test"})
