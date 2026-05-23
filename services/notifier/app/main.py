"""Notifier service main entry."""
from __future__ import annotations
import asyncio
import structlog
from shared.kafka import KafkaConsumer, Topics
from app.config import settings
from app.dispatcher import NotificationDispatcher

logger = structlog.get_logger()

async def main():
    logger.info("notifier_starting", service=settings.service_name)
    consumer = KafkaConsumer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_consumer_group,
        topics=[Topics.ALERT_NOTIFY],
    )
    dispatcher = NotificationDispatcher()
    await consumer.start()
    try:
        async for message in consumer.consume():
            alert = message["value"]
            await dispatcher.dispatch(alert)
    finally:
        await consumer.stop()
        logger.info("notifier_stopped")

if __name__ == "__main__":
    asyncio.run(main())
