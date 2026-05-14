from __future__ import annotations

from datetime import datetime
from pathlib import Path
import fitz
from pypdf import PdfReader, PdfWriter

from services.types import ServiceResult


def encrypt_pdf(path: Path, password: str, output_dir: Path) -> ServiceResult:
    output_path = output_dir / "protected.pdf"
    reader = PdfReader(str(path))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    with open(output_path, "wb") as output_file:
        writer.write(output_file)
    return ServiceResult(
        kind="document",
        path=output_path,
        filename="protected.pdf",
        caption="\u2705 \u062a\u0645 \u062d\u0645\u0627\u064a\u0629 PDF \u0628\u0643\u0644\u0645\u0629 \u0645\u0631\u0648\u0631!",
    )


def decrypt_pdf(path: Path, password: str, output_dir: Path) -> ServiceResult:
    output_path = output_dir / "unlocked.pdf"
    reader = PdfReader(str(path))
    if reader.is_encrypted:
        if reader.decrypt(password) == 0:
            raise ValueError("\u0643\u0644\u0645\u0629 \u0627\u0644\u0645\u0631\u0648\u0631 \u063a\u064a\u0631 \u0635\u062d\u064a\u062d\u0629.")
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with open(output_path, "wb") as output_file:
        writer.write(output_file)
    return ServiceResult(
        kind="document",
        path=output_path,
        filename="unlocked.pdf",
        caption="\u2705 \u062a\u0645 \u0625\u0632\u0627\u0644\u0629 \u0627\u0644\u062d\u0645\u0627\u064a\u0629!",
    )


def rotate_pdf(path: Path, degrees: int, output_dir: Path) -> ServiceResult:
    output_path = output_dir / "rotated.pdf"
    reader = PdfReader(str(path))
    writer = PdfWriter()
    for page in reader.pages:
        if hasattr(page, "rotate_clockwise"):
            page.rotate_clockwise(degrees)
        else:
            page.rotate(degrees)
        writer.add_page(page)
    with open(output_path, "wb") as output_file:
        writer.write(output_file)
    return ServiceResult(
        kind="document",
        path=output_path,
        filename="rotated.pdf",
        caption=f"\u2705 \u062a\u0645 \u062a\u062f\u0648\u064a\u0631 \u0627\u0644\u0635\u0641\u062d\u0627\u062a {degrees}\u00b0!",
    )


def watermark_pdf(path: Path, text: str, output_dir: Path) -> ServiceResult:
    output_path = output_dir / "watermarked.pdf"
    doc = fitz.open(path)
    for page in doc:
        rect = page.rect
        page.insert_text(
            fitz.Point(rect.width * 0.15, rect.height * 0.5),
            text,
            fontsize=48,
            rotate=45,
            color=(0.7, 0.7, 0.7),
            fill_opacity=0.2,
        )
    doc.save(output_path)
    doc.close()
    return ServiceResult(
        kind="document",
        path=output_path,
        filename="watermarked.pdf",
        caption="\u2705 \u062a\u0645 \u0625\u0636\u0627\u0641\u0629 \u0627\u0644\u0639\u0644\u0627\u0645\u0629 \u0627\u0644\u0645\u0627\u0626\u064a\u0629!",
    )


def sign_pdf(path: Path, signature_text: str, output_dir: Path) -> ServiceResult:
    output_path = output_dir / "signed.pdf"
    doc = fitz.open(path)
    stamp = f"{signature_text} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    for page in doc:
        rect = page.rect
        position = fitz.Point(rect.width * 0.65, rect.height * 0.92)
        page.insert_text(position, stamp, fontsize=12, color=(0.1, 0.1, 0.1))
    doc.save(output_path)
    doc.close()
    return ServiceResult(
        kind="document",
        path=output_path,
        filename="signed.pdf",
        caption="\u2705 \u062a\u0645 \u062a\u0648\u0642\u064a\u0639 PDF!",
    )


def reorder_pages(path: Path, order: list[int], output_dir: Path) -> ServiceResult:
    output_path = output_dir / "reordered.pdf"
    doc = fitz.open(path)
    new_doc = fitz.open()
    for page_number in order:
        new_doc.insert_pdf(doc, from_page=page_number - 1, to_page=page_number - 1)
    new_doc.save(output_path)
    new_doc.close()
    doc.close()
    return ServiceResult(
        kind="document",
        path=output_path,
        filename="reordered.pdf",
        caption="\u2705 \u062a\u0645 \u0625\u0639\u0627\u062f\u0629 \u062a\u0631\u062a\u064a\u0628 \u0627\u0644\u0635\u0641\u062d\u0627\u062a!",
    )
