from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger = context.application.bot_data.get("logger")
    if logger:
        logger.exception("Unhandled error", exc_info=context.error)

    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("\u26a0\ufe0f \u062d\u062f\u062b \u062e\u0637\u0623 \u063a\u064a\u0631 \u0645\u062a\u0648\u0642\u0639. \u062d\u0627\u0648\u0644 \u0645\u0631\u0629 \u0623\u062e\u0631\u0649.")
        except Exception:
            pass
