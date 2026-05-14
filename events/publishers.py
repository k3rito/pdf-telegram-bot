from __future__ import annotations

from events.bus import EventBus
from events.models import Event, EventType


async def publish_task_created(bus: EventBus, payload: dict) -> None:
    await bus.publish(Event(type=EventType.task_created, payload=payload))


async def publish_task_failed(bus: EventBus, payload: dict) -> None:
    await bus.publish(Event(type=EventType.task_failed, payload=payload))
