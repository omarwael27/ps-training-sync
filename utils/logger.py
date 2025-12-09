import logging
import sys
from typing import Optional


def setup_logger(name: str = "ACMTracker", level: int = logging.INFO) -> logging.Logger:
    """
    Setup and configure logger with both file and console handlers

    Args:
        name: Logger name
        level: Logging level

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_format)

    file_handler = logging.FileHandler("acm_tracker.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
