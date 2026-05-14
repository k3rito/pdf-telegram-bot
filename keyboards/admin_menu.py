from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def admin_menu() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("\ud83d\udcca \u0627\u0644\u0625\u062d\u0635\u0627\u0626\u064a\u0627\u062a", callback_data="admin_stats"),
            InlineKeyboardButton("\ud83d\udc65 \u0627\u0644\u0645\u0633\u062a\u062e\u062f\u0645\u0648\u0646", callback_data="admin_users"),
        ],
        [
            InlineKeyboardButton("\ud83d\udcc2 \u0627\u0644\u0639\u0645\u0644\u064a\u0627\u062a", callback_data="admin_tasks"),
            InlineKeyboardButton("\ud83d\udeab \u0627\u0644\u0645\u062d\u0638\u0648\u0631\u0648\u0646", callback_data="admin_banned"),
        ],
        [InlineKeyboardButton("\ud83d\udce2 \u0628\u062b \u0631\u0633\u0627\u0644\u0629", callback_data="admin_broadcast")],
        [InlineKeyboardButton("\ud83c\udfe0 \u0627\u0644\u0631\u062c\u0648\u0639", callback_data="main_menu")],
    ]

    return InlineKeyboardMarkup(rows)
