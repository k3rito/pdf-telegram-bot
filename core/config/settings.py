from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from core.config.constants import (
    DEFAULT_CLEANUP_INTERVAL,
    DEFAULT_DB_BACKEND,
    DEFAULT_LANG,
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAX_FILE_SIZE,
    DEFAULT_MAX_FILES_PER_SESSION,
    DEFAULT_MAX_TOTAL_SIZE,
    DEFAULT_PREFIX_TOKEN,
    DEFAULT_QUEUE_BACKEND,
    DEFAULT_RATE_LIMIT_COUNT,
    DEFAULT_RATE_LIMIT_WINDOW,
    DEFAULT_REPLY_DELETE_SECONDS,
    DEFAULT_TASK_RETRIES,
    DEFAULT_TASK_TIMEOUT,
    DEFAULT_WORKER_COUNT,
    EnvironmentName,
)

try:  # pragma: no cover - preferred production path
    from pydantic import Field, SecretStr, field_validator
    from pydantic_settings import BaseSettings, SettingsConfigDict
    _PYDANTIC_AVAILABLE = True
except Exception:  # pragma: no cover - local dev fallback when dependencies are missing
    _PYDANTIC_AVAILABLE = False

    class SecretStr:
        def __init__(self, value: str) -> None:
            self._value = value

        def get_secret_value(self) -> str:
            return self._value

    def Field(default: Any = None, *, alias: str | None = None):  # type: ignore[override]
        return default

    def field_validator(*args, **kwargs):  # type: ignore[override]
        def decorator(func):
            return func

        return decorator

    class BaseSettings:  # type: ignore[override]
        pass

    def SettingsConfigDict(**kwargs):  # type: ignore[override]
        return kwargs


