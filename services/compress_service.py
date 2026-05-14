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
            "\u2705 \u062a\u0645 \u0627\u0644\u0636\u063a\u0637!\n"
            f"\ud83d\udce6 \u0627\u0644\u0623\u0635\u0644\u064a: {original_size // 1024} \u0643\u064a\u0644\u0648\n"
            f"\ud83d\udce6 \u0627\u0644\u0645\u0636\u063a\u0648\u0637: {compressed_size // 1024} \u0643\u064a\u0644\u0648\n"
            f"\ud83d\udcb0 \u0648\u0641\u0631\u0646\u0627: {saved}%"
        ),
    )
