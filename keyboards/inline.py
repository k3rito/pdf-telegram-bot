from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def upload_actions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("\ud83d\ude80 \u0628\u062f\u0621 \u0627\u0644\u0645\u0639\u0627\u0644\u062c\u0629", callback_data="process_now")],
            [
                InlineKeyboardButton("\u2795 \u0625\u0636\u0627\u0641\u0629 \u0645\u0644\u0641\u0627\u062a", callback_data="continue_upload"),
                InlineKeyboardButton("\ud83d\uddd1 \u062d\u0630\u0641 \u0622\u062e\u0631 \u0645\u0644\u0641", callback_data="remove_last"),
            ],
            [InlineKeyboardButton("\u274c \u0625\u0644\u063a\u0627\u0621", callback_data="cancel")],
        ]
    )


def single_actions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("\ud83d\ude80 \u0628\u062f\u0621 \u0627\u0644\u0645\u0639\u0627\u0644\u062c\u0629", callback_data="process_now")],
            [InlineKeyboardButton("\u274c \u0625\u0644\u063a\u0627\u0621", callback_data="cancel")],
        ]
    )


def rotate_actions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("90\u00b0", callback_data="rotate_90"),
                InlineKeyboardButton("180\u00b0", callback_data="rotate_180"),
                InlineKeyboardButton("270\u00b0", callback_data="rotate_270"),
            ],
            [InlineKeyboardButton("\u274c \u0625\u0644\u063a\u0627\u0621", callback_data="cancel")],
        ]
    )
