from __future__ import annotations

from services.queue.manager import QueueManager


class LegacyQueueManager:
    def __init__(self, task_manager) -> None:
        self.task_manager = task_manager

    async def enqueue(self, task) -> str:
        return await self.task_manager.enqueue(task)


__all__ = ["QueueManager", "LegacyQueueManager"]
