from __future__ import annotations

import re
from typing import List


def is_pdf(filename: str, mime_type: str | None) -> bool:
    return filename.lower().endswith(".pdf") or (mime_type == "application/pdf")


def is_image(filename: str, mime_type: str | None) -> bool:
    if mime_type and mime_type.startswith("image/"):
        return True
    return filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp"))


def validate_file_size(size: int, max_size: int) -> bool:
    return size <= max_size


def parse_rotate(value: str) -> int | None:
    try:
        deg = int(value.strip())
    except ValueError:
        return None
    if deg in (90, 180, 270):
        return deg
    return None


def parse_page_order(order_text: str, page_count: int) -> List[int] | None:
    parts = re.split(r"[ ,]+", order_text.strip())
    if not parts:
        return None
    order = []
    for part in parts:
        if not part.isdigit():
            return None
        num = int(part)
        if num < 1 or num > page_count:
            return None
        order.append(num)
    if len(order) != page_count:
        return None
    return order


def validate_password(value: str) -> bool:
    return len(value.strip()) >= 4
