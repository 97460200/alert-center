"""Workers module."""
from app.workers.base import BaseWorker
from app.workers.dedup import DedupWorker

__all__ = ["BaseWorker", "DedupWorker"]
