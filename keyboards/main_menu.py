from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu(is_admin: bool = False, ocr_enabled: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("دمج", callback_data="merge"),
            InlineKeyboardButton("تقسيم", callback_data="split"),
        ],
        [
            InlineKeyboardButton("ضغط", callback_data="compress"),
            InlineKeyboardButton("استخراج نص", callback_data="extract_text"),
        ],
        [
            InlineKeyboardButton("استخراج صور", callback_data="extract_images"),
            InlineKeyboardButton("صور إلى PDF", callback_data="images_to_pdf"),
        ],
        [
            InlineKeyboardButton("PDF إلى Word", callback_data="pdf_to_word"),
            InlineKeyboardButton("PDF إلى Excel", callback_data="pdf_to_excel"),
        ],
    ]

    if ocr_enabled:
        rows.append([InlineKeyboardButton("OCR", callback_data="ocr")])

    rows.extend(
        [
            [
                InlineKeyboardButton("أدوات إضافية", callback_data="more_menu"),
                InlineKeyboardButton("حسابي", callback_data="profile"),
            ],
            [
                InlineKeyboardButton("مساعدة", callback_data="help"),
                InlineKeyboardButton("إلغاء", callback_data="cancel"),
            ],
        ]
    )

    if is_admin:
        rows.append([InlineKeyboardButton("لوحة الإدارة", callback_data="admin_menu")])

    return InlineKeyboardMarkup(rows)


def more_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("حماية", callback_data="encrypt_pdf"),
            InlineKeyboardButton("إزالة حماية", callback_data="decrypt_pdf"),
        ],
        [
            InlineKeyboardButton("تدوير", callback_data="rotate_pdf"),
            InlineKeyboardButton("علامة مائية", callback_data="watermark_pdf"),
        ],
        [
            InlineKeyboardButton("توقيع", callback_data="sign_pdf"),
            InlineKeyboardButton("PDF إلى صور", callback_data="pdf_to_images"),
        ],
        [
            InlineKeyboardButton("إعادة ترتيب", callback_data="reorder_pages"),
            InlineKeyboardButton("القائمة الرئيسية", callback_data="main_menu"),
        ],
    ]

    if is_admin:
        rows.append([InlineKeyboardButton("لوحة الإدارة", callback_data="admin_menu")])

    return InlineKeyboardMarkup(rows)
