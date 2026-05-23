"""Kafka producer wrapper."""
from __future__ import annotations

import json
from typing import Any

import structlog
from aiokafka import AIOKafkaProducer

from shared.kafka.topics import Topics

logger = structlog.get_logger()


class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
        await self._producer.start()
        logger.info("kafka_producer_started", bootstrap_servers=self.bootstrap_servers)

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()
            logger.info("kafka_producer_stopped")

    async def send(self, topic: str, value: dict[str, Any], key: str | None = None) -> None:
        if not self._producer:
            raise RuntimeError("Producer not started")
        await self._producer.send_and_wait(topic, value, key=key)
        logger.debug("kafka_message_sent", topic=topic, key=key)

    async def send_alert_raw(self, alert: dict[str, Any], key: str | None = None) -> None:
        await self.send(Topics.ALERT_RAW, alert, key=key)

    async def send_alert_notify(self, alert: dict[str, Any], key: str | None = None) -> None:
        await self.send(Topics.ALERT_NOTIFY, alert, key=key)

    async def send_lifecycle_event(self, event: dict[str, Any], key: str | None = None) -> None:
        await self.send(Topics.ALERT_LIFECYCLE, event, key=key)
