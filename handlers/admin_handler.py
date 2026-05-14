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
        await update.callback_query.message.reply_text("\u26d4 \u0644\u0627 \u062a\u0645\u062a\u0644\u0643 \u0635\u0644\u0627\u062d\u064a\u0629 \u0627\u0644\u0625\u062f\u0627\u0631\u0629.")
        return

    await update.callback_query.message.reply_text("\ud83d\udee1 \u0644\u0648\u062d\u0629 \u0627\u0644\u0625\u062f\u0627\u0631\u0629:", reply_markup=admin_menu())


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user_id = update.effective_user.id
    if not _is_admin(context, user_id):
        await update.message.reply_text("\u26d4 \u0644\u0627 \u062a\u0645\u062a\u0644\u0643 \u0635\u0644\u0627\u062d\u064a\u0629 \u0627\u0644\u0625\u062f\u0627\u0631\u0629.")
        return

    await update.message.reply_text("\ud83d\udee1 \u0644\u0648\u062d\u0629 \u0627\u0644\u0625\u062f\u0627\u0631\u0629:", reply_markup=admin_menu())


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
        "\ud83d\udcca *\u062d\u0627\u0644\u0629 \u0627\u0644\u0628\u0648\u062a*\n\n"
        f"\ud83d\udc65 \u0627\u0644\u0645\u0633\u062a\u062e\u062f\u0645\u0648\u0646: {overview['users']}\n"
        f"\ud83d\udcc4 \u0627\u0644\u0645\u0644\u0641\u0627\u062a \u0627\u0644\u0645\u0639\u0627\u0644\u062c\u0629: {overview['files']}\n"
        f"\u2b50 \u0627\u0644\u062e\u062f\u0645\u0629 \u0627\u0644\u0623\u0643\u062b\u0631: {overview['top_service']}\n"
        f"\ud83d\udeab \u0627\u0644\u0645\u062d\u0638\u0648\u0631\u0648\u0646: {overview['banned']}\n"
        f"\u26a1 \u0645\u0647\u0627\u0645 \u0646\u0634\u0637\u0629: {len(task_manager.active_tasks)}\n"
        f"\ud83d\udd52 \u0641\u064a \u0627\u0644\u0637\u0627\u0628\u0648\u0631: {task_manager.queue.qsize()}\n\n"
        f"\ud83d\udca1 RAM: {memory.percent}%\n"
        f"\ud83d\udcbe Disk: {disk.percent}%"
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
        f"\ud83d\udc65 \u0625\u062c\u0645\u0627\u0644\u064a \u0627\u0644\u0645\u0633\u062a\u062e\u062f\u0645\u064a\u0646: {overview['users']}",
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
        "\ud83d\udcc2 *\u0627\u0644\u0645\u0647\u0627\u0645*\n\n"
        f"\u26a1 \u0646\u0634\u0637\u0629: {len(task_manager.active_tasks)}\n"
        f"\ud83d\udd52 \u0641\u064a \u0627\u0644\u0637\u0627\u0628\u0648\u0631: {task_manager.queue.qsize()}\n\n"
        f"\ud83d\udccc \u0627\u0644\u0645\u0647\u0627\u0645 \u0627\u0644\u0646\u0634\u0637\u0629:\n{active}"
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
        f"\ud83d\udeab \u0627\u0644\u0645\u062d\u0638\u0648\u0631\u0648\u0646: {overview['banned']}",
        reply_markup=admin_menu(),
    )


async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user_id = update.effective_user.id
    if not _is_admin(context, user_id):
        return

    context.user_data["broadcast_pending"] = True
    await update.callback_query.message.reply_text("\ud83d\udce2 \u0623\u0631\u0633\u0644 \u0631\u0633\u0627\u0644\u0629 \u0627\u0644\u0628\u062b \u0627\u0644\u0622\u0646:")


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

    await update.message.reply_text(f"\u2705 \u062a\u0645 \u0625\u0631\u0633\u0627\u0644 \u0627\u0644\u0628\u062b \u0625\u0644\u0649 {sent} \u0645\u0633\u062a\u062e\u062f\u0645.")


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
    await update.message.reply_text("\u2705 \u062a\u0645 \u062d\u0638\u0631 \u0627\u0644\u0645\u0633\u062a\u062e\u062f\u0645.")


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
    await update.message.reply_text("\u2705 \u062a\u0645 \u0625\u0644\u063a\u0627\u0621 \u062d\u0638\u0631 \u0627\u0644\u0645\u0633\u062a\u062e\u062f\u0645.")


async def admin_back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    is_admin = update.effective_user.id in context.application.bot_data["admin_ids"]
    ocr_enabled = context.application.bot_data.get("ocr_enabled", False)
    await update.callback_query.message.reply_text(
        "\ud83c\udfe0 \u0627\u0644\u0631\u062c\u0648\u0639 \u0625\u0644\u0649 \u0627\u0644\u0642\u0627\u0626\u0645\u0629:",
        reply_markup=main_menu(is_admin=is_admin, ocr_enabled=ocr_enabled),
    )
