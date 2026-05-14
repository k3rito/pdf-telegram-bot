from __future__ import annotations

from dataclasses import dataclass
from time import time


@dataclass(slots=True)
class Heartbeat:
    worker_id: str
    last_seen: float = 0.0

    def ping(self) -> None:
        self.last_seen = time()

    def is_stale(self, timeout: int) -> bool:
        return (time() - self.last_seen) > timeout
