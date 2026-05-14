from __future__ import annotations

from core.config.constants import EnvironmentName
from core.config.logging import configure_logging as setup_logging
from core.config.settings import get_settings

_settings = get_settings()

BOT_TOKEN = _settings.bot_token.get_secret_value()
ADMIN_IDS = _settings.admin_id_list
RATE_LIMIT_COUNT = _settings.rate_limit_count
RATE_LIMIT_WINDOW = _settings.rate_limit_window
PREFIX_TOKEN = _settings.prefix_token
REPLY_DELETE_SECONDS = _settings.reply_delete_seconds
MAX_FILE_SIZE = _settings.max_file_size
MAX_FILES_PER_SESSION = _settings.max_files_per_session
MAX_TOTAL_SIZE = _settings.max_total_size
WORKER_COUNT = _settings.worker_count
TASK_TIMEOUT = _settings.task_timeout
TASK_RETRIES = _settings.task_retries
CLEANUP_INTERVAL = _settings.cleanup_interval
OCR_ENABLED = _settings.ocr_enabled
TEMP_ROOT = _settings.temp_dir
STORAGE_DIR = _settings.storage_dir
LOG_DIR = _settings.log_dir
DB_PATH = _settings.db_path
LOG_LEVEL = _settings.log_level
PARSE_MODE = "Markdown"
DEFAULT_LANG = _settings.default_lang
PROCESS_MESSAGES = [
    "📄 جاري تحليل الملف...",
    "🧠 فحص بنية الـ PDF...",
    "⚙️ تنفيذ العملية...",
    "📦 تجهيز الملف النهائي...",
    "🚀 رفع النتيجة...",
]
PROGRESS_FRAMES = ["⏳", "⌛", "⚙️", "📄"]
UPLOAD_MESSAGES = [
    "📤 جاري رفع الملف...",
    "📥 تحقق من البيانات...",
    "📦 حفظ مؤقت...",
]
UPLOAD_FRAMES = ["░░░░", "▓░░░", "▓▓░░", "▓▓▓░", "▓▓▓▓"]

__all__ = [
    "EnvironmentName",
    "BOT_TOKEN",
    "ADMIN_IDS",
    "RATE_LIMIT_COUNT",
    "RATE_LIMIT_WINDOW",
    "PREFIX_TOKEN",
    "REPLY_DELETE_SECONDS",
    "MAX_FILE_SIZE",
    "MAX_FILES_PER_SESSION",
    "MAX_TOTAL_SIZE",
    "WORKER_COUNT",
    "TASK_TIMEOUT",
    "TASK_RETRIES",
    "CLEANUP_INTERVAL",
    "OCR_ENABLED",
    "TEMP_ROOT",
    "STORAGE_DIR",
    "LOG_DIR",
    "DB_PATH",
    "LOG_LEVEL",
    "PARSE_MODE",
    "DEFAULT_LANG",
    "PROCESS_MESSAGES",
    "PROGRESS_FRAMES",
    "UPLOAD_MESSAGES",
    "UPLOAD_FRAMES",
    "setup_logging",
]
