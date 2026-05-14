from __future__ import annotations

from pathlib import Path
import psutil
from telegram import Update
from telegram.ext import ContextTypes

from core.middleware import guard
from database.stats import get_admin_overview
from keyboards.admin_menu import admin_menu
from keyboards.main_menu import main_menu


def _is_admin(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    return user_id in context.application.bot_data.get("admin_ids", [])


async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user_id = update.effective_user.id
    if not _is_admin(context, user_id):
        await update.callback_query.message.reply_text("لا تمتلك صلاحية الإدارة.")
        return

    await update.callback_query.message.reply_text("لوحة الإدارة:", reply_markup=admin_menu())


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user_id = update.effective_user.id
    if not _is_admin(context, user_id):
        await update.message.reply_text("لا تمتلك صلاحية الإدارة.")
        return

    await update.message.reply_text("لوحة الإدارة:", reply_markup=admin_menu())


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user_id = update.effective_user.id
    if not _is_admin(context, user_id):
        return

    db = context.application.bot_data["db"]
    overview = await get_admin_overview(db)
    from utils.helpers import service_title

    overview["top_service"] = service_title(overview.get("top_service"))
    task_manager = context.application.bot_data["task_manager"]

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(Path.cwd().anchor)

    text = (
        "*حالة البوت*\n\n"
        f"المستخدمون: {overview['users']}\n"
        f"الملفات المعالجة: {overview['files']}\n"
        f"الخدمة الأكثر: {overview['top_service']}\n"
        f"المحظورون: {overview['banned']}\n"
        f"مهام نشطة: {len(task_manager.active_tasks)}\n"
        f"في الطابور: {task_manager.queue.qsize()}\n\n"
        f"RAM: {memory.percent}%\n"
        f"Disk: {disk.percent}%"
    )

    await update.callback_query.message.reply_text(text, reply_markup=admin_menu(), parse_mode="Markdown")


async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user_id = update.effective_user.id
    if not _is_admin(context, user_id):
        return

    db = context.application.bot_data["db"]
    overview = await get_admin_overview(db)
    await update.callback_query.message.reply_text(
        f"إجمالي المستخدمين: {overview['users']}",
        reply_markup=admin_menu(),
    )


async def admin_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user_id = update.effective_user.id
    if not _is_admin(context, user_id):
        return

    task_manager = context.application.bot_data["task_manager"]
    active = "\n".join(
        f"- {task_id} ({task.service})" for task_id, task in task_manager.active_tasks.items()
    ) or "-"

    text = (
        "*المهام*\n\n"
        f"نشطة: {len(task_manager.active_tasks)}\n"
        f"في الطابور: {task_manager.queue.qsize()}\n\n"
        f"المهام النشطة:\n{active}"
    )

    await update.callback_query.message.reply_text(text, reply_markup=admin_menu(), parse_mode="Markdown")


async def admin_banned(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user_id = update.effective_user.id
    if not _is_admin(context, user_id):
        return

    db = context.application.bot_data["db"]
    overview = await get_admin_overview(db)
    await update.callback_query.message.reply_text(
        f"المحظورون: {overview['banned']}",
        reply_markup=admin_menu(),
    )


async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user_id = update.effective_user.id
    if not _is_admin(context, user_id):
        return

    context.user_data["broadcast_pending"] = True
    await update.callback_query.message.reply_text("أرسل رسالة البث الآن:")


async def run_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not _is_admin(context, user_id):
        context.user_data.pop("broadcast_pending", None)
        return

    context.user_data.pop("broadcast_pending", None)
    text = update.message.text
    db = context.application.bot_data["db"]
    user_ids = await db.get_all_user_ids()

    sent = 0
    for uid in user_ids:
        try:
            await context.application.bot.send_message(uid, text)
            sent += 1
        except Exception:
            continue

    await update.message.reply_text(f"تم إرسال البث إلى {sent} مستخدم.")


async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user_id = update.effective_user.id
    if not _is_admin(context, user_id):
        return

    if not context.args:
        await update.message.reply_text("\u0627\u0633\u062a\u062e\u062f\u0645: /ban <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("\u0627\u0644\u0645\u0639\u0631\u0641 \u063a\u064a\u0631 \u0635\u062d\u064a\u062d.")
        return
    db = context.application.bot_data["db"]
    await db.set_ban(target_id, True)
    await update.message.reply_text("تم حظر المستخدم.")


async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user_id = update.effective_user.id
    if not _is_admin(context, user_id):
        return

    if not context.args:
        await update.message.reply_text("\u0627\u0633\u062a\u062e\u062f\u0645: /unban <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("\u0627\u0644\u0645\u0639\u0631\u0641 \u063a\u064a\u0631 \u0635\u062d\u064a\u062d.")
        return
    db = context.application.bot_data["db"]
    await db.set_ban(target_id, False)
    await update.message.reply_text("تم إلغاء حظر المستخدم.")


async def admin_back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    is_admin = update.effective_user.id in context.application.bot_data["admin_ids"]
    ocr_enabled = context.application.bot_data.get("ocr_enabled", False)
    await update.callback_query.message.reply_text(
        "الرجوع إلى القائمة:",
        reply_markup=main_menu(is_admin=is_admin, ocr_enabled=ocr_enabled),
    )
