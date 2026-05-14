from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from time import time
from typing import Any


class EventType(StrEnum):
    task_created = "task_created"
    task_updated = "task_updated"
    task_failed = "task_failed"
    analytics_tick = "analytics_tick"
    admin_notification = "admin_notification"
    broadcast_requested = "broadcast_requested"


@dataclass(slots=True)
class Event:
    type: EventType
    payload: dict[str, Any] = field(default_factory=dict)
    trace_id: str | None = None
    correlation_id: str | None = None
    created_at: float = field(default_factory=time)
