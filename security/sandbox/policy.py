from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class SandboxPolicy:
    max_file_size: int
    max_files: int
    max_total_size: int
    allowed_suffixes: set[str] = field(default_factory=lambda: {".pdf", ".png", ".jpg", ".jpeg"})

    def validate(self, files: list[Path]) -> None:
        if len(files) > self.max_files:
            raise ValueError("Too many files")
        total = 0
        for file_path in files:
            if file_path.suffix.lower() not in self.allowed_suffixes:
                raise ValueError(f"Disallowed file type: {file_path.suffix}")
            if file_path.stat().st_size > self.max_file_size:
                raise ValueError("File too large")
            total += file_path.stat().st_size
        if total > self.max_total_size:
            raise ValueError("Total size too large")
