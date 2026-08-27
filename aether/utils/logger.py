"""
Structured research logger for AETHER experiments.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "aether",
    log_dir: Optional[Path] = None,
    log_level: int = logging.INFO,
    console_output: bool = True,
) -> logging.Logger:
    """
    Initializes a structured logger with formatting and optional file persistence.

    Args:
        name: Logger identifier.
        log_dir: Directory where log files are stored.
        log_level: Logging level (default: logging.INFO).
        console_output: If True, streams formatted logs to stdout.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Avoid duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_dir is not None:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / f"{name}.log", encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "aether") -> logging.Logger:
    """Retrieves an existing logger or creates a default logger."""
    return logging.getLogger(name)
