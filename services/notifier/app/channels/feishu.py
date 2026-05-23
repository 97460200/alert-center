"""Feishu robot channel."""
from __future__ import annotations
import hashlib
import hmac
import time
import base64
from typing import Any
import httpx
import structlog
from app.channels.base import BaseChannel

logger = structlog.get_logger()

class FeishuChannel(BaseChannel):
    async def send(self, alert: dict[str, Any]) -> bool:
        webhook_url = self.config.get("webhook_url")
        secret = self.config.get("secret")
        if not webhook_url:
            return False
        severity = alert.get("severity", "P3")
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        content = annotations.get("summary", "No summary")
        message = {
            "msg_type": "interactive",
            "card": {
                "header": {"title": {"tag": "plain_text", "content": f"[{severity}] {labels.get('alertname', 'Alert')}"}},
                "elements": [{"tag": "div", "text": {"tag": "plain_text", "content": content}}],
            },
        }
        url = webhook_url
        if secret:
            timestamp = str(int(time.time()))
            sign = self._sign(timestamp, secret)
            url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=message, timeout=10)
                if response.status_code < 400:
                    return True
                return False
        except Exception as e:
            logger.error("feishu_error", error=str(e))
            return False

    async def test(self) -> bool:
        return await self.send({"severity": "P3", "status": "test", "labels": {}, "annotations": {"summary": "Test"}, "source": "test"})

    def _sign(self, timestamp: str, secret: str) -> str:
        string_to_sign = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(secret.encode("utf-8"), string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        return base64.b64encode(hmac_code).decode("utf-8")
