from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class Scanner(Protocol):
    async def scan(self, path: Path) -> bool:
        ...


@dataclass(slots=True)
class ScannerResult:
    scanner: str
    clean: bool
    details: str = ""
