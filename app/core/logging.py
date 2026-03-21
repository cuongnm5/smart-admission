from __future__ import annotations

import json
import logging
from datetime import datetime, timezone


_DEFAULT_LOG_RECORD_FIELDS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "taskName",
    "message",
    "asctime",
}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra_payload = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _DEFAULT_LOG_RECORD_FIELDS and not key.startswith("_")
        }
        payload.update(extra_payload)
        return json.dumps(payload)


def configure_logging(log_file: str = "app.log") -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    formatter = JsonFormatter()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)
