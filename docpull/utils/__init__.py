"""Utility functions for doc_fetcher."""

from .logging_config import setup_logging
from .file_utils import clean_filename, ensure_dir

__all__ = ["setup_logging", "clean_filename", "ensure_dir"]
