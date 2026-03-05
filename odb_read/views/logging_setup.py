"""OBD log capture and logging configuration."""

import logging
import os
from datetime import datetime

from odb_read.models.log_config import LogConfig


class OBDLogHandler(logging.Handler):
    """In-memory log handler that keeps the last 80 log messages for TUI display."""

    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        msg = self.format(record)
        self.logs.append(msg)
        if len(self.logs) > 80:
            self.logs.pop(0)


def setup_logging(log_config: LogConfig):
    """Configure obd/obd.elm loggers. Returns (log_handler, elm_log_file)."""
    log_handler = OBDLogHandler()
    log_handler.setFormatter(logging.Formatter("[%(name)s] %(message)s"))

    elm_log_file = None

    for name in ("obd", "obd.elm"):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        logger.addHandler(log_handler)
        logger.propagate = False

    if log_config.enable_elm:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"elm_log_{ts}.log"
        elm_log_file = log_config.path(default_name, log_config.elm_filename)
        os.makedirs(os.path.dirname(elm_log_file) or ".", exist_ok=True)
        file_handler = logging.FileHandler(elm_log_file)
        file_handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(name)s] %(message)s")
        )
        for name in ("obd", "obd.elm"):
            logging.getLogger(name).addHandler(file_handler)

    return log_handler, elm_log_file
