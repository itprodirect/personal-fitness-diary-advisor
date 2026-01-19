"""Centralized logging configuration for Personal Fitness Diary Advisor."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Log directory setup
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Log file path
LOG_FILE = LOG_DIR / "fitness_diary.log"

# Log format
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Default log level (can be overridden by environment variable)
DEFAULT_LOG_LEVEL = logging.INFO

# Track if logging has been configured
_logging_configured = False


def configure_logging(level: int = DEFAULT_LOG_LEVEL) -> None:
    """Configure the root logger with file and console handlers.

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
    """
    global _logging_configured

    if _logging_configured:
        return

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove any existing handlers
    root_logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console handler - INFO and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler - with rotation (5MB max, 3 backups)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    _logging_configured = True

    # Log startup message
    root_logger.info("Logging configured - File: %s, Level: %s", LOG_FILE, logging.getLevelName(level))


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module.

    Args:
        name: Name of the logger (typically __name__ from the calling module)

    Returns:
        Configured logger instance
    """
    # Ensure logging is configured
    configure_logging()

    return logging.getLogger(name)
