from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from time import time

from services.queue.base import QueueLease


@dataclass(slots=True)
class WorkerState:
    worker_id: str
    last_heartbeat: float = field(default_factory=time)
    active_task_id: str | None = None
    lease_token: str | None = None

    def beat(self) -> None:
        self.last_heartbeat = time()


class Worker:
    def __init__(self, worker_id: str, lease_timeout: int = 60) -> None:
        self.state = WorkerState(worker_id=worker_id)
        self.lease_timeout = lease_timeout
        self._stop_event = asyncio.Event()

    async def run(self, queue_manager, handler) -> None:
        while not self._stop_event.is_set():
            lease = await queue_manager.reserve(timeout=1)
            if lease is None:
                await asyncio.sleep(0.1)
                continue
            self.state.active_task_id = lease.task.id
            self.state.lease_token = lease.lease_token
            self.state.beat()
            try:
                await handler(lease)
                await queue_manager.ack(lease.task.id)
            except Exception:
                await queue_manager.nack(lease.task.id, delay_seconds=2)
            finally:
                self.state.active_task_id = None
                self.state.lease_token = None
                self.state.beat()

    def stop(self) -> None:
        self._stop_event.set()
