import logging
import os
import sys
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, Optional

# Configure logging formats
DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DETAILED_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | [%(filename)s:%(lineno)d] | %(message)s"
)

# Log level mapping
LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

# Default log configuration
DEFAULT_LOG_CONFIG = {
    "level": "info",
    "format": DEFAULT_FORMAT,
    "date_format": "%Y-%m-%d %H:%M:%S",
}


@lru_cache(maxsize=128)
def get_logger(
    name: str,
    level: Optional[str] = None,
    format_string: Optional[str] = None,
    date_format: Optional[str] = None,
    detailed: bool = False,
    log_to_file: bool = False,
    log_dir: Optional[str] = None,
) -> logging.Logger:
    """
    Get a configured logger with the specified settings.
    Uses an LRU cache to avoid creating multiple instances for the same logger name.

    Args:
        name: The name of the logger
        level: Log level (debug, info, warning, error, critical)
        format_string: Custom format string for the logs
        date_format: Custom date format for the logs
        detailed: Use detailed format including filename and line number
        log_to_file: Whether to also log to a file
        log_dir: Directory for log files

    Returns:
        A configured logger instance
    """
    # Use environment variables or defaults
    env_level = os.getenv("LOG_LEVEL", DEFAULT_LOG_CONFIG["level"]).lower()
    level = (level or env_level).lower()

    if level not in LOG_LEVEL_MAP:
        level = "info"  # Fallback to info if invalid level

    numeric_level = LOG_LEVEL_MAP[level]

    # Set format based on parameters or environment
    if detailed:
        format_string = DETAILED_FORMAT
    else:
        format_string = format_string or os.getenv(
            "LOG_FORMAT", DEFAULT_LOG_CONFIG["format"]
        )

    date_format = date_format or os.getenv(
        "LOG_DATE_FORMAT", DEFAULT_LOG_CONFIG["date_format"]
    )

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)

    # Clear existing handlers to avoid duplication when using cached loggers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter(format_string, date_format)
    console_handler.setFormatter(formatter)

    # Add console handler to logger
    logger.addHandler(console_handler)

    # Add file handler if requested
    if log_to_file:
        log_dir = log_dir or os.getenv("LOG_DIR", "./logs")
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


class LogContext:
    """
    Context manager for adding additional context to log messages.
    """

    def __init__(self, logger: logging.Logger, context: Dict[str, Any]):
        self.logger = logger
        self.context = context
        self.original_factory = logging.getLogRecordFactory()

    def __enter__(self):
        # Create a new record factory that adds our context
        old_factory = self.original_factory
        context = self.context

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            for key, value in context.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore the original record factory
        logging.setLogRecordFactory(self.original_factory)


def with_context(logger: logging.Logger, context: Dict[str, Any]) -> LogContext:
    """
    Add context to a logger.

    Args:
        logger: The logger to add context to
        context: Dictionary of context values to add

    Returns:
        A LogContext context manager
    """
    return LogContext(logger, context)


# Example usage
if __name__ == "__main__":
    # Simple usage
    logger = get_logger("example")
    logger.info("This is an info message")
    logger.error("This is an error message")

    # With context
    with with_context(logger, {"user_id": "123", "request_id": "abc-def"}):
        logger.info("Processing user request")
