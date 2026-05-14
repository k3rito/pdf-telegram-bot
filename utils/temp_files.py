from __future__ import annotations

import shutil
import uuid
from pathlib import Path


def create_temp_dir(root: Path, chat_id: int, user_id: int) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    session_id = uuid.uuid4().hex
    temp_dir = root / f"session_{chat_id}_{user_id}_{session_id}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def build_temp_path(temp_dir: Path, filename: str) -> Path:
    return temp_dir / filename


def cleanup_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
