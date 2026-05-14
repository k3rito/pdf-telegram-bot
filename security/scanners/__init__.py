from __future__ import annotations

from security.scanners.abstraction import Scanner, ScannerResult
from security.scanners.noop import NoopScanner

__all__ = ["Scanner", "ScannerResult", "NoopScanner"]
