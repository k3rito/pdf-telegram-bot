from __future__ import annotations

from pathlib import Path
import asyncio
import fitz

from telegram import Update
from telegram.ext import ContextTypes

from config import MAX_FILE_SIZE, MAX_FILES_PER_SESSION, MAX_TOTAL_SIZE, UPLOAD_FRAMES, UPLOAD_MESSAGES
from core.middleware import guard
from core.task_manager import build_task
from keyboards.inline import upload_actions, single_actions, rotate_actions
from keyboards.main_menu import main_menu
from utils.helpers import build_file_list, format_size, safe_filename
from utils.service_config import SERVICE_RULES
from utils.validators import is_pdf, parse_rotate, parse_page_order, validate_password


async def activate_service_session(update: Update, context: ContextTypes.DEFAULT_TYPE, service: str) -> None:
    if service == "ocr" and not context.application.bot_data.get("ocr_enabled", False):
        target = update.message or update.callback_query and update.callback_query.message
        if target:
            await target.reply_text("OCR غير متاح حالياً.")
        return

    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return

    session_manager = context.application.bot_data["session_manager"]
    session = session_manager.create(chat.id, user.id, service)

    rules = SERVICE_RULES.get(service)
    if not rules:
        return

    target = update.message or update.callback_query and update.callback_query.message
    if not target:
        return

    await target.reply_text(rules["prompt"], parse_mode="Markdown")

    if session.files:
        await _show_upload_status(update, context, session)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    doc = update.message.document
    if not doc:
        return

    session_manager = context.application.bot_data["session_manager"]
    session = session_manager.get(chat_id, user_id)

    if not session:
        return

    if session.locked:
        await update.message.reply_text("المعالجة جارية بالفعل. انتظر النتيجة.")
        return

    rules = SERVICE_RULES.get(session.service)
    if session.service != "auto" and not rules:
        return

    if rules and rules["file_type"] != "pdf":
        await update.message.reply_text("هذه الخدمة تحتاج صور وليس PDF.")
        return

    if not is_pdf(doc.file_name or "", doc.mime_type):
        await update.message.reply_text("الرجاء إرسال ملف PDF فقط.")
        return

    if doc.file_size and doc.file_size > MAX_FILE_SIZE:
        await update.message.reply_text("حجم الملف كبير جداً.")
        return

    if len(session.files) >= MAX_FILES_PER_SESSION:
        await update.message.reply_text("تم بلوغ الحد الأقصى للملفات.")
        return

    file = await doc.get_file()
    filename = safe_filename(doc.file_name or "file.pdf")
    target = session.temp_dir / filename

    await _download_with_progress(update, file, target)

    size = target.stat().st_size
    session.files.append({"path": target, "name": filename, "size": size})
    session.last_message_id = update.message.message_id
    session.touch()

    total_size = sum(item["size"] for item in session.files)
    if total_size > MAX_TOTAL_SIZE:
        target.unlink(missing_ok=True)
        session.files.pop()
        await update.message.reply_text("إجمالي الحجم تجاوز الحد المسموح.")
        return

    await _show_upload_status(update, context, session)

    if rules and rules.get("needs_param") and not session.params.get(rules["needs_param"]):
        await _request_param(update, context, session, rules["needs_param"], from_upload=True)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    session_manager = context.application.bot_data["session_manager"]
    session = session_manager.get(chat_id, user_id)

    photo = update.message.photo[-1] if update.message.photo else None
    doc = update.message.document
    if not photo and doc and doc.mime_type and doc.mime_type.startswith("image/"):
        photo = doc

    if not photo:
        return

    if not session:
        return

    rules = SERVICE_RULES.get(session.service)
    if rules and rules["file_type"] != "image":
        await update.message.reply_text("هذه الخدمة تحتاج PDF وليس صور.")
        return

    if session.locked:
        await update.message.reply_text("المعالجة جارية بالفعل.")
        return

    if len(session.files) >= MAX_FILES_PER_SESSION:
        await update.message.reply_text("تم بلوغ الحد الأقصى للملفات.")
        return

    file_obj = await photo.get_file()
    filename = "image" if not doc else safe_filename(doc.file_name or "image")
    ext = Path(filename).suffix or ".jpg"
    filename = f"image_{len(session.files) + 1}{ext}"
    target = session.temp_dir / filename

    photo_size = doc.file_size if doc and doc.file_size else getattr(photo, "file_size", None)
    if photo_size and photo_size > MAX_FILE_SIZE:
        await update.message.reply_text("حجم الصورة كبير جداً.")
        return

    await _download_with_progress(update, file_obj, target)

    size = target.stat().st_size
    session.files.append({"path": target, "name": filename, "size": size})
    session.last_message_id = update.message.message_id
    session.touch()

    total_size = sum(item["size"] for item in session.files)
    if total_size > MAX_TOTAL_SIZE:
        target.unlink(missing_ok=True)
        session.files.pop()
        await update.message.reply_text("إجمالي الحجم تجاوز الحد المسموح.")
        return

    await _show_upload_status(update, context, session)


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update, context):
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    if context.user_data.get("broadcast_pending"):
        from handlers.admin_handler import run_broadcast

        await run_broadcast(update, context)
        return

    session_manager = context.application.bot_data["session_manager"]
    session = session_manager.get(chat_id, user_id)
    if not session or not session.awaiting_input:
        return

    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        bot_id = context.application.bot.id
        if update.message.reply_to_message.from_user.id != bot_id:
            return
    else:
        return

    text = update.message.text.strip()
    if session.awaiting_input == "password":
        if not validate_password(text):
            await update.message.reply_text("كلمة المرور قصيرة جداً.")
            return
        session.params["password"] = text

    elif session.awaiting_input == "watermark":
        session.params["watermark"] = text

    elif session.awaiting_input == "signature":
        session.params["signature"] = text

    elif session.awaiting_input == "degrees":
        degrees = parse_rotate(text)
        if not degrees:
            await update.message.reply_text("الرجاء إرسال 90 أو 180 أو 270.")
            return
        session.params["degrees"] = degrees

    elif session.awaiting_input == "order":
        if not session.files:
            await update.message.reply_text("أرسل ملف PDF أولاً.")
            return
        doc = fitz.open(session.files[0]["path"])
        page_count = doc.page_count
        doc.close()
        order = parse_page_order(text, page_count)
        if not order:
            await update.message.reply_text(
                f"رتب الصفحات بأرقام من 1 إلى {page_count} بدون تكرار."
            )
            return
        session.params["order"] = order

    session.awaiting_input = None
    session.last_message_id = update.message.message_id
    session.touch()
    await update.message.reply_text(
        "تم حفظ البيانات. اضغط بدء المعالجة.",
        reply_markup=single_actions() if not SERVICE_RULES[session.service]["multi"] else upload_actions(),
    )


