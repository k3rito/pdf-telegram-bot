from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ServiceResult:
    kind: str
    path: Path | None = None
    filename: str | None = None
    caption: str | None = None
    text: str | None = None
