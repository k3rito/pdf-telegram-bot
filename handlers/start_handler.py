from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import DEFAULT_LANG, PARSE_MODE
from core.middleware import guard
from keyboards.main_menu import main_menu
from utils.i18n import LANG, t


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user = update.effective_user
    chat_id = update.effective_chat.id
    session_manager = context.application.bot_data["session_manager"]
    session_manager.clear(chat_id, user.id)

    is_admin = user.id in context.application.bot_data["admin_ids"]
    ocr_enabled = context.application.bot_data.get("ocr_enabled", False)

    lang = context.user_data.get("lang", DEFAULT_LANG)
    await update.message.reply_text(
        t("welcome", lang),
        reply_markup=main_menu(is_admin=is_admin, ocr_enabled=ocr_enabled),
        parse_mode=PARSE_MODE,
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user = update.effective_user
    chat_id = update.effective_chat.id
    session_manager = context.application.bot_data["session_manager"]
    session_manager.clear(chat_id, user.id)

    is_admin = user.id in context.application.bot_data["admin_ids"]
    ocr_enabled = context.application.bot_data.get("ocr_enabled", False)
    lang = context.user_data.get("lang", DEFAULT_LANG)
    await update.message.reply_text(
        t("cancel", lang),
        reply_markup=main_menu(is_admin=is_admin, ocr_enabled=ocr_enabled),
        parse_mode=PARSE_MODE,
    )


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    if not context.args:
        await update.message.reply_text(t("lang_help"))
        return

    lang = context.args[0].lower()
    if lang not in LANG:
        await update.message.reply_text(t("lang_help"))
        return

    context.user_data["lang"] = lang
    await update.message.reply_text(t("lang_set", lang).format(lang=lang))
