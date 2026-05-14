from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu(is_admin: bool = False, ocr_enabled: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("\ud83d\udcce \u062f\u0645\u062c", callback_data="merge"),
            InlineKeyboardButton("\u2702\ufe0f \u062a\u0642\u0633\u064a\u0645", callback_data="split"),
        ],
        [
            InlineKeyboardButton("\ud83d\udddc\ufe0f \u0636\u063a\u0637", callback_data="compress"),
            InlineKeyboardButton("\ud83d\udcdd \u0627\u0633\u062a\u062e\u0631\u0627\u062c \u0646\u0635", callback_data="extract_text"),
        ],
        [
            InlineKeyboardButton("\ud83d\uddbc\ufe0f \u0627\u0633\u062a\u062e\u0631\u0627\u062c \u0635\u0648\u0631", callback_data="extract_images"),
            InlineKeyboardButton("\ud83d\uddbc\ufe0f\u27a1\ufe0f\ud83d\udcc4 \u0635\u0648\u0631 \u0627\u0644\u0649 PDF", callback_data="images_to_pdf"),
        ],
        [
            InlineKeyboardButton("\ud83d\udcc4\u27a1\ufe0f Word", callback_data="pdf_to_word"),
            InlineKeyboardButton("\ud83d\udcca\u27a1\ufe0f Excel", callback_data="pdf_to_excel"),
        ],
    ]

    if ocr_enabled:
        rows.append([InlineKeyboardButton("\ud83d\udd0d OCR", callback_data="ocr")])

    rows.extend(
        [
            [
                InlineKeyboardButton("\ud83e\udde9 \u0623\u062f\u0648\u0627\u062a \u0625\u0636\u0627\u0641\u064a\u0629", callback_data="more_menu"),
                InlineKeyboardButton("\ud83d\udc64 \u062d\u0633\u0627\u0628\u064a", callback_data="profile"),
            ],
            [
                InlineKeyboardButton("\u2139\ufe0f \u0645\u0633\u0627\u0639\u062f\u0629", callback_data="help"),
                InlineKeyboardButton("\u274c \u0625\u0644\u063a\u0627\u0621", callback_data="cancel"),
            ],
        ]
    )

    if is_admin:
        rows.append([InlineKeyboardButton("\ud83d\udee1 \u0644\u0648\u062d\u0629 \u0627\u0644\u0625\u062f\u0627\u0631\u0629", callback_data="admin_menu")])

    return InlineKeyboardMarkup(rows)


def more_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("\ud83d\udd12 \u062d\u0645\u0627\u064a\u0629", callback_data="encrypt_pdf"),
            InlineKeyboardButton("\ud83d\udd13 \u0625\u0632\u0627\u0644\u0629 \u062d\u0645\u0627\u064a\u0629", callback_data="decrypt_pdf"),
        ],
        [
            InlineKeyboardButton("\ud83d\udd03 \u062a\u062f\u0648\u064a\u0631", callback_data="rotate_pdf"),
            InlineKeyboardButton("\ud83c\udf0a \u0639\u0644\u0627\u0645\u0629 \u0645\u0627\u0626\u064a\u0629", callback_data="watermark_pdf"),
        ],
        [
            InlineKeyboardButton("\u270d\ufe0f \u062a\u0648\u0642\u064a\u0639", callback_data="sign_pdf"),
            InlineKeyboardButton("\ud83d\uddbc\ufe0f PDF \u0627\u0644\u0649 \u0635\u0648\u0631", callback_data="pdf_to_images"),
        ],
        [
            InlineKeyboardButton("\ud83e\udde9 \u0625\u0639\u0627\u062f\u0629 \u062a\u0631\u062a\u064a\u0628", callback_data="reorder_pages"),
            InlineKeyboardButton("\ud83c\udfe0 \u0627\u0644\u0642\u0627\u0626\u0645\u0629 \u0627\u0644\u0631\u0626\u064a\u0633\u064a\u0629", callback_data="main_menu"),
        ],
    ]

    if is_admin:
        rows.append([InlineKeyboardButton("\ud83d\udee1 \u0644\u0648\u062d\u0629 \u0627\u0644\u0625\u062f\u0627\u0631\u0629", callback_data="admin_menu")])

    return InlineKeyboardMarkup(rows)
