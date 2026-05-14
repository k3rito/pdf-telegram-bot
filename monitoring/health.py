from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class HealthStatus:
    ok: bool
    details: dict[str, Any]


def liveness() -> HealthStatus:
    return HealthStatus(ok=True, details={"status": "alive"})


def readiness(dependencies: dict[str, bool]) -> HealthStatus:
    ok = all(dependencies.values())
    return HealthStatus(ok=ok, details={"dependencies": dependencies})
