from __future__ import annotations

from pathlib import Path
import fitz

from services.types import ServiceResult


def merge_pdfs(paths: list[Path], output_dir: Path) -> ServiceResult:
    output_path = output_dir / "merged.pdf"
    out_doc = fitz.open()
    for path in paths:
        doc = fitz.open(path)
        out_doc.insert_pdf(doc)
        doc.close()
    out_doc.save(output_path)
    out_doc.close()
    return ServiceResult(
        kind="document",
        path=output_path,
        filename="merged.pdf",
        caption="\u2705 \u062a\u0645 \u062f\u0645\u062c \u0627\u0644\u0645\u0644\u0641\u0627\u062a!",
    )
