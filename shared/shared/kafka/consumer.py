"""Kafka consumer wrapper."""
from __future__ import annotations

import json
from collections.abc import AsyncGenerator

import structlog
from aiokafka import AIOKafkaConsumer

logger = structlog.get_logger()


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str, topics: list[str], auto_offset_reset: str = "earliest"):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topics = topics
        self.auto_offset_reset = auto_offset_reset
        self._consumer: AIOKafkaConsumer | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset=self.auto_offset_reset,
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
        )
        await self._consumer.start()
        logger.info("kafka_consumer_started", group_id=self.group_id, topics=self.topics)

    async def stop(self) -> None:
        if self._consumer:
            await self._consumer.stop()
            logger.info("kafka_consumer_stopped")

    async def consume(self) -> AsyncGenerator[dict, None]:
        if not self._consumer:
            raise RuntimeError("Consumer not started")
        async for message in self._consumer:
            yield {
                "topic": message.topic,
                "partition": message.partition,
                "offset": message.offset,
                "key": message.key,
                "value": message.value,
                "timestamp": message.timestamp,
            }
