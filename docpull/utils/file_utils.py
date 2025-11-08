import re
from pathlib import Path
from typing import Union


def clean_filename(url: str, base_url: str) -> str:
    path = url.replace(base_url, "").strip("/")
    filename = path.replace("/", "-")
    filename = re.sub(r"[^\w\-.]", "-", filename)
    filename = re.sub(r"-+", "-", filename)
    filename = filename.strip("-")

    if not filename or filename in (".", ".."):
        filename = "index"

    if len(filename) > 200:
        filename = filename[:200]

    if not filename.endswith(".md"):
        filename += ".md"

    return filename


def ensure_dir(path: Union[str, Path]) -> Path:
    path = Path(path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_output_path(output_path: Path, base_dir: Path) -> Path:
    resolved_output = output_path.resolve()
    resolved_base = base_dir.resolve()

    try:
        resolved_output.relative_to(resolved_base)
    except ValueError:
        raise ValueError(f"Path traversal detected: {output_path} is outside {base_dir}")

    return resolved_output
