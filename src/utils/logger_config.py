"""[BOILERPLATE] Structured JSON logging configuration.

Do not modify per client.
"""
import json
import logging
import os
from datetime import datetime
from threading import Lock

try:
    from bson import ObjectId
    HAS_BSON = True
except ImportError:
    HAS_BSON = False


class SingletonLogger:
    """Thread-safe singleton logger."""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        """Create singleton instance."""
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._init()
            return cls._instance

    def _init(self):
        """Initialize logger with handlers."""
        self.logger = logging.getLogger("ChatbotLogger")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        if self.logger.handlers:
            return

        formatter = JsonFormatter()

        stream = logging.StreamHandler()
        stream.setFormatter(formatter)
        self.logger.addHandler(stream)

        log_dir = os.getenv("LOG_DIR", "/tmp/logs")
        os.makedirs(log_dir, exist_ok=True)

        try:
            file_handler = logging.FileHandler(f"{log_dir}/app.log", "a")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.warning(f"File logging disabled: {e}")


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record):
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Include extra fields
        skip_keys = {
            "name", "msg", "args", "created", "filename", "funcName",
            "levelname", "levelno", "lineno", "module", "msecs",
            "message", "pathname", "process", "processName", "relativeCreated",
            "thread", "threadName", "exc_info", "exc_text", "stack_info",
        }
        for k, v in vars(record).items():
            if k not in skip_keys:
                if HAS_BSON and isinstance(v, ObjectId):
                    log_data[k] = str(v)
                elif isinstance(v, datetime):
                    log_data[k] = v.isoformat()
                else:
                    log_data[k] = v

        return json.dumps(log_data, default=str)


logger = SingletonLogger().logger
