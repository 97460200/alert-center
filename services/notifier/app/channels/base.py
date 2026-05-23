"""Base notification channel."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class BaseChannel(ABC):
    def __init__(self, config: dict[str, Any]):
        self.config = config

    @abstractmethod
    async def send(self, alert: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def test(self) -> bool:
        pass
