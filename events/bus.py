from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from events.models import Event, EventType

Subscriber = Callable[[Event], Awaitable[None]]


@dataclass(slots=True)
class EventBus:
    subscribers: dict[EventType, list[Subscriber]] = field(default_factory=lambda: defaultdict(list))
    _queue: asyncio.Queue[Event] = field(default_factory=asyncio.Queue)
    _pump_task: asyncio.Task[None] | None = None
    _stop_event: asyncio.Event = field(default_factory=asyncio.Event)

    async def start(self) -> None:
        self._stop_event.clear()
        if self._pump_task is None or self._pump_task.done():
            self._pump_task = asyncio.create_task(self._pump())

    async def stop(self) -> None:
        self._stop_event.set()
        if self._pump_task:
            self._pump_task.cancel()
            try:
                await self._pump_task
            except Exception:
                pass
            self._pump_task = None

    async def publish(self, event: Event) -> None:
        await self._queue.put(event)

    def subscribe(self, event_type: EventType, handler: Subscriber) -> None:
        self.subscribers[event_type].append(handler)

    async def _pump(self) -> None:
        while not self._stop_event.is_set():
            try:
                event = await self._queue.get()
                await self._dispatch(event)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(0.1)

    async def _dispatch(self, event: Event) -> None:
        for handler in self.subscribers.get(event.type, []):
            await handler(event)
