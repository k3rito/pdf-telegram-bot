import logging
from pathlib import Path

def setup_logging(log_dir: Path, level: str) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "bot.log"

    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(log_path, encoding="utf-8"),
    ]

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )

    return logging.getLogger("pdfbot")
