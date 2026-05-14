from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RetentionPolicy:
    keep_days: int = 30

    def should_delete(self, age_days: int) -> bool:
        return age_days > self.keep_days
