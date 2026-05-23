"""Deduplication worker."""
from __future__ import annotations

import structlog
from typing import Any

import redis.asyncio as redis

from app.config import settings
from app.workers.base import BaseWorker

logger = structlog.get_logger()


class DedupWorker(BaseWorker):
    def __init__(self):
        self.redis: redis.Redis | None = None

    async def _get_redis(self) -> redis.Redis:
        if self.redis is None:
            self.redis = redis.from_url(settings.redis_url)
        return self.redis

    async def process(self, alert: dict[str, Any]) -> dict[str, Any] | None:
        fingerprint = alert.get("fingerprint")
        if not fingerprint:
            return alert

        r = await self._get_redis()
        key = f"dedup:{alert['tenant_id']}:{fingerprint}"

        existing = await r.get(key)
        if existing:
            dedup_count = int(existing) + 1
            await r.setex(key, settings.dedup_window_seconds, str(dedup_count))
            logger.debug("alert_deduplicated", fingerprint=fingerprint, dedup_count=dedup_count)
            return None

        await r.setex(key, settings.dedup_window_seconds, "1")
        alert["dedup_count"] = 0
        return alert
