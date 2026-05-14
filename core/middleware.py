from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


def _get_reply_target(update: Update):
    return update.message or update.callback_query and update.callback_query.message


async def guard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if not user:
        return False

    db = context.application.bot_data.get("db")
    if db:
        await db.ensure_user(user.id, user.username or "")
        if await db.is_banned(user.id):
            target = _get_reply_target(update)
            if target:
                await target.reply_text("\u26d4 \u062d\u0633\u0627\u0628\u0643 \u0645\u062d\u0638\u0648\u0631 \u062d\u0627\u0644\u064a\u0627.")
            return False

    limiter = context.application.bot_data.get("rate_limiter")
    if limiter:
        allowed, retry_after = limiter.allow(user.id)
        if not allowed:
            target = _get_reply_target(update)
            if target:
                await target.reply_text(
                    f"\u23f3 \u062a\u0645 \u062a\u062c\u0627\u0648\u0632 \u062d\u062f \u0627\u0644\u0627\u0633\u062a\u062e\u062f\u0627\u0645. \u062d\u0627\u0648\u0644 \u0645\u0631\u0629 \u0627\u062e\u0631\u0649 \u0628\u0639\u062f {retry_after} \u062b\u0627\u0646\u064a\u0629."
                )
            return False

    return True
