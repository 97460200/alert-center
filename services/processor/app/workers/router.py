"""Router worker."""
from __future__ import annotations

import structlog
from typing import Any

from shared.kafka import KafkaProducer, Topics

from app.config import settings
from app.workers.base import BaseWorker

logger = structlog.get_logger()


class RouterWorker(BaseWorker):
    def __init__(self):
        self.producer: KafkaProducer | None = None

    async def _get_producer(self) -> KafkaProducer:
        if self.producer is None:
            self.producer = KafkaProducer(settings.kafka_bootstrap_servers)
            await self.producer.start()
        return self.producer

    async def process(self, alert: dict[str, Any]) -> dict[str, Any] | None:
        producer = await self._get_producer()
        await producer.send_alert_notify(alert, key=alert.get("fingerprint"))
        logger.debug("alert_routed", fingerprint=alert.get("fingerprint"))
        return alert
