from __future__ import annotations

from pathlib import Path


def sniff_pdf(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return handle.read(5) == b"%PDF-"
    except Exception:
        return False


def is_safe_filename(filename: str) -> bool:
    return bool(filename) and "/" not in filename and "\\" not in filename and ".." not in filename
