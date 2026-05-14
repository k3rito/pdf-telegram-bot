from __future__ import annotations

import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[int, deque[float]] = defaultdict(deque)

    def allow(self, user_id: int) -> tuple[bool, int]:
        now = time.monotonic()
        history = self._hits[user_id]

        while history and (now - history[0]) > self.window_seconds:
            history.popleft()

        if len(history) >= self.max_requests:
            retry_after = int(self.window_seconds - (now - history[0]))
            return False, max(retry_after, 1)

        history.append(now)
        return True, 0
