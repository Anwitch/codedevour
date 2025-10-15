from __future__ import annotations

import re
from pathlib import Path
from server.config import clean_path


def _read_patterns(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        return [
            line.strip()
            for line in handle
            if line.strip() and not line.lstrip().startswith("#")
        ]


def sync_gitignore_to_exclude(target_folder: str, exclude_file_path: str) -> bool:
    if not target_folder or not exclude_file_path:
        return False

    gitignore_path = Path(clean_path(target_folder)) / ".gitignore"
    if not gitignore_path.exists():
        return False

    try:
        gitignore_lines = _read_patterns(gitignore_path)

        exclude_path = Path(clean_path(exclude_file_path))
        existing_lines = _read_patterns(exclude_path)

        combined = set(existing_lines)
        new_patterns = [pattern for pattern in gitignore_lines if pattern not in combined]
        if not new_patterns:
            return True

        combined.update(new_patterns)

        header = (
            "\n\n# === POLA DARI .gitignore ===\n"
            "# Pola di bawah ini otomatis disinkronkan saat Set Path.\n"
        )

        old_content = ""
        if exclude_path.exists():
            old_content = exclude_path.read_text(encoding="utf-8")

        new_section = header + "\n".join(new_patterns) + "\n"

        if "# === POLA DARI .gitignore ===" in old_content:
            pattern = re.compile(r"(# === POLA DARI \.gitignore ===[\s\S]*?)(?=\n\n|\Z)")
            if pattern.search(old_content):
                final_content = pattern.sub(new_section.rstrip() + "\n", old_content).strip() + "\n"
            else:
                final_content = (old_content.rstrip() + new_section).strip() + "\n"
        else:
            final_content = (old_content.rstrip() + new_section).strip() + "\n"

        exclude_path.parent.mkdir(parents=True, exist_ok=True)
        exclude_path.write_text(final_content, encoding="utf-8")
        return True
    except Exception:
        return False
