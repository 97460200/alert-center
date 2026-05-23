"""Enrichment worker."""
from __future__ import annotations

import structlog
from typing import Any

from app.workers.base import BaseWorker

logger = structlog.get_logger()


class EnrichWorker(BaseWorker):
    async def process(self, alert: dict[str, Any]) -> dict[str, Any] | None:
        alert["enriched"] = True
        return alert
