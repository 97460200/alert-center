"""Convergence worker."""
from __future__ import annotations

import structlog
from typing import Any

from app.workers.base import BaseWorker

logger = structlog.get_logger()


class ConvergeWorker(BaseWorker):
    async def process(self, alert: dict[str, Any]) -> dict[str, Any] | None:
        # TODO: Implement convergence logic
        return alert
