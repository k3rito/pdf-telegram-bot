from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # For type checkers only; at runtime we import lazily to avoid editor/server diagnostics when
    # `python-telegram-bot` is not installed in the environment.
    from telegram.ext import (
        Application as TGApplication,
        CallbackQueryHandler as TGCallbackQueryHandler,
        MessageHandler as TGMessageHandler,
        filters as TGFilters,
    )  # type: ignore

import importlib

try:
    _telegram_ext = importlib.import_module("telegram.ext")
    Application = _telegram_ext.Application
    CallbackQueryHandler = _telegram_ext.CallbackQueryHandler
    MessageHandler = _telegram_ext.MessageHandler
    filters = _telegram_ext.filters
except Exception:
    Application = None
    CallbackQueryHandler = None
    MessageHandler = None
    filters = None

from config import (
    ADMIN_IDS,
    BOT_TOKEN,
    CLEANUP_INTERVAL,
    DB_PATH,
    LOG_DIR,
    LOG_LEVEL,
    OCR_ENABLED,
    PROCESS_MESSAGES,
    PROGRESS_FRAMES,
    RATE_LIMIT_COUNT,
    RATE_LIMIT_WINDOW,
    STORAGE_DIR,
    TASK_RETRIES,
    TASK_TIMEOUT,
    TEMP_ROOT,
    WORKER_COUNT,
)
from core.progress_manager import ProgressManager
from core.rate_limiter import RateLimiter
from core.session_manager import SessionManager
from core.task_manager import TaskManager
from database.db import Database
from handlers.callback_handler import handle_callback
from handlers.error_handler import handle_error
from handlers.router_handler import handle_incoming_message
from utils.logger import setup_logging


async def on_startup(application: "TGApplication") -> None:
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    db = Database(DB_PATH)
    await db.connect()

    session_manager = SessionManager(TEMP_ROOT)
    rate_limiter = RateLimiter(RATE_LIMIT_COUNT, RATE_LIMIT_WINDOW)
    progress_manager = ProgressManager(PROGRESS_FRAMES, PROCESS_MESSAGES)
    task_manager = TaskManager(
        worker_count=WORKER_COUNT,
        task_timeout=TASK_TIMEOUT,
        task_retries=TASK_RETRIES,
        db=db,
        session_manager=session_manager,
        progress_manager=progress_manager,
        ocr_enabled=OCR_ENABLED,
        logger=application.bot_data["logger"],
    )

    application.bot_data.update(
        {
            "db": db,
            "session_manager": session_manager,
            "rate_limiter": rate_limiter,
            "progress_manager": progress_manager,
            "task_manager": task_manager,
        }
    )

    await task_manager.start(application)

    application.job_queue.run_repeating(cleanup_sessions, interval=CLEANUP_INTERVAL, first=CLEANUP_INTERVAL)


async def on_shutdown(application: "TGApplication") -> None:
    db = application.bot_data.get("db")
    if db:
        await db.close()


async def cleanup_sessions(context) -> None:
    session_manager = context.application.bot_data.get("session_manager")
    logger = context.application.bot_data.get("logger")
    if not session_manager:
        return
    removed = session_manager.cleanup_expired()
    if removed and logger:
        logger.info("Cleaned %s expired sessions", removed)


def main() -> None:
    logger = setup_logging(LOG_DIR, LOG_LEVEL)

    if Application is None:
        raise RuntimeError(
            "python-telegram-bot is not installed in this environment. Install it or run the bot inside the provided Docker image."
        )
    # Narrow types for the type checker: assert the imported variables are available.
    assert Application is not None
    assert CallbackQueryHandler is not None
    assert MessageHandler is not None
    assert filters is not None

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )

    application.bot_data.update(
        {
            "logger": logger,
            "admin_ids": ADMIN_IDS,
            "ocr_enabled": OCR_ENABLED,
        }
    )

    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.ALL, handle_incoming_message))

    application.add_error_handler(handle_error)

    logger.info("Bot is running")
    application.run_polling(allowed_updates=None)


if __name__ == "__main__":
    main()