class AppSettings(BaseSettings):
    if _PYDANTIC_AVAILABLE:
        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: SecretStr = Field(..., alias="BOT_TOKEN")
    admin_ids: str = Field(default="", alias="ADMIN_IDS")
    prefix_token: str = Field(default=DEFAULT_PREFIX_TOKEN, alias="PREFIX_TOKEN")
    reply_delete_seconds: int = Field(default=DEFAULT_REPLY_DELETE_SECONDS, alias="REPLY_DELETE_SECONDS")
    rate_limit_count: int = Field(default=DEFAULT_RATE_LIMIT_COUNT, alias="RATE_LIMIT_COUNT")
    rate_limit_window: int = Field(default=DEFAULT_RATE_LIMIT_WINDOW, alias="RATE_LIMIT_WINDOW")
    max_file_size: int = Field(default=DEFAULT_MAX_FILE_SIZE, alias="MAX_FILE_SIZE")
    max_files_per_session: int = Field(default=DEFAULT_MAX_FILES_PER_SESSION, alias="MAX_FILES_PER_SESSION")
    max_total_size: int = Field(default=DEFAULT_MAX_TOTAL_SIZE, alias="MAX_TOTAL_SIZE")
    worker_count: int = Field(default=DEFAULT_WORKER_COUNT, alias="WORKER_COUNT")
    task_timeout: int = Field(default=DEFAULT_TASK_TIMEOUT, alias="TASK_TIMEOUT")
    task_retries: int = Field(default=DEFAULT_TASK_RETRIES, alias="TASK_RETRIES")
    cleanup_interval: int = Field(default=DEFAULT_CLEANUP_INTERVAL, alias="CLEANUP_INTERVAL")
    ocr_enabled: bool = Field(default=False, alias="OCR_ENABLED")
    default_lang: str = Field(default=DEFAULT_LANG, alias="DEFAULT_LANG")
    log_level: str = Field(default=DEFAULT_LOG_LEVEL, alias="LOG_LEVEL")
    temp_dir: Path = Field(default=Path("temp"), alias="TEMP_DIR")
    storage_dir: Path = Field(default=Path("storage"), alias="STORAGE_DIR")
    log_dir: Path = Field(default=Path("logs"), alias="LOG_DIR")
    db_path: Path = Field(default=Path("database/pdfbot.db"), alias="DB_PATH")
    queue_backend: str = Field(default=DEFAULT_QUEUE_BACKEND, alias="QUEUE_BACKEND")
    db_backend: str = Field(default=DEFAULT_DB_BACKEND, alias="DB_BACKEND")
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="pdfbot", alias="DB_NAME")
    db_user: str = Field(default="pdfbot", alias="DB_USER")
    db_password: SecretStr = Field(default=SecretStr("pdfbot"), alias="DB_PASSWORD")
    environment: EnvironmentName = Field(default=EnvironmentName.development, alias="APP_ENV")
    api_enabled: bool = Field(default=True, alias="API_ENABLED")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8080, alias="API_PORT")

    def __init__(self, **kwargs: Any) -> None:
        if _PYDANTIC_AVAILABLE:
            super().__init__(**kwargs)
            return

        values = self._defaults_from_env()
        values.update(kwargs)
        self.bot_token = self._as_secret(values.get("BOT_TOKEN", ""))
        self.admin_ids = str(values.get("ADMIN_IDS", ""))
        self.prefix_token = self._normalize_prefix(str(values.get("PREFIX_TOKEN", DEFAULT_PREFIX_TOKEN)))
        self.reply_delete_seconds = int(values.get("REPLY_DELETE_SECONDS", DEFAULT_REPLY_DELETE_SECONDS))
        self.rate_limit_count = int(values.get("RATE_LIMIT_COUNT", DEFAULT_RATE_LIMIT_COUNT))
        self.rate_limit_window = int(values.get("RATE_LIMIT_WINDOW", DEFAULT_RATE_LIMIT_WINDOW))
        self.max_file_size = int(values.get("MAX_FILE_SIZE", DEFAULT_MAX_FILE_SIZE))
        self.max_files_per_session = int(values.get("MAX_FILES_PER_SESSION", DEFAULT_MAX_FILES_PER_SESSION))
        self.max_total_size = int(values.get("MAX_TOTAL_SIZE", DEFAULT_MAX_TOTAL_SIZE))
        self.worker_count = int(values.get("WORKER_COUNT", DEFAULT_WORKER_COUNT))
        self.task_timeout = int(values.get("TASK_TIMEOUT", DEFAULT_TASK_TIMEOUT))
        self.task_retries = int(values.get("TASK_RETRIES", DEFAULT_TASK_RETRIES))
        self.cleanup_interval = int(values.get("CLEANUP_INTERVAL", DEFAULT_CLEANUP_INTERVAL))
        self.ocr_enabled = self._as_bool(values.get("OCR_ENABLED", False))
        self.default_lang = str(values.get("DEFAULT_LANG", DEFAULT_LANG)).lower()
        self.log_level = str(values.get("LOG_LEVEL", DEFAULT_LOG_LEVEL)).upper()
        self.temp_dir = Path(values.get("TEMP_DIR", "temp"))
        self.storage_dir = Path(values.get("STORAGE_DIR", "storage"))
        self.log_dir = Path(values.get("LOG_DIR", "logs"))
        self.db_path = Path(values.get("DB_PATH", "database/pdfbot.db"))
        self.queue_backend = str(values.get("QUEUE_BACKEND", DEFAULT_QUEUE_BACKEND)).lower()
        self.db_backend = str(values.get("DB_BACKEND", DEFAULT_DB_BACKEND)).lower()
        self.redis_url = str(values.get("REDIS_URL", "redis://redis:6379/0"))
        self.database_url = values.get("DATABASE_URL") or None
        self.db_host = str(values.get("DB_HOST", "localhost"))
        self.db_port = int(values.get("DB_PORT", 5432))
        self.db_name = str(values.get("DB_NAME", "pdfbot"))
        self.db_user = str(values.get("DB_USER", "pdfbot"))
        self.db_password = self._as_secret(values.get("DB_PASSWORD", "pdfbot"))
        self.environment = EnvironmentName(str(values.get("APP_ENV", EnvironmentName.development)))
        self.api_enabled = self._as_bool(values.get("API_ENABLED", True))
        self.api_host = str(values.get("API_HOST", "0.0.0.0"))
        self.api_port = int(values.get("API_PORT", 8080))

    @staticmethod
    def _defaults_from_env() -> dict[str, Any]:
        return {
            "BOT_TOKEN": os.getenv("BOT_TOKEN", ""),
            "ADMIN_IDS": os.getenv("ADMIN_IDS", ""),
            "PREFIX_TOKEN": os.getenv("PREFIX_TOKEN", DEFAULT_PREFIX_TOKEN),
            "REPLY_DELETE_SECONDS": os.getenv("REPLY_DELETE_SECONDS", str(DEFAULT_REPLY_DELETE_SECONDS)),
            "RATE_LIMIT_COUNT": os.getenv("RATE_LIMIT_COUNT", str(DEFAULT_RATE_LIMIT_COUNT)),
            "RATE_LIMIT_WINDOW": os.getenv("RATE_LIMIT_WINDOW", str(DEFAULT_RATE_LIMIT_WINDOW)),
            "MAX_FILE_SIZE": os.getenv("MAX_FILE_SIZE", str(DEFAULT_MAX_FILE_SIZE)),
            "MAX_FILES_PER_SESSION": os.getenv("MAX_FILES_PER_SESSION", str(DEFAULT_MAX_FILES_PER_SESSION)),
            "MAX_TOTAL_SIZE": os.getenv("MAX_TOTAL_SIZE", str(DEFAULT_MAX_TOTAL_SIZE)),
            "WORKER_COUNT": os.getenv("WORKER_COUNT", str(DEFAULT_WORKER_COUNT)),
            "TASK_TIMEOUT": os.getenv("TASK_TIMEOUT", str(DEFAULT_TASK_TIMEOUT)),
            "TASK_RETRIES": os.getenv("TASK_RETRIES", str(DEFAULT_TASK_RETRIES)),
            "CLEANUP_INTERVAL": os.getenv("CLEANUP_INTERVAL", str(DEFAULT_CLEANUP_INTERVAL)),
            "OCR_ENABLED": os.getenv("OCR_ENABLED", "false"),
            "DEFAULT_LANG": os.getenv("DEFAULT_LANG", DEFAULT_LANG),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL),
            "TEMP_DIR": os.getenv("TEMP_DIR", "temp"),
            "STORAGE_DIR": os.getenv("STORAGE_DIR", "storage"),
            "LOG_DIR": os.getenv("LOG_DIR", "logs"),
            "DB_PATH": os.getenv("DB_PATH", "database/pdfbot.db"),
            "QUEUE_BACKEND": os.getenv("QUEUE_BACKEND", DEFAULT_QUEUE_BACKEND),
            "DB_BACKEND": os.getenv("DB_BACKEND", DEFAULT_DB_BACKEND),
            "REDIS_URL": os.getenv("REDIS_URL", "redis://redis:6379/0"),
            "DATABASE_URL": os.getenv("DATABASE_URL", ""),
            "DB_HOST": os.getenv("DB_HOST", "localhost"),
            "DB_PORT": os.getenv("DB_PORT", "5432"),
            "DB_NAME": os.getenv("DB_NAME", "pdfbot"),
            "DB_USER": os.getenv("DB_USER", "pdfbot"),
            "DB_PASSWORD": os.getenv("DB_PASSWORD", "pdfbot"),
            "APP_ENV": os.getenv("APP_ENV", EnvironmentName.development),
            "API_ENABLED": os.getenv("API_ENABLED", "true"),
            "API_HOST": os.getenv("API_HOST", "0.0.0.0"),
            "API_PORT": os.getenv("API_PORT", "8080"),
        }

    @staticmethod
    def _as_secret(value: Any) -> SecretStr:
        return value if isinstance(value, SecretStr) else SecretStr(str(value))

    @staticmethod
    def _as_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

    @field_validator("admin_ids", mode="before")
    @classmethod
    def _normalize_admin_ids(cls, value: Any) -> str:
        if isinstance(value, str):
            return value
        if value is None:
            return ""
        return str(value)

    @field_validator("prefix_token")
    @classmethod
    def _normalize_prefix(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith("@"):
            raise ValueError("PREFIX_TOKEN must start with @")
        return value.lower()

    @field_validator("queue_backend", "db_backend", "log_level", "default_lang", mode="before")
    @classmethod
    def _normalize_strings(cls, value: Any) -> str:
        return str(value).strip().lower() if value is not None else ""

    @field_validator("temp_dir", "storage_dir", "log_dir", "db_path", mode="before")
    @classmethod
    def _normalize_paths(cls, value: Any) -> Path:
        return Path(value)

    @property
    def admin_id_list(self) -> list[int]:
        return [int(item) for item in self.admin_ids.split(",") if item.strip().isdigit()]

    def masked(self) -> dict[str, Any]:
        data = self.model_dump(mode="python") if _PYDANTIC_AVAILABLE else self.__dict__.copy()
        data["bot_token"] = "***"
        data["db_password"] = "***"
        return data

    def model_dump(self, mode: str = "python") -> dict[str, Any]:
        _ = mode
        return self.__dict__.copy()


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
