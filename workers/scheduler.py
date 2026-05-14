from __future__ import annotations

import asyncio
from dataclasses import dataclass
from time import time


@dataclass(slots=True)
class ScheduledJob:
    name: str
    interval: int
    last_run: float = 0.0

    def due(self) -> bool:
        return (time() - self.last_run) >= self.interval


class Scheduler:
    def __init__(self) -> None:
        self.jobs: list[ScheduledJob] = []
        self._task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()

    def add_job(self, job: ScheduledJob) -> None:
        self.jobs.append(job)

    async def run(self, callback_registry: dict[str, callable]) -> None:
        self._stop_event.clear()
        while not self._stop_event.is_set():
            for job in self.jobs:
                if job.due() and job.name in callback_registry:
                    await callback_registry[job.name]()
                    job.last_run = time()
            await asyncio.sleep(1)

    def stop(self) -> None:
        self._stop_event.set()
