"""Tests for notification channels."""
import pytest
from unittest.mock import AsyncMock, patch
from app.channels.webhook import WebhookChannel

@pytest.mark.asyncio
async def test_webhook_channel_send():
    channel = WebhookChannel({"url": "https://example.com/webhook", "headers": {"Authorization": "Bearer token"}})
    alert = {
        "fingerprint": "abc123", "source": "test", "severity": "P1",
        "status": "firing", "labels": {"service": "api"},
        "annotations": {"summary": "Test alert"},
    }
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        result = await channel.send(alert)
        assert result is True

@pytest.mark.asyncio
async def test_webhook_channel_missing_url():
    channel = WebhookChannel({})
    alert = {"fingerprint": "abc123", "source": "test", "severity": "P1", "status": "firing"}
    result = await channel.send(alert)
    assert result is False
