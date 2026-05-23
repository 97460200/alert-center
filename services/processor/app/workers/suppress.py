"""Suppression worker."""
from __future__ import annotations

import structlog
from typing import Any

from app.workers.base import BaseWorker

logger = structlog.get_logger()


class SuppressWorker(BaseWorker):
    async def process(self, alert: dict[str, Any]) -> dict[str, Any] | None:
        # TODO: Check for higher severity alerts
        return alert
