from __future__ import annotations

from pathlib import Path

from services.types import ServiceResult
from services.merge_service import merge_pdfs
from services.split_service import split_pdf
from services.compress_service import compress_pdf
from services.extract_service import extract_text_pdf, extract_images_pdf, ocr_pdf
from services.convert_service import images_to_pdf, pdf_to_word, pdf_to_excel, pdf_to_images
from services.security_service import (
    encrypt_pdf,
    decrypt_pdf,
    rotate_pdf,
    watermark_pdf,
    sign_pdf,
    reorder_pages,
)


def run_service(
    service: str,
    files: list[Path],
    params: dict,
    output_dir: Path,
    ocr_enabled: bool,
) -> ServiceResult:
    if service == "merge":
        return merge_pdfs(files, output_dir)
    if service == "split":
        return split_pdf(files[0], output_dir)
    if service == "compress":
        return compress_pdf(files[0], output_dir)
    if service == "extract_text":
        return extract_text_pdf(files[0], output_dir)
    if service == "extract_images":
        return extract_images_pdf(files[0], output_dir)
    if service == "images_to_pdf":
        return images_to_pdf(files, output_dir)
    if service == "pdf_to_word":
        return pdf_to_word(files[0], output_dir)
    if service == "pdf_to_excel":
        return pdf_to_excel(files[0], output_dir)
    if service == "pdf_to_images":
        return pdf_to_images(files[0], output_dir)
    if service == "ocr":
        if not ocr_enabled:
            raise RuntimeError("OCR is disabled")
        return ocr_pdf(files[0], output_dir)
    if service == "encrypt_pdf":
        return encrypt_pdf(files[0], params.get("password", ""), output_dir)
    if service == "decrypt_pdf":
        return decrypt_pdf(files[0], params.get("password", ""), output_dir)
    if service == "rotate_pdf":
        return rotate_pdf(files[0], params.get("degrees", 90), output_dir)
    if service == "watermark_pdf":
        return watermark_pdf(files[0], params.get("watermark", ""), output_dir)
    if service == "sign_pdf":
        return sign_pdf(files[0], params.get("signature", ""), output_dir)
    if service == "reorder_pages":
        return reorder_pages(files[0], params.get("order", []), output_dir)

    raise ValueError("Unknown service")
