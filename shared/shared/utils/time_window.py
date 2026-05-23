"""Time window utilities for alert processing."""
from __future__ import annotations

from datetime import datetime, timedelta


def is_in_time_window(timestamp: datetime, window_start: datetime, window_seconds: int) -> bool:
    """Check if timestamp is within time window."""
    window_end = window_start + timedelta(seconds=window_seconds)
    return window_start <= timestamp <= window_end


def get_time_window_key(timestamp: datetime, window_seconds: int) -> str:
    """Get time window key for grouping."""
    epoch = datetime(1970, 1, 1)
    total_seconds = (timestamp - epoch).total_seconds()
    window_index = int(total_seconds // window_seconds)
    window_start = epoch + timedelta(seconds=window_index * window_seconds)
    return window_start.isoformat()
