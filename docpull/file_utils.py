import re
from pathlib import Path
from typing import Union


def clean_filename(url: str, base_url: str) -> str:
    """
    Clean and sanitize a URL to create a safe filename.

    Args:
        url: The URL to convert to a filename
        base_url: The base URL to remove from the path

    Returns:
        A sanitized filename ending in .md

    Raises:
        TypeError: If url or base_url are not strings
        ValueError: If url or base_url are empty
    """
    if not isinstance(url, str):
        raise TypeError(f"url must be a string, got {type(url).__name__}")
    if not isinstance(base_url, str):
        raise TypeError(f"base_url must be a string, got {type(base_url).__name__}")

    if not url:
        raise ValueError("url cannot be empty")
    if not base_url:
        raise ValueError("base_url cannot be empty")

    path = url.replace(base_url, "").strip("/")
    filename = path.replace("/", "-")
    filename = re.sub(r"[^\w\-.]", "-", filename)
    filename = re.sub(r"-+", "-", filename)
    filename = filename.strip("-")

    if not filename or filename in (".", ".."):
        filename = "index"

    if len(filename) > 200:
        # Hash the overflow to maintain uniqueness and prevent collisions
        import hashlib

        overflow = filename[180:]
        hash_suffix = hashlib.sha256(overflow.encode()).hexdigest()[:12]
        filename = filename[:180] + "-" + hash_suffix

    if not filename.endswith(".md"):
        filename += ".md"

    return filename


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: The directory path to create

    Returns:
        The resolved Path object

    Raises:
        OSError: If directory creation fails
    """
    path = Path(path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_output_path(output_path: Path, base_dir: Path) -> Path:
    """
    Validate that an output path is within the base directory.

    Prevents path traversal attacks by ensuring the output path
    doesn't escape the base directory.

    Args:
        output_path: The path to validate
        base_dir: The base directory to check against

    Returns:
        The resolved output path if valid

    Raises:
        ValueError: If path traversal is detected
    """
    resolved_output = output_path.resolve()
    resolved_base = base_dir.resolve()

    try:
        resolved_output.relative_to(resolved_base)
    except ValueError as e:
        raise ValueError(f"Path traversal detected: {output_path} is outside {base_dir}") from e

    return resolved_output
