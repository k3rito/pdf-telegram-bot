from __future__ import annotations

from pathlib import Path
import fitz

from services.types import ServiceResult


def compress_pdf(path: Path, output_dir: Path) -> ServiceResult:
    output_path = output_dir / "compressed.pdf"
    original_size = path.stat().st_size

    doc = fitz.open(path)
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()

    compressed_size = output_path.stat().st_size
    saved = int((1 - (compressed_size / max(original_size, 1))) * 100)

    return ServiceResult(
        kind="document",
        path=output_path,
        filename="compressed.pdf",
        caption=(
            "تم الضغط.\n"
            f"الحجم الأصلي: {original_size // 1024} كيلوبايت\n"
            f"الحجم المضغوط: {compressed_size // 1024} كيلوبايت\n"
            f"التوفير: {saved}%"
        ),
    )
