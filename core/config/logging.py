from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        for key in ("trace_id", "correlation_id", "user_id", "chat_id", "task_id"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(log_dir: Path, level: str = "INFO") -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("pdfbot")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()
    logger.propagate = False

    stream = logging.StreamHandler()
    stream.setFormatter(JsonFormatter())
    logger.addHandler(stream)

    file_handler = RotatingFileHandler(log_dir / "pdfbot.log", maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)
    return logger
