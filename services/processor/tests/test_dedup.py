"""Tests for dedup worker."""
import pytest
from unittest.mock import AsyncMock

from app.workers.dedup import DedupWorker


@pytest.mark.asyncio
async def test_dedup_worker_new_alert():
    worker = DedupWorker()
    worker.redis = AsyncMock()
    worker.redis.get = AsyncMock(return_value=None)
    worker.redis.setex = AsyncMock()

    alert = {"tenant_id": 1, "fingerprint": "abc123", "status": "firing"}
    result = await worker.process(alert)

    assert result is not None
    assert result["dedup_count"] == 0


@pytest.mark.asyncio
async def test_dedup_worker_duplicate_alert():
    worker = DedupWorker()
    worker.redis = AsyncMock()
    worker.redis.get = AsyncMock(return_value=b"2")
    worker.redis.setex = AsyncMock()

    alert = {"tenant_id": 1, "fingerprint": "abc123", "status": "firing"}
    result = await worker.process(alert)

    assert result is None
