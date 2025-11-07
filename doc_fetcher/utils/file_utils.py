"""File utility functions."""

import re
from pathlib import Path
from typing import Union


def clean_filename(url: str, base_url: str) -> str:
    """
    Convert URL to a clean filename.

    Args:
        url: Full URL to convert
        base_url: Base URL to remove

    Returns:
        Clean filename with .md extension
    """
    # Remove base URL
    path = url.replace(base_url, "").strip("/")

    # Replace slashes with hyphens
    filename = path.replace("/", "-")

    # Remove or replace problematic characters
    filename = re.sub(r"[^\w\-.]", "-", filename)

    # Remove multiple consecutive hyphens
    filename = re.sub(r"-+", "-", filename)

    # Remove leading/trailing hyphens
    filename = filename.strip("-")

    # Ensure .md extension
    if not filename:
        filename = "index"
    if not filename.endswith(".md"):
        filename += ".md"

    return filename


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
