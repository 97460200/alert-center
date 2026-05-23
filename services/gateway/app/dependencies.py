"""FastAPI dependencies."""
from __future__ import annotations

from shared.kafka import KafkaProducer

from app.config import settings

_kafka_producer: KafkaProducer | None = None


async def get_kafka_producer() -> KafkaProducer:
    global _kafka_producer
    if _kafka_producer is None:
        _kafka_producer = KafkaProducer(settings.kafka_bootstrap_servers)
        await _kafka_producer.start()
    return _kafka_producer