async def start_processing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    session_manager = context.application.bot_data["session_manager"]
    session = session_manager.get(chat_id, user_id)
    if not session:
        await update.callback_query.message.reply_text("لا توجد ملفات للمعالجة.")
        return

    rules = SERVICE_RULES.get(session.service)
    if not rules:
        await update.callback_query.message.reply_text(
            "اختر الخدمة أولاً.",
            reply_markup=main_menu(
                is_admin=user_id in context.application.bot_data["admin_ids"],
                ocr_enabled=context.application.bot_data.get("ocr_enabled", False),
            ),
        )
        return

    if len(session.files) < rules["min_files"]:
        await update.callback_query.message.reply_text("أرسل ملفات أكثر للمعالجة.")
        return

    needs_param = rules.get("needs_param")
    if needs_param and not session.params.get(needs_param):
        await _request_param(update, context, session, needs_param, from_upload=False)
        return

    session.locked = True
    task_manager = context.application.bot_data["task_manager"]
    file_paths = [item["path"] for item in session.files]

    task = build_task(
        user_id=user_id,
        chat_id=chat_id,
        service=session.service,
        file_paths=file_paths,
        params=session.params,
        temp_dir=session.temp_dir,
        reply_to_message_id=session.last_message_id,
        chat_type=update.effective_chat.type,
    )

    queue_size = task_manager.queue.qsize() + len(task_manager.active_tasks) + 1
    await update.callback_query.message.reply_text(
        f"تمت إضافة المهمة للطابور. رقمك: {queue_size}"
    )
    await task_manager.enqueue(task)


async def _show_upload_status(update: Update, context: ContextTypes.DEFAULT_TYPE, session) -> None:
    total_size = sum(item["size"] for item in session.files)
    file_list = build_file_list(session.files)
    rules = SERVICE_RULES.get(session.service)
    target = update.message or update.callback_query and update.callback_query.message
    if not target:
        return
    if session.service == "auto":
        await target.reply_text(
            "تم استلام PDF. اختر الخدمة المناسبة:\n\n"
            f"{file_list}",
            reply_markup=main_menu(
                is_admin=update.effective_user.id in context.application.bot_data["admin_ids"],
                ocr_enabled=context.application.bot_data.get("ocr_enabled", False),
            ),
        )
        return

    multi = rules.get("multi", False) if rules else False

    text = (
        "الملفات الحالية:\n"
        f"{file_list}\n\n"
        f"الحجم الكلي: {format_size(total_size)}"
    )

    keyboard = upload_actions() if multi else single_actions()
    await target.reply_text(text, reply_markup=keyboard)


async def show_session_status(update: Update, context: ContextTypes.DEFAULT_TYPE, session) -> None:
    await _show_upload_status(update, context, session)


async def _request_param(update: Update, context: ContextTypes.DEFAULT_TYPE, session, param: str, from_upload: bool) -> None:
    session.awaiting_input = param
    target = update.message or update.callback_query and update.callback_query.message
    if param == "password":
        await target.reply_text("أرسل كلمة مرور قوية (لا تقل عن 4 أحرف).")
        return

    if param == "watermark":
        await target.reply_text("اكتب نص العلامة المائية.")
        return

    if param == "signature":
        await target.reply_text("اكتب نص التوقيع.")
        return

    if param == "order":
        await target.reply_text(
            "أرسل ترتيب الصفحات مثل: 3 1 2"
        )
        return

    if param == "degrees":
        await target.reply_text(
            "اختر زاوية التدوير:",
            reply_markup=rotate_actions(),
        )
        return


async def _download_with_progress(update: Update, file_obj, target: Path) -> None:
    message = await update.message.reply_text("جاري رفع الملف...")

    async def animate() -> None:
        index = 0
        while True:
            try:
                frame = UPLOAD_FRAMES[index % len(UPLOAD_FRAMES)]
                text = UPLOAD_MESSAGES[index % len(UPLOAD_MESSAGES)]
                await message.edit_text(f"{frame} {text}")
                index += 1
                await asyncio.sleep(1.2)
            except Exception:
                break

    task = asyncio.create_task(animate())
    try:
        await file_obj.download_to_drive(custom_path=str(target))
    finally:
        task.cancel()
        try:
            await message.delete()
        except Exception:
            pass
