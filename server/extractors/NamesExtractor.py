# NamesExtractor.py
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.config import clean_path, get_config  # noqa: E402

config_data = get_config()

# Pastikan encoding aman (Windows-friendly)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass  # older Python fallback

# --- GLOBAL logger switch ---
is_json_out = False


def log(*args, **kwargs):
    """Kirim log ke stderr saat output mode JSON, agar stdout tetap 'bersih' untuk JSON."""
    if is_json_out:
        print(*args, file=sys.stderr, **kwargs)
    else:
        print(*args, **kwargs)


def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    idx = 0
    size = float(size_bytes)
    while size >= 1024 and idx < len(size_names) - 1:
        size /= 1024.0
        idx += 1
    return f"{size:.1f} {size_names[idx]}"


def get_folder_size(folder_path: str) -> int:
    total_size = 0
    try:
        for root, _, files in os.walk(folder_path):
            for filename in files:
                full_path = os.path.join(root, filename)
                try:
                    if not os.path.islink(full_path):
                        total_size += os.path.getsize(full_path)
                except (OSError, IOError):
                    pass
    except (OSError, IOError):
        pass
    return total_size


def get_item_size(item_path: str) -> tuple[int, str]:
    try:
        if os.path.isfile(item_path):
            size_bytes = os.path.getsize(item_path)
        elif os.path.isdir(item_path):
            size_bytes = get_folder_size(item_path)
        else:
            return 0, "0 B"
        return size_bytes, format_file_size(size_bytes)
    except (OSError, IOError):
        return 0, "0 B"


def read_list_file(file_path: str) -> list[str]:
    if not file_path or not os.path.exists(file_path):
        return []
    items: list[str] = []
    with open(file_path, "r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                items.append(stripped)
    return items


def match_any_token(value: str, tokens: set[str]) -> bool:
    if not tokens:
        return True
    value_norm = value.replace("\\", "/")
    for token in tokens:
        if token and token in value_norm:
            return True
    return False


def read_exclude_file(file_path: str) -> list[str]:
    if not file_path or not os.path.exists(file_path):
        return []
    excluded: list[str] = []
    with open(file_path, "r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                excluded.append(stripped)
    return excluded


def add_files_to_list(all_items: list[dict], files: list[str], root: str, exclude_names_set: set[str], include_size: bool) -> None:
    for filename in files:
        if filename in exclude_names_set:
            continue
        file_path = os.path.join(root, filename)
        if include_size:
            size_bytes, formatted_size = get_item_size(file_path)
            all_items.append(
                {
                    "path": file_path,
                    "type": "FILE",
                    "size_bytes": size_bytes,
                    "formatted_size": formatted_size,
                }
            )
        else:
            all_items.append({"path": file_path, "type": "FILE"})


def list_all_names(folder_path: str, include_files: bool = True, include_size: bool = False, exclude_file: str | None = None) -> list[dict]:
    if not os.path.isdir(folder_path):
        log(f"[!] Error: Folder '{folder_path}' tidak ditemukan atau bukan direktori.")
        return []

    all_items: list[dict] = []
    exclude_names = read_exclude_file(exclude_file) if exclude_file else []
    exclude_names_set = set(exclude_names)

    just_me_path = config_data.get("JUST_ME_FILE_PATH")
    just_tokens = set(read_list_file(just_me_path) if just_me_path else [])

    log(f"-> Memulai penelusuran dari direktori: {folder_path}")

    for root, dirs, files in os.walk(folder_path):
        if os.path.basename(root) in exclude_names_set:
            del dirs[:]
            continue

        dirs[:] = [directory for directory in dirs if directory not in exclude_names_set]

        def child_matches() -> bool:
            for directory in dirs:
                if match_any_token(os.path.join(root, directory), just_tokens):
                    return True
            for filename in files:
                full_path = os.path.join(root, filename)
                if match_any_token(full_path, just_tokens) or match_any_token(filename, just_tokens):
                    return True
            return False

        show_folder = (not just_tokens) or match_any_token(root, just_tokens) or child_matches()

        if show_folder:
            if include_size:
                size_bytes, formatted_size = get_item_size(root)
                all_items.append(
                    {"path": root, "type": "FOLDER", "size_bytes": size_bytes, "formatted_size": formatted_size}
                )
            else:
                all_items.append({"path": root, "type": "FOLDER"})

        if include_files:
            filtered_files: list[str] = []
            for filename in files:
                if filename in exclude_names_set:
                    continue
                full_path = os.path.join(root, filename)
                if just_tokens and not (
                    match_any_token(full_path, just_tokens) or match_any_token(filename, just_tokens)
                ):
                    continue
                filtered_files.append(filename)

            add_files_to_list(all_items, filtered_files, root, exclude_names_set, include_size)

    return all_items


def main() -> None:
    global is_json_out

    parser = argparse.ArgumentParser(description="List files and folders recursively.")
    parser.add_argument("--include-files", type=lambda x: x.lower() == "true", default=True)
    parser.add_argument("--include-size", type=lambda x: x.lower() == "true", default=False)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    is_json_out = args.format == "json"

    folder = clean_path(os.environ.get("VT_FOLDER") or config_data.get("TARGET_FOLDER") or "")
    if not folder:
        log("[!] TARGET_FOLDER belum diset di config.json")
        return

    items = list_all_names(
        folder_path=folder,
        include_files=args.include_files,
        include_size=args.include_size,
        exclude_file=config_data.get("EXCLUDE_FILE_PATH"),
    )

    if args.format == "json":
        sys.stdout.write(json.dumps(items, ensure_ascii=False))
        try:
            sys.stdout.flush()
        except Exception:
            pass
    else:
        output_file_name = config_data.get("NAME_OUTPUT_FILE")
        try:
            output_path = Path(output_file_name)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding="utf-8") as handle:
                for item in items:
                    if args.include_size and "size_bytes" in item:
                        handle.write(f"{item['path']}; [{item['type']}]; {item['size_bytes']}; {item['formatted_size']}\n")
                    else:
                        handle.write(f"{item['path']}; [{item['type']}]\n")
            log(f"\n-> Berhasil! Daftar semua file/folder disimpan ke '{output_path}'.")
        except Exception as exc:
            log(f"\n[!] Gagal menulis file output: {exc}")


if __name__ == "__main__":
    main()

