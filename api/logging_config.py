"""Logging configuration for the Themis API."""

from __future__ import annotations

import logging
import os
import sys
from typing import Any

# ANSI color codes for terminal output
COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[35m",  # Magenta
    "RESET": "\033[0m",  # Reset
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        if sys.stdout.isatty():  # Only add colors if outputting to terminal
            level_color = COLORS.get(record.levelname, COLORS["RESET"])
            record.levelname = f"{level_color}{record.levelname}{COLORS['RESET']}"
        return super().format(record)


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Get log level from environment or use provided default
    level_str = os.getenv("LOG_LEVEL", log_level).upper()
    level = getattr(logging, level_str, logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Use colored formatter for console
    colored_formatter = ColoredFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(colored_formatter)

    # Configure specific loggers
    loggers = [
        "themis",
        "themis.api",
        "themis.orchestrator",
        "themis.agents",
        "themis.llm_client",
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.handlers = [console_handler]
        logger.propagate = False

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logging.info(f"Logging configured at {level_str} level")


def get_request_logger() -> logging.Logger:
    """Get logger for HTTP requests."""
    return logging.getLogger("themis.api.requests")


def get_audit_logger() -> logging.Logger:
    """Get logger for security audit events."""
    return logging.getLogger("themis.api.audit")


def get_performance_logger() -> logging.Logger:
    """Get logger for performance metrics."""
    return logging.getLogger("themis.api.performance")


def log_structured(logger: logging.Logger, level: str, message: str, **kwargs: Any) -> None:
    """Log a structured message with additional context.

    Args:
        logger: Logger instance to use
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **kwargs: Additional structured data to include
    """
    log_method = getattr(logger, level.lower())
    if kwargs:
        extra_info = " | ".join(f"{k}={v}" for k, v in kwargs.items())
        log_method(f"{message} | {extra_info}")
    else:
        log_method(message)
