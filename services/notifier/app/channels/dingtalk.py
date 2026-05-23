"""DingTalk robot channel."""
from __future__ import annotations
import hashlib
import hmac
import time
import base64
import urllib.parse
from typing import Any
import httpx
import structlog
from app.channels.base import BaseChannel

logger = structlog.get_logger()

class DingTalkChannel(BaseChannel):
    async def send(self, alert: dict[str, Any]) -> bool:
        webhook_url = self.config.get("webhook_url")
        secret = self.config.get("secret")
        if not webhook_url:
            logger.error("dingtalk_missing_webhook")
            return False
        severity = alert.get("severity", "P3")
        status = alert.get("status", "firing")
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        title = f"[{severity}] {labels.get('alertname', 'Alert')} - {status}"
        content = annotations.get("summary", "No summary")
        message = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": f"### {title}\n\n{content}\n\n> Source: {alert.get('source')}\n> Fingerprint: {alert.get('fingerprint', '')[:16]}...",
            },
        }
        url = webhook_url
        if secret:
            timestamp = str(int(time.time() * 1000))
            sign = self._sign(timestamp, secret)
            url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=message, timeout=10)
                result = response.json()
                if result.get("errcode") == 0:
                    logger.info("dingtalk_sent", fingerprint=alert.get("fingerprint"))
                    return True
                else:
                    logger.error("dingtalk_failed", error=result)
                    return False
        except Exception as e:
            logger.error("dingtalk_error", error=str(e))
            return False

    async def test(self) -> bool:
        return await self.send({"severity": "P3", "status": "test", "labels": {"alertname": "Test"}, "annotations": {"summary": "Test"}, "source": "test"})

    def _sign(self, timestamp: str, secret: str) -> str:
        string_to_sign = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(secret.encode("utf-8"), string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        return urllib.parse.quote_plus(base64.b64encode(hmac_code))
