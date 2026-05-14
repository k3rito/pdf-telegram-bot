from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class UserProfile:
    total_tasks: int
    total_files: int
    favorite_service: str | None
