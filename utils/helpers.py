from __future__ import annotations

from pathlib import Path

SERVICE_TITLES = {
    "merge": "دمج",
    "split": "تقسيم",
    "compress": "ضغط",
    "extract_text": "استخراج نص",
    "extract_images": "استخراج صور",
    "images_to_pdf": "صور إلى PDF",
    "pdf_to_word": "PDF إلى Word",
    "pdf_to_excel": "PDF إلى Excel",
    "ocr": "OCR",
    "encrypt_pdf": "حماية PDF",
    "decrypt_pdf": "إزالة حماية",
    "rotate_pdf": "تدوير صفحات",
    "watermark_pdf": "علامة مائية",
    "sign_pdf": "توقيع",
    "pdf_to_images": "PDF إلى صور",
    "reorder_pages": "إعادة ترتيب",
}


def format_size(value: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(value)
    for unit in units:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def build_file_list(files: list[dict]) -> str:
    lines = []
    for idx, item in enumerate(files, 1):
        name = item.get("name", f"file_{idx}")
        size = item.get("size", 0)
        lines.append(f"{idx}. {name} ({format_size(size)})")
    return "\n".join(lines) if lines else "-"


def safe_filename(name: str) -> str:
    cleaned = name.replace("/", "_").replace("\\", "_")
    return cleaned or "file"


def service_title(service: str) -> str:
    return SERVICE_TITLES.get(service, service)
