from __future__ import annotations

import math
import os
import re
from pathlib import Path
from typing import Dict


def human_readable_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    idx = 0
    size = float(num_bytes)
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024.0
        idx += 1
    return f"{size:.1f} {units[idx]}"


def compute_size(path: str) -> int:
    target = Path(path)
    if target.is_file():
        try:
            return target.stat().st_size
        except OSError:
            return 0

    total = 0
    for root, _, files in os.walk(target, followlinks=False):
        for name in files:
            file_path = Path(root) / name
            try:
                if not file_path.is_symlink():
                    total += file_path.stat().st_size
            except OSError:
                continue
    return total


def summarize_output_file(path: str) -> Dict[str, int | bool]:
    file_path = Path(path)
    if not file_path.exists():
        return {
            "exists": False,
            "words": 0,
            "tokens": 0,
            "lines": 0,
            "chars": 0,
            "bytes": 0,
        }

    text = file_path.read_text(encoding="utf-8", errors="ignore")
    words = len(re.findall(r"\S+", text))
    lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
    chars = len(text)
    bytes_len = len(text.encode("utf-8"))

    tokens = 0
    try:
        import tiktoken

        try:
            encoder = tiktoken.encoding_for_model("gpt-4o-mini")
        except Exception:
            encoder = tiktoken.get_encoding("cl100k_base")
        tokens = len(encoder.encode(text))
    except Exception:
        tokens = math.ceil(chars / 4) if chars else 0

    return {
        "exists": True,
        "words": words,
        "tokens": tokens,
        "lines": lines,
        "chars": chars,
        "bytes": bytes_len,
    }

