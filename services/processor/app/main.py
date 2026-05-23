"""Processor service main entry."""
from __future__ import annotations

import asyncio

import structlog

from shared.kafka import KafkaConsumer, Topics

from app.config import settings
from app.workers.converge import ConvergeWorker
from app.workers.dedup import DedupWorker
from app.workers.enrich import EnrichWorker
from app.workers.router import RouterWorker
from app.workers.silence import SilenceWorker
from app.workers.suppress import SuppressWorker

logger = structlog.get_logger()


async def main():
    logger.info("processor_starting", service=settings.service_name)

    consumer = KafkaConsumer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_consumer_group,
        topics=[Topics.ALERT_RAW],
    )

    workers = [
        DedupWorker(),
        SilenceWorker(),
        SuppressWorker(),
        ConvergeWorker(),
        EnrichWorker(),
        RouterWorker(),
    ]

    await consumer.start()
    try:
        async for message in consumer.consume():
            alert = message["value"]
            for worker in workers:
                alert = await worker.process(alert)
                if alert is None:
                    break
            if alert:
                logger.debug("alert_processed", fingerprint=alert.get("fingerprint"))
    finally:
        await consumer.stop()
        logger.info("processor_stopped")


if __name__ == "__main__":
    asyncio.run(main())
