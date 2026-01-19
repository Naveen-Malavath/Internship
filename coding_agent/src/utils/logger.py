"""Logging setup with rich formatting"""

import sys
from pathlib import Path

from loguru import logger
from rich.console import Console
from rich.logging import RichHandler


def setup_logger(log_level: str = "INFO", log_file: str = "agent.log") -> None:
    """
    Setup logger with rich formatting and file output
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
    """
    # Remove default logger
    logger.remove()

    # Console handler with rich formatting
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # File handler
    log_path = Path(log_file)
    logger.add(
        log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )

    logger.info(f"Logger initialized with level: {log_level}")


# Rich console for pretty output
console = Console()
