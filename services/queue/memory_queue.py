from __future__ import annotations

import asyncio
import heapq
import itertools
import uuid
from collections import defaultdict
from dataclasses import replace
from time import time

from services.queue.base import QueueBackend, QueueLease, QueueStatus, QueueTask


class MemoryQueueBackend(QueueBackend):
    name = "memory"

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._condition = asyncio.Condition(self._lock)
        self._sequence = itertools.count()
        self._scheduled: list[tuple[float, int, int, str, QueueTask]] = []
        self._pending: dict[str, QueueTask] = {}
        self._leased: dict[str, QueueLease] = {}
        self._canceled: set[str] = set()
        self._failed_attempts = defaultdict(int)
        self._stopped = False

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        async with self._condition:
            self._stopped = True
            self._condition.notify_all()

    async def enqueue(self, task: QueueTask) -> str:
        async with self._condition:
            if task.id in self._canceled:
                return task.id
            scheduled_task = replace(task)
            priority_score = -int(scheduled_task.priority)
            heapq.heappush(
                self._scheduled,
                (float(scheduled_task.run_at), priority_score, next(self._sequence), scheduled_task.id, scheduled_task),
            )
            self._pending[scheduled_task.id] = scheduled_task
            self._condition.notify_all()
            return scheduled_task.id

    async def reserve(self, timeout: float | None = None) -> QueueLease | None:
        deadline = None if timeout is None else time() + timeout
        async with self._condition:
            while True:
                if self._stopped:
                    return None

                now = time()
                while self._scheduled and self._scheduled[0][0] <= now:
                    _, _, _, task_id, task = heapq.heappop(self._scheduled)
                    if task_id in self._canceled:
                        self._pending.pop(task_id, None)
                        continue
                    lease = QueueLease(task=task, backend_name=self.name, lease_token=uuid.uuid4().hex)
                    self._leased[task_id] = lease
                    self._pending.pop(task_id, None)
                    return lease

                wait_for = None
                if self._scheduled:
                    wait_for = max(0.0, self._scheduled[0][0] - now)
                if deadline is not None:
                    remaining = max(0.0, deadline - now)
                    wait_for = remaining if wait_for is None else min(wait_for, remaining)
                    if remaining <= 0:
                        return None

                if wait_for is None:
                    await self._condition.wait()
                else:
                    try:
                        await asyncio.wait_for(self._condition.wait(), timeout=wait_for)
                    except asyncio.TimeoutError:
                        continue

    async def ack(self, task_id: str) -> None:
        async with self._condition:
            self._leased.pop(task_id, None)
            self._pending.pop(task_id, None)

    async def nack(self, task_id: str, delay_seconds: int = 0) -> None:
        async with self._condition:
            lease = self._leased.pop(task_id, None)
            if not lease:
                return
            self._failed_attempts[task_id] += 1
            task = replace(lease.task, run_at=time() + max(0, delay_seconds))
            heapq.heappush(
                self._scheduled,
                (task.run_at, -int(task.priority), next(self._sequence), task.id, task),
            )
            self._pending[task.id] = task
            self._condition.notify_all()

    async def cancel(self, task_id: str) -> bool:
        async with self._condition:
            self._canceled.add(task_id)
            removed = self._pending.pop(task_id, None) is not None
            self._leased.pop(task_id, None)
            self._condition.notify_all()
            return removed

    def qsize(self) -> int:
        return len(self._pending)

    def snapshot(self) -> dict[str, int]:
        return {
            "pending": len(self._pending),
            "leased": len(self._leased),
            "canceled": len(self._canceled),
            "failed": sum(self._failed_attempts.values()),
        }
