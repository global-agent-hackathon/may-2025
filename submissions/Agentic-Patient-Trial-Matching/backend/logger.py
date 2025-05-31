import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

def setup_logger(
    name: str,
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 1024 * 1024,  # 1MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configure and return a logger instance with both console and file handlers.
    
    Args:
        name: Name of the logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        max_file_size: Maximum size of each log file in bytes
        backup_count: Number of backup files to keep
    """
    # Create logs directory if it doesn't exist
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        # Option 1: Clear existing handlers and reconfigure (if you want fresh config)
        # logger.handlers.clear()
        # Option 2: Just return if already configured (if first setup is canonical)
        return logger
    
    logger.setLevel(getattr(logging, log_level.upper()))

    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
    )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Create file handler if log_file is specified
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

# Default logger configuration
default_logger = setup_logger(
    "trial_matcher",
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE", "logs/trial_matcher.log")
)