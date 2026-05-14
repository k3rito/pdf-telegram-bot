from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AutoScalerDecision:
    desired_workers: int
    reason: str


class AutoScaler:
    def __init__(self, min_workers: int = 1, max_workers: int = 8, scale_up_threshold: int = 10, scale_down_threshold: int = 2) -> None:
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold

    def decide(self, queued: int, active: int, current_workers: int) -> AutoScalerDecision:
        load = queued + active
        if load >= self.scale_up_threshold:
            return AutoScalerDecision(desired_workers=min(self.max_workers, current_workers + 1), reason="scale_up")
        if load <= self.scale_down_threshold:
            return AutoScalerDecision(desired_workers=max(self.min_workers, current_workers - 1), reason="scale_down")
        return AutoScalerDecision(desired_workers=current_workers, reason="steady")
