from __future__ import annotations

from pathlib import Path

SERVICE_TITLES = {
    "merge": "\ud83d\udcce \u062f\u0645\u062c",
    "split": "\u2702\ufe0f \u062a\u0642\u0633\u064a\u0645",
    "compress": "\ud83d\udddc\ufe0f \u0636\u063a\u0637",
    "extract_text": "\ud83d\udcdd \u0627\u0633\u062a\u062e\u0631\u0627\u062c \u0646\u0635",
    "extract_images": "\ud83d\uddbc\ufe0f \u0627\u0633\u062a\u062e\u0631\u0627\u062c \u0635\u0648\u0631",
    "images_to_pdf": "\ud83d\uddbc\ufe0f\u27a1\ufe0f\ud83d\udcc4 \u0635\u0648\u0631 \u0627\u0644\u0649 PDF",
    "pdf_to_word": "\ud83d\udcc4\u27a1\ufe0f\ud83d\udcdd PDF \u0627\u0644\u0649 Word",
    "pdf_to_excel": "\ud83d\udcca\u27a1\ufe0f PDF \u0627\u0644\u0649 Excel",
    "ocr": "\ud83d\udd0d OCR",
    "encrypt_pdf": "\ud83d\udd12 \u062d\u0645\u0627\u064a\u0629 PDF",
    "decrypt_pdf": "\ud83d\udd13 \u0627\u0632\u0627\u0644\u0629 \u062d\u0645\u0627\u064a\u0629",
    "rotate_pdf": "\ud83d\udd03 \u062a\u062f\u0648\u064a\u0631 \u0635\u0641\u062d\u0627\u062a",
    "watermark_pdf": "\ud83c\udf0a \u0639\u0644\u0627\u0645\u0629 \u0645\u0627\u0626\u064a\u0629",
    "sign_pdf": "\u270d\ufe0f \u062a\u0648\u0642\u064a\u0639",
    "pdf_to_images": "\ud83d\uddbc\ufe0f PDF \u0627\u0644\u0649 \u0635\u0648\u0631",
    "reorder_pages": "\ud83e\udde9 \u0627\u0639\u0627\u062f\u0629 \u062a\u0631\u062a\u064a\u0628",
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
