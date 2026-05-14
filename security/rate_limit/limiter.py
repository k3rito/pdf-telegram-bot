from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class RateLimitDecision:
    allowed: bool
    retry_after: int = 0
    abuse_score: float = 0.0


@dataclass(slots=True)
class AdaptiveRateLimiter:
    limit: int
    window_seconds: int
    buckets: dict[int, list[float]] = field(default_factory=dict)

    def allow(self, user_id: int) -> RateLimitDecision:
        now = time()
        bucket = [timestamp for timestamp in self.buckets.get(user_id, []) if (now - timestamp) <= self.window_seconds]
        bucket.append(now)
        self.buckets[user_id] = bucket
        if len(bucket) <= self.limit:
            return RateLimitDecision(allowed=True, abuse_score=min(1.0, len(bucket) / max(self.limit, 1)))
        retry_after = int(self.window_seconds - (now - bucket[0]))
        return RateLimitDecision(allowed=False, retry_after=max(1, retry_after), abuse_score=1.0)
