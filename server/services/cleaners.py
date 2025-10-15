from __future__ import annotations

from pathlib import Path
from typing import Tuple


def remove_blank_lines_inplace(file_path: str) -> Tuple[bool, int | str]:
    """Remove blank or whitespace-only lines from a file in-place."""
    path = Path(file_path)
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
        cleaned = [line for line in lines if line.strip()]
        path.write_text("".join(cleaned), encoding="utf-8", errors="ignore")
        return True, len(lines) - len(cleaned)
    except Exception as exc:
        return False, str(exc)

