from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass(slots=True)
class DailySummary:
    day: date
    command_usage: dict[str, int] = field(default_factory=dict)
    processing_durations: dict[str, float] = field(default_factory=dict)
    ocr_success_rate: float = 0.0
    compression_ratios: dict[str, float] = field(default_factory=dict)
    active_users: int = 0
    peak_usage_window: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
