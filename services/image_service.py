from __future__ import annotations

from pathlib import Path

from services.convert_service import images_to_pdf, pdf_to_images
from services.types import ServiceResult


def images_to_pdf_service(paths: list[Path], output_dir: Path) -> ServiceResult:
    return images_to_pdf(paths, output_dir)


def pdf_to_images_service(path: Path, output_dir: Path) -> ServiceResult:
    return pdf_to_images(path, output_dir)
