from __future__ import annotations

from pathlib import Path

from security.validators.mime import is_safe_filename, sniff_pdf


class PDFValidationError(ValueError):
    pass


def validate_pdf_file(path: Path) -> None:
    if not path.exists():
        raise PDFValidationError("File does not exist")
    if path.stat().st_size <= 0:
        raise PDFValidationError("File is empty")
    if not sniff_pdf(path):
        raise PDFValidationError("Invalid PDF signature")


def validate_filename(filename: str) -> None:
    if not is_safe_filename(filename):
        raise PDFValidationError("Unsafe filename")
