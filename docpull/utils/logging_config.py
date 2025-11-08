import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO", log_file: Optional[str] = None, format_string: Optional[str] = None
) -> logging.Logger:
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger("doc_fetcher")
    logger.setLevel(numeric_level)
    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(format_string)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
