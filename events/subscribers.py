from __future__ import annotations

from events.models import Event, EventType


async def log_event(event: Event) -> None:
    _ = event


async def notify_admin(event: Event) -> None:
    _ = event
    _ = EventType.admin_notification
