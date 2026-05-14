from __future__ import annotations

from pathlib import Path

from security.scanners.abstraction import Scanner


class NoopScanner(Scanner):
    async def scan(self, path: Path) -> bool:
        _ = path
        return True
