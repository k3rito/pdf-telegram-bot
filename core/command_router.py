from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable

from telegram import Update
from telegram.ext import ContextTypes

from config import DEFAULT_LANG, PREFIX_TOKEN, PARSE_MODE
from core.middleware import guard
from core.prefix_parser import ParsedCommand, PrefixParser
from handlers.pdf_handler import activate_service_session
from handlers.start_handler import cancel, start
from utils.i18n import t


@dataclass(slots=True)
class RoutedContext:
    update: Update
    context: ContextTypes.DEFAULT_TYPE
    parsed: ParsedCommand
    session: object | None
    is_group: bool
    is_private: bool
    reply_target: object | None


CommandHandler = Callable[[RoutedContext], Awaitable[None]]
CommandMiddleware = Callable[[RoutedContext], Awaitable[bool]]


class CommandRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, CommandHandler] = {}
        self._aliases: dict[str, str] = {}

    def register(self, command: str, handler: CommandHandler, *aliases: str) -> None:
        self._handlers[command] = handler
        for alias in aliases:
            self._aliases[alias] = command

    def resolve(self, command: str) -> CommandHandler | None:
        canonical = self._aliases.get(command, command)
        return self._handlers.get(canonical)


class CommandRouter:
    def __init__(self, prefix_token: str = PREFIX_TOKEN) -> None:
        self.parser = PrefixParser(prefix_token)
        self.registry = CommandRegistry()
        self.middlewares: list[CommandMiddleware] = [self._guard_middleware]
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.registry.register("help", self._handle_help, "start", "settings")
        self.registry.register("cancel", self._handle_cancel)
        self.registry.register("lang", self._handle_lang)
        self.registry.register("queue", self._handle_queue)
        self.registry.register("merge", self._handle_service)
        self.registry.register("split", self._handle_service)
        self.registry.register("compress", self._handle_service)
        self.registry.register("extract_text", self._handle_service, "extract")
        self.registry.register("extract_images", self._handle_service, "images")
        self.registry.register("rotate_pdf", self._handle_service, "rotate")
        self.registry.register("ocr", self._handle_service)
        self.registry.register("encrypt_pdf", self._handle_service, "encrypt")
        self.registry.register("decrypt_pdf", self._handle_service, "decrypt")
        self.registry.register("watermark_pdf", self._handle_service, "watermark")
        self.registry.register("reorder_pages", self._handle_service, "reorder")

    async def route(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        message = update.message
        if not message or not message.text:
            return False

        bot_username = getattr(context.application.bot, "username", None)
        parsed = self.parser.parse(
            message.text,
            bot_username,
            update.effective_chat.type if update.effective_chat else "",
            getattr(message, "entities", None),
        )
        if not parsed:
            return False

        user = update.effective_user
        chat = update.effective_chat
        if not user or not chat:
            return False

        session_manager = context.application.bot_data["session_manager"]
        session = session_manager.get(chat.id, user.id)
        routed = RoutedContext(
            update=update,
            context=context,
            parsed=parsed,
            session=session,
            is_group=chat.type in {"group", "supergroup"},
            is_private=chat.type == "private",
            reply_target=message,
        )

        for middleware in self.middlewares:
            if not await middleware(routed):
                return True

        handler = self.registry.resolve(parsed.command)
        if not handler:
            await self._reply_unknown(routed)
            return True

        await handler(routed)
        return True

    async def _guard_middleware(self, routed: RoutedContext) -> bool:
        return await guard(routed.update, routed.context)

    async def _handle_help(self, routed: RoutedContext) -> None:
        await start(routed.update, routed.context)

    async def _handle_cancel(self, routed: RoutedContext) -> None:
        await cancel(routed.update, routed.context)

    async def _handle_lang(self, routed: RoutedContext) -> None:
        lang = routed.parsed.args[0].lower() if routed.parsed.args else None
        if lang not in {"ar", "en"}:
            await routed.reply_target.reply_text(
                "🌐 استخدم: @pdf lang ar أو @pdf lang en\n\n🌐 Use: @pdf lang ar or @pdf lang en",
                parse_mode=PARSE_MODE,
            )
            return

        routed.context.user_data["lang"] = lang
        await routed.reply_target.reply_text(t("lang_set", lang).format(lang=lang), parse_mode=PARSE_MODE)

    async def _handle_queue(self, routed: RoutedContext) -> None:
        task_manager = routed.context.application.bot_data["task_manager"]
        session = routed.session
        active_count = len(task_manager.active_tasks)
        queued_count = task_manager.queue.qsize()
        session_state = "نشطة" if session and getattr(session, "locked", False) else "غير نشطة"
        await routed.reply_target.reply_text(
            "📦 حالة الطابور:\n"
            f"- المهام النشطة: {active_count}\n"
            f"- المهام المنتظرة: {queued_count}\n"
            f"- الجلسة الحالية: {session_state}",
            parse_mode=PARSE_MODE,
        )

    async def _handle_service(self, routed: RoutedContext) -> None:
        service = routed.parsed.command
        service_aliases = {
            "extract_text": "extract_text",
            "extract_images": "extract_images",
            "rotate_pdf": "rotate_pdf",
            "encrypt_pdf": "encrypt_pdf",
            "decrypt_pdf": "decrypt_pdf",
            "watermark_pdf": "watermark_pdf",
            "reorder_pages": "reorder_pages",
        }
        await activate_service_session(routed.update, routed.context, service_aliases.get(service, service))

    async def _reply_unknown(self, routed: RoutedContext) -> None:
        await routed.reply_target.reply_text(
            "❓ أمر غير معروف.\n\n"
            "الأوامر المتاحة:\n"
            "@pdf merge\n"
            "@pdf split\n"
            "@pdf compress\n"
            "@pdf extract\n"
            "@pdf rotate\n"
            "@pdf ocr\n"
            "@pdf encrypt\n"
            "@pdf decrypt\n"
            "@pdf images\n"
            "@pdf reorder\n"
            "@pdf watermark\n"
            "@pdf queue\n"
            "@pdf settings\n"
            "@pdf lang",
            parse_mode=PARSE_MODE,
        )


command_router = CommandRouter()