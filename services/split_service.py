from __future__ import annotations

import zipfile
from pathlib import Path
from typing import TYPE_CHECKING
import importlib

if TYPE_CHECKING:
    import fitz  # type: ignore

try:
    fitz = importlib.import_module("fitz")
except Exception:
    fitz = None  # type: ignore

from services.types import ServiceResult


def split_pdf(path: Path, output_dir: Path) -> ServiceResult:
    if fitz is None:
        return ServiceResult(kind="error", text="PyMuPDF (fitz) is not installed in this environment.")

    doc = None
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        doc = fitz.open(path)
        page_count = doc.page_count

        if page_count == 0:
            doc.close()
            return ServiceResult(kind="error", text="No pages found in the PDF.")

        zip_path = output_dir / "pages.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for index in range(page_count):
                single = fitz.open()
                single.insert_pdf(doc, from_page=index, to_page=index)
                page_path = output_dir / f"page_{index + 1}.pdf"
                single.save(page_path)
                single.close()
                zf.write(page_path, arcname=page_path.name)
                page_path.unlink(missing_ok=True)
        doc.close()
        return ServiceResult(
            kind="document",
            path=zip_path,
            filename="pages.zip",
            caption=f"\u2705 \u062a\u0645 \u062a\u0642\u0633\u064a\u0645 PDF \u0625\u0644\u0649 {page_count} \u0635\u0641\u062d\u0629!",
        )
    except Exception as e:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass
        return ServiceResult(kind="error", text=str(e))
