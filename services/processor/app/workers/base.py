"""Base worker class."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseWorker(ABC):
    @abstractmethod
    async def process(self, alert: dict[str, Any]) -> dict[str, Any] | None:
        pass
