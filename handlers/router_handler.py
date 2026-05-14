from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from core.command_router import command_router
from handlers.pdf_handler import handle_document, handle_photo, handle_text_input


async def handle_incoming_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return

    session_manager = context.application.bot_data.get("session_manager")
    session = session_manager.get(chat.id, user.id) if session_manager else None

    if message.text and message.text.strip().startswith("/"):
        return

    if message.text and await command_router.route(update, context):
        return

    if message.document:
        if session:
            await handle_document(update, context)
        return

    if message.photo:
        if session:
            await handle_photo(update, context)
        return

    if message.text and (context.user_data.get("broadcast_pending") or (session and session.awaiting_input)):
        await handle_text_input(update, context)