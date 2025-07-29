"""Logging utilities for Nomos."""

import os

from loguru import logger

LOG_LEVEL = os.getenv("SOFIA_LOG_LEVEL", "INFO").upper()
ENABLE_LOGGING = os.getenv("SOFIA_ENABLE_LOGGING", "false").lower() == "true"

if ENABLE_LOGGING:
    logger.info(f"Logging is enabled. Log level set to {LOG_LEVEL}.")


def log_debug(message: str) -> None:
    """Log a debug message."""
    if ENABLE_LOGGING and LOG_LEVEL == "DEBUG":
        logger.debug(message)


def log_info(message: str) -> None:
    """Log an info message."""
    if ENABLE_LOGGING and LOG_LEVEL in ["DEBUG", "INFO", "WARNING"]:
        logger.info(message)


def log_warning(message: str) -> None:
    """Log a warning message."""
    if ENABLE_LOGGING and LOG_LEVEL in ["DEBUG", "INFO", "WARNING"]:
        logger.warning(message)


def log_error(message: str) -> None:
    """Log an error message."""
    if ENABLE_LOGGING and LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        logger.error(message)
