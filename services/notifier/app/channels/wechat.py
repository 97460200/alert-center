"""WeChat Work robot channel."""
from __future__ import annotations
from typing import Any
import httpx
import structlog
from app.channels.base import BaseChannel

logger = structlog.get_logger()

class WeChatChannel(BaseChannel):
    async def send(self, alert: dict[str, Any]) -> bool:
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return False
        severity = alert.get("severity", "P3")
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        content = annotations.get("summary", "No summary")
        message = {
            "msgtype": "markdown",
            "markdown": {"content": f"## [{severity}] {labels.get('alertname', 'Alert')}\n\n{content}"},
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=message, timeout=10)
                result = response.json()
                if result.get("errcode") == 0:
                    return True
                return False
        except Exception as e:
            logger.error("wechat_error", error=str(e))
            return False

    async def test(self) -> bool:
        return await self.send({"severity": "P3", "status": "test", "labels": {}, "annotations": {"summary": "Test"}, "source": "test"})
