from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import PARSE_MODE
from core.middleware import guard
from handlers.admin_handler import (
    show_admin_menu,
    admin_stats,
    admin_users,
    admin_tasks,
    admin_banned,
    admin_broadcast,
)
from handlers.pdf_handler import activate_service_session, start_processing
from keyboards.main_menu import main_menu, more_menu
from utils.service_config import SERVICE_KEYS, SERVICE_RULES


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    query = update.callback_query
    await query.answer()
    data = query.data

    user_id = update.effective_user.id
    is_admin = user_id in context.application.bot_data["admin_ids"]
    ocr_enabled = context.application.bot_data.get("ocr_enabled", False)

    if data == "main_menu":
        await query.edit_message_text(
            "القائمة الرئيسية:",
            reply_markup=main_menu(is_admin=is_admin, ocr_enabled=ocr_enabled),
            parse_mode=PARSE_MODE,
        )
        return

    if data == "more_menu":
        await query.edit_message_text(
            "أدوات إضافية:",
            reply_markup=more_menu(is_admin=is_admin),
            parse_mode=PARSE_MODE,
        )
        return

    if data == "help":
        from utils.i18n import t
        from config import DEFAULT_LANG

        lang = context.user_data.get("lang", DEFAULT_LANG)
        await query.edit_message_text(
            t("help", lang),
            reply_markup=main_menu(is_admin=is_admin, ocr_enabled=ocr_enabled),
            parse_mode=PARSE_MODE,
        )
        return

    if data == "profile":
        from database.stats import get_profile

        db = context.application.bot_data["db"]
        profile = await get_profile(db, user_id)
        from utils.helpers import service_title

        favorite = service_title(profile.favorite_service) if profile.favorite_service else "-"
        text = (
            "*معلوماتك*\n\n"
            f"المهام المنفذة: {profile.total_tasks}\n"
            f"الملفات المعالجة: {profile.total_files}\n"
            f"الخدمة المفضلة: {favorite}"
        )
        await query.edit_message_text(
            text,
            reply_markup=main_menu(is_admin=is_admin, ocr_enabled=ocr_enabled),
            parse_mode=PARSE_MODE,
        )
        return

    if data == "admin_menu":
        await show_admin_menu(update, context)
        return

    if data == "admin_stats":
        await admin_stats(update, context)
        return

    if data == "admin_users":
        await admin_users(update, context)
        return

    if data == "admin_tasks":
        await admin_tasks(update, context)
        return

    if data == "admin_banned":
        await admin_banned(update, context)
        return

    if data == "admin_broadcast":
        await admin_broadcast(update, context)
        return

    if data == "cancel":
        session_manager = context.application.bot_data["session_manager"]
        session_manager.clear(update.effective_chat.id, user_id)
        await query.edit_message_text(
            "تم الإلغاء. اختر خدمة أخرى:",
            reply_markup=main_menu(is_admin=is_admin, ocr_enabled=ocr_enabled),
            parse_mode=PARSE_MODE,
        )
        return

    if data == "continue_upload":
        await query.message.reply_text("أرسل الملفات الإضافية الآن.")
        return

    if data == "remove_last":
        session_manager = context.application.bot_data["session_manager"]
        session = session_manager.get(update.effective_chat.id, user_id)
        if not session or not session.files:
            await query.message.reply_text("لا يوجد ملفات للحذف.")
            return

        last = session.files.pop()
        last_path = last["path"]
        if last_path.exists():
            last_path.unlink(missing_ok=True)
        session.touch()
        await query.message.reply_text("تم حذف آخر ملف.")
        return

    if data == "process_now":
        await start_processing(update, context)
        return

    if data.startswith("rotate_"):
        session_manager = context.application.bot_data["session_manager"]
        session = session_manager.get(update.effective_chat.id, user_id)
        if not session:
            return
        degrees = int(data.split("_")[1])
        session.params["degrees"] = degrees
        session.awaiting_input = None
        from keyboards.inline import single_actions, upload_actions
        from utils.service_config import SERVICE_RULES

        rules = SERVICE_RULES.get(session.service, {})
        actions = upload_actions() if rules.get("multi") else single_actions()
        await query.message.reply_text(
            f"تم تحديد {degrees}°. اضغط بدء المعالجة.",
            reply_markup=actions,
        )
        return

    if data in SERVICE_KEYS:
        await activate_service_session(update, context, data)
        return

