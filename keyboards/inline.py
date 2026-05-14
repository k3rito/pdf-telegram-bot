from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def upload_actions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("بدء المعالجة", callback_data="process_now")],
            [
                InlineKeyboardButton("إضافة ملفات", callback_data="continue_upload"),
                InlineKeyboardButton("حذف آخر ملف", callback_data="remove_last"),
            ],
            [InlineKeyboardButton("إلغاء", callback_data="cancel")],
        ]
    )


def single_actions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("بدء المعالجة", callback_data="process_now")],
            [InlineKeyboardButton("إلغاء", callback_data="cancel")],
        ]
    )


def rotate_actions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("90°", callback_data="rotate_90"),
                InlineKeyboardButton("180°", callback_data="rotate_180"),
                InlineKeyboardButton("270°", callback_data="rotate_270"),
            ],
            [InlineKeyboardButton("إلغاء", callback_data="cancel")],
        ]
    )
