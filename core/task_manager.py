from __future__ import annotations

import asyncio
import logging
import uuid
from pathlib import Path

from telegram import InputFile
from telegram.error import RetryAfter

from core.config.settings import get_settings
from services.queue.base import QueueTask
from services.queue.manager import QueueManager
from services.dispatcher import run_service
from services.types import ServiceResult
from keyboards.main_menu import main_menu
from models.task_status import TaskStatus


Task = QueueTask


class TaskManager:
    def __init__(
        self,
        worker_count: int,
        task_timeout: int,
        task_retries: int,
        db,
        session_manager,
        progress_manager,
        ocr_enabled: bool,
        logger: logging.Logger,
        queue_manager: QueueManager | None = None,
    ) -> None:
        self.worker_count = worker_count
        self.task_timeout = task_timeout
        self.task_retries = task_retries
        self.db = db
        self.session_manager = session_manager
        self.progress_manager = progress_manager
        self.ocr_enabled = ocr_enabled
        self.logger = logger
        self.queue_manager = queue_manager or QueueManager.from_settings(get_settings())
        self.queue = self.queue_manager
        self.active_tasks: dict[str, Task] = {}
        self._workers: list[asyncio.Task[None]] = []

    async def start(self, application) -> None:
        await self.queue_manager.start()
        for _ in range(self.worker_count):
            self._workers.append(asyncio.create_task(self._worker(application)))

    async def stop(self) -> None:
        for worker in self._workers:
            worker.cancel()
        self._workers.clear()
        await self.queue_manager.stop()

    async def enqueue(self, task: QueueTask) -> str:
        await self.db.add_task(task.id, task.user_id, task.service, TaskStatus.QUEUED.value)
        await self.queue_manager.enqueue(task)
        return task.id

    async def _worker(self, application) -> None:
        while True:
            lease = await self.queue_manager.reserve(timeout=1)
            if lease is None:
                await asyncio.sleep(0.1)
                continue

            task = lease.task
            self.active_tasks[task.id] = task
            try:
                await self.db.update_task_status(task.id, TaskStatus.RUNNING.value)
                await self._execute(task, application)
                await self.db.update_task_status(task.id, TaskStatus.SUCCESS.value)
                await self.queue_manager.ack(task.id)
            except Exception as exc:
                await self.db.update_task_status(task.id, TaskStatus.FAILED.value)
                file_paths = [Path(path) for path in task.file_paths]
                file_count = len(file_paths)
                total_size = sum(path.stat().st_size for path in file_paths if path.exists())
                await self.db.add_stat(task.user_id, task.service, TaskStatus.FAILED.value, file_count, total_size)
                self.logger.exception("Task failed USER=%s SERVICE=%s", task.user_id, task.service)
                await self._notify_error(application, task, exc)
            finally:
                self.active_tasks.pop(task.id, None)
                self.session_manager.clear(task.chat_id, task.user_id)

    async def _execute(self, task: Task, application) -> None:
        bot = application.bot
        message = await self._safe_send_message(
            bot,
            task.chat_id,
            "بدء المعالجة...",
            reply_to_message_id=task.reply_to_message_id,
        )
        progress = asyncio.create_task(self.progress_manager.animate(message))

        try:
            result = await self._run_with_retries(task)
        finally:
            progress.cancel()
            try:
                await message.delete()
            except Exception:
                pass

        await self._send_result(bot, task, result)

        is_admin = task.user_id in application.bot_data.get("admin_ids", [])
        ocr_enabled = application.bot_data.get("ocr_enabled", False)
        await self._safe_send_message(
            bot,
            task.chat_id,
            "اختر خدمة أخرى:",
            reply_markup=main_menu(is_admin=is_admin, ocr_enabled=ocr_enabled),
            reply_to_message_id=task.reply_to_message_id,
        )

        file_count = len(task.file_paths)
        total_size = sum(path.stat().st_size for path in task.file_paths if path.exists())
        await self.db.add_stat(task.user_id, task.service, TaskStatus.SUCCESS.value, file_count, total_size)

    async def _send_result(self, bot, task: Task, result: ServiceResult) -> None:
        if result.kind == "text":
            await self._safe_send_message(
                bot,
                task.chat_id,
                result.text or "",
                reply_to_message_id=task.reply_to_message_id,
            )
            return

        if result.path and result.path.exists():
            with open(result.path, "rb") as handle:
                document = InputFile(handle, filename=result.filename or result.path.name)
                await self._safe_send_document(
                    bot,
                    task.chat_id,
                    document=document,
                    caption=result.caption,
                    reply_to_message_id=task.reply_to_message_id,
                )

    async def _notify_error(self, application, task: Task, exc: Exception) -> None:
        bot = application.bot
        message = (
            "فشل تنفيذ العملية.\n\n"
            "السبب المحتمل:\n"
            "الملف تالف أو محمي.\n\n"
            "حاول رفع ملف آخر."
        )
        if isinstance(exc, RuntimeError):
            message = str(exc)
        await self._safe_send_message(
            bot,
            task.chat_id,
            message,
            reply_to_message_id=task.reply_to_message_id,
        )

        is_admin = task.user_id in application.bot_data.get("admin_ids", [])
        ocr_enabled = application.bot_data.get("ocr_enabled", False)
        await self._safe_send_message(
            bot,
            task.chat_id,
            "اختر خدمة أخرى:",
            reply_markup=main_menu(is_admin=is_admin, ocr_enabled=ocr_enabled),
            reply_to_message_id=task.reply_to_message_id,
        )

    async def _run_with_retries(self, task: Task) -> ServiceResult:
        attempts = max(0, int(getattr(self, "task_retries", 0))) + 1
        last_exc: Exception | None = None
        for attempt in range(attempts):
            try:
                return await asyncio.wait_for(
                    asyncio.to_thread(
                        run_service,
                        task.service,
                        [Path(path) for path in task.file_paths],
                        task.params,
                        Path(task.temp_dir),
                        self.ocr_enabled,
                    ),
                    timeout=self.task_timeout,
                )
            except Exception as exc:
                last_exc = exc
                if attempt < attempts - 1:
                    await asyncio.sleep(1)
                    continue
                raise
        raise last_exc if last_exc else RuntimeError("Task failed")

    async def _safe_send_message(self, bot, chat_id: int, text: str, **kwargs):
        while True:
            try:
                return await bot.send_message(chat_id=chat_id, text=text, **kwargs)
            except RetryAfter as exc:
                await asyncio.sleep(exc.retry_after)

    async def _safe_send_document(self, bot, chat_id: int, document, **kwargs):
        while True:
            try:
                return await bot.send_document(chat_id=chat_id, document=document, **kwargs)
            except RetryAfter as exc:
                await asyncio.sleep(exc.retry_after)


def build_task(
    user_id: int,
    chat_id: int,
    chat_type: str,
    reply_to_message_id: int | None,
    service: str,
    file_paths: list[Path],
    params: dict,
    temp_dir: Path,
) -> Task:
    task_id = uuid.uuid4().hex
    return QueueTask(
        id=task_id,
        user_id=user_id,
        chat_id=chat_id,
        chat_type=chat_type,
        reply_to_message_id=reply_to_message_id,
        service=service,
        file_paths=[str(path) for path in file_paths],
        params=params,
        temp_dir=str(temp_dir),
    )
