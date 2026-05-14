from __future__ import annotations

from dataclasses import asdict
from typing import Any

from core.config.settings import get_settings
from services.queue.base import QueueBackend, QueueLease, QueueTask
from services.queue.memory_queue import MemoryQueueBackend
from services.queue.redis_queue import RedisQueueBackend


class QueueManager:
    def __init__(self, backend: QueueBackend, settings=None) -> None:
        self.backend = backend
        self.settings = settings or get_settings()

    @classmethod
    def from_settings(cls, settings=None) -> "QueueManager":
        settings = settings or get_settings()
        if settings.queue_backend == "redis":
            backend = RedisQueueBackend(settings.redis_url)
        else:
            backend = MemoryQueueBackend()
        return cls(backend, settings)

    async def start(self) -> None:
        await self.backend.start()

    async def stop(self) -> None:
        await self.backend.stop()

    async def enqueue(self, task: QueueTask) -> str:
        return await self.backend.enqueue(task)

    async def reserve(self, timeout: float | None = None) -> QueueLease | None:
        return await self.backend.reserve(timeout=timeout)

    async def ack(self, task_id: str) -> None:
        await self.backend.ack(task_id)

    async def nack(self, task_id: str, delay_seconds: int = 0) -> None:
        await self.backend.nack(task_id, delay_seconds=delay_seconds)

    async def cancel(self, task_id: str) -> bool:
        return await self.backend.cancel(task_id)

    def qsize(self) -> int:
        return self.backend.qsize()

    def snapshot(self) -> dict[str, int]:
        return self.backend.snapshot()

    @property
    def name(self) -> str:
        return self.backend.name

    @property
    def queue(self) -> "QueueManager":
        return self
