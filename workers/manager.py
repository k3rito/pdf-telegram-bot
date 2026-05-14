from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from workers.worker import Worker


@dataclass(slots=True)
class WorkerRegistry:
    workers: list[Worker] = field(default_factory=list)

    def snapshot(self) -> list[dict[str, str | float | None]]:
        return [
            {
                "worker_id": worker.state.worker_id,
                "last_heartbeat": worker.state.last_heartbeat,
                "active_task_id": worker.state.active_task_id,
            }
            for worker in self.workers
        ]


class WorkerManager:
    def __init__(self, worker_count: int) -> None:
        self.worker_count = worker_count
        self.registry = WorkerRegistry()
        self._tasks: list[asyncio.Task[None]] = []

    def build_workers(self) -> list[Worker]:
        if self.registry.workers:
            return self.registry.workers
        self.registry.workers = [Worker(worker_id=f"worker-{index + 1}") for index in range(self.worker_count)]
        return self.registry.workers

    async def start(self, queue_manager, handler) -> None:
        for worker in self.build_workers():
            self._tasks.append(asyncio.create_task(worker.run(queue_manager, handler)))

    async def stop(self) -> None:
        for worker in self.registry.workers:
            worker.stop()
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()
