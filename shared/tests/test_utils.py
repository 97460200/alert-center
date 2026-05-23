"""Tests for utility functions."""
from datetime import datetime, timedelta

from shared.utils.fingerprint import generate_fingerprint, generate_fingerprint_from_alert
from shared.utils.time_window import is_in_time_window, get_time_window_key


def test_generate_fingerprint():
    fp1 = generate_fingerprint("prometheus", {"service": "api", "env": "prod"})
    fp2 = generate_fingerprint("prometheus", {"env": "prod", "service": "api"})
    fp3 = generate_fingerprint("prometheus", {"service": "api", "env": "dev"})
    assert fp1 == fp2  # Same content, same fingerprint
    assert fp1 != fp3  # Different labels, different fingerprint
    assert len(fp1) == 64  # SHA256 hex


def test_generate_fingerprint_from_alert():
    alert = {"source": "prometheus", "labels": {"service": "api"}}
    fp = generate_fingerprint_from_alert(alert)
    assert len(fp) == 64


def test_is_in_time_window():
    now = datetime.now()
    window_start = now - timedelta(seconds=30)
    assert is_in_time_window(now, window_start, 60) is True
    assert is_in_time_window(now - timedelta(seconds=120), window_start, 60) is False


def test_get_time_window_key():
    ts = datetime(2024, 1, 1, 12, 30, 45)
    key = get_time_window_key(ts, 300)
    assert key is not None
    assert isinstance(key, str)
