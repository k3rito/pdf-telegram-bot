from __future__ import annotations

import asyncio
import zipfile
from pathlib import Path
import fitz

from services.ocr import OCREngine, OCRPipeline
from services.types import ServiceResult


def extract_text_pdf(path: Path, output_dir: Path) -> ServiceResult:
    doc = fitz.open(path)
    parts = []
    for index in range(doc.page_count):
        page = doc.load_page(index)
        text = page.get_text("text") or ""
        parts.append(f"\u2500\u2500 \u0635\u0641\u062d\u0629 {index + 1} \u2500\u2500\n{text.strip()}\n")
    doc.close()

    full_text = "\n".join(parts).strip() or "\u0644\u0645 \u064a\u062a\u0645 \u0627\u0644\u0639\u062b\u0648\u0631 \u0639\u0644\u0649 \u0646\u0635\u0648\u0635."

    if len(full_text) > 4000:
        txt_path = output_dir / "extracted_text.txt"
        txt_path.write_text(full_text, encoding="utf-8")
        return ServiceResult(
            kind="document",
            path=txt_path,
            filename="extracted_text.txt",
            caption="\u2705 \u062a\u0645 \u0627\u0633\u062a\u062e\u0631\u0627\u062c \u0627\u0644\u0646\u0635\u0648\u0635!",
        )

    return ServiceResult(kind="text", text=full_text)


def extract_images_pdf(path: Path, output_dir: Path) -> ServiceResult:
    doc = fitz.open(path)
    zip_path = output_dir / "images.zip"
    image_count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            for img_index, img in enumerate(page.get_images(full=True), 1):
                xref = img[0]
                base = doc.extract_image(xref)
                ext = base.get("ext", "png")
                image_bytes = base.get("image")
                image_count += 1
                image_name = f"image_{page_index + 1}_{img_index}.{ext}"
                zf.writestr(image_name, image_bytes)
    doc.close()

    if image_count == 0:
        return ServiceResult(kind="text", text="\u26a0\ufe0f \u0644\u0645 \u064a\u062a\u0645 \u0627\u0644\u0639\u062b\u0648\u0631 \u0639\u0644\u0649 \u0635\u0648\u0631 \u0641\u064a \u0647\u0630\u0627 \u0627\u0644\u0645\u0644\u0641.")

    return ServiceResult(
        kind="document",
        path=zip_path,
        filename="images.zip",
        caption=f"\u2705 \u062a\u0645 \u0627\u0633\u062a\u062e\u0631\u0627\u062c {image_count} \u0635\u0648\u0631\u0629!",
    )


def ocr_pdf(path: Path, output_dir: Path) -> ServiceResult:
    try:
        from PIL import Image
    except Exception as exc:
        raise RuntimeError("OCR dependencies are not available") from exc

    doc = fitz.open(path)
    pages: list[tuple[int, Image.Image]] = []
    for index in range(doc.page_count):
        page = doc.load_page(index)
        pix = page.get_pixmap(dpi=300)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pages.append((index + 1, image))
    doc.close()

    try:
        engine = OCREngine(languages="ara+eng")
        pipeline = OCRPipeline(engine=engine, max_concurrency=2)
        document = asyncio.run(pipeline.run(pages))
        full_text = document.combined_text or "\u0644\u0645 \u064a\u062a\u0645 \u0627\u0644\u0639\u062b\u0648\u0631 \u0639\u0644\u0649 \u0646\u0635 \u0645\u0631\u0626\u064a."
        confidence = document.average_confidence
    except Exception as exc:
        raise RuntimeError("OCR processing failed") from exc
    confidence = float(confidence)

    txt_path = output_dir / "ocr_text.txt"
    txt_path.write_text(full_text, encoding="utf-8")
    return ServiceResult(
        kind="document",
        path=txt_path,
        filename="ocr_text.txt",
        caption=f"\u2705 \u062a\u0645 OCR \u0628\u0646\u062c\u0627\u062d! (confidence={confidence:.2f})",
    )
