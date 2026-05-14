from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def admin_menu() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("الإحصائيات", callback_data="admin_stats"),
            InlineKeyboardButton("المستخدمون", callback_data="admin_users"),
        ],
        [
            InlineKeyboardButton("العمليات", callback_data="admin_tasks"),
            InlineKeyboardButton("المحظورون", callback_data="admin_banned"),
        ],
        [InlineKeyboardButton("بث رسالة", callback_data="admin_broadcast")],
        [InlineKeyboardButton("الرجوع", callback_data="main_menu")],
    ]

    return InlineKeyboardMarkup(rows)
