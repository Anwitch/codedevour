# TextEXtractor.py
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.config import clean_path, get_config  # noqa: E402

# Encoding aman
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

config_data = get_config()

# --- Konfigurasi filter konten ---
# Set None untuk mematikan whitelist dan mengambil semua file teks (deteksi binary tetap berlaku).
WHITELIST_EXT = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".md",
    ".txt",
    ".html",
    ".css",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".sql",
    ".sh",
    ".bat",
    ".ps1",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".java",
    ".kt",
    ".go",
    ".rs",
    ".vue",
    ".xml",
}
MAX_FILE_BYTES = 2 * 1024 * 1024  # 2 MB


def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def looks_binary(sample: bytes) -> bool:
    if not sample:
        return False
    if b"\x00" in sample:
        return True
    non_text = sum(1 for byte in sample if byte < 9 or (13 < byte < 32) or byte > 126)
    return non_text > len(sample) * 0.30


def read_exclude_file(file_path: str) -> list[str]:
    path = Path(file_path)
    if not path.exists():
        return []
    entries: list[str] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                entries.append(stripped)
    return entries


def is_excluded(root: str, filename: str, exclude_set: set[str]) -> bool:
    base = os.path.basename(root)
    if base in exclude_set or filename in exclude_set:
        return True
    rel_root = root.replace("\\", "/")
    for token in exclude_set:
        if token in rel_root or token in filename:
            return True
    return False


def read_list_file(file_path: str) -> list[str]:
    path = Path(file_path)
    if not path.exists():
        return []
    entries: list[str] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                entries.append(stripped)
    return entries


def match_any_token(path_or_name: str, tokens_set: set[str]) -> bool:
    if not tokens_set:
        return True
    normalized = path_or_name.replace("\\", "/")
    for token in tokens_set:
        if token and token in normalized:
            return True
    return False


def dir_should_keep(root_path: str, just_set: set[str], exclude_set: set[str]) -> bool:
    if not just_set:
        return True
    if match_any_token(root_path, just_set):
        return True
    base = os.path.basename(root_path)
    if base in exclude_set:
        return False
    return False


def combine_files_in_folder_recursive(
    folder_path: str, output_file_name: str = "Output.txt", exclude_file: str | None = None, formatted_output: bool = True
) -> None:
    output_path = Path(output_file_name)
    if output_path.exists():
        try:
            output_path.unlink()
        except Exception:
            log(f"[!] Error: Gagal menghapus file output '{output_path}'. Tutup file jika sedang dibuka.")
            return

    if not os.path.isdir(folder_path):
        log(f"[!] Error: Folder '{folder_path}' tidak ditemukan atau bukan direktori.")
        return

    exclude_set = set(read_exclude_file(exclude_file) if exclude_file else [])
    just_me_path = config_data.get("JUST_ME_FILE_PATH")
    just_set = set(read_list_file(just_me_path) if just_me_path else [])

    header_note = "BA denotes the top border and WA denotes the bottom border used to separate files.\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", errors="ignore") as out:
        if formatted_output:
            out.write(header_note)

        for root, dirs, files in os.walk(folder_path):
            pruned_dirs: list[str] = []
            for directory in list(dirs):
                full_path = os.path.join(root, directory)
                if is_excluded(full_path, directory, exclude_set):
                    continue
                if not dir_should_keep(full_path, just_set, exclude_set):
                    continue
                pruned_dirs.append(directory)
            dirs[:] = pruned_dirs

            for filename in files:
                if is_excluded(root, filename, exclude_set):
                    continue

                if just_set and not (
                    match_any_token(os.path.join(root, filename), just_set)
                    or match_any_token(filename, just_set)
                ):
                    continue

                ext = os.path.splitext(filename)[1].lower()
                if WHITELIST_EXT is not None and ext and ext not in WHITELIST_EXT:
                    continue

                file_path = os.path.join(root, filename)

                try:
                    size = os.path.getsize(file_path)
                except Exception:
                    continue

                if size > MAX_FILE_BYTES:
                    continue

                try:
                    with open(file_path, "rb") as binary_file:
                        sample = binary_file.read(4096)
                        if looks_binary(sample):
                            continue

                    with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
                        content = handle.read()

                    if formatted_output:
                        out.write("BA\n")
                        out.write(f"'{file_path}'\n")
                        out.write(content)
                        out.write("\nWA\n")
                    else:
                        out.write(f"----- {file_path} -----\n")
                        out.write(content)
                        out.write("\n\n")
                except Exception as exc:
                    log(f"[!] Melewatkan file '{file_path}' karena kesalahan: {exc}")

    log(f"\n-> Berhasil! Semua konten digabungkan ke '{output_path}'.")


def main() -> None:
    folder = clean_path(os.environ.get("VT_FOLDER") or config_data.get("TARGET_FOLDER") or "")
    if not folder:
        log("[!] TARGET_FOLDER belum diset di config.json")
        return

    output_file = config_data.get("OUTPUT_FILE") or str(Path("Output.txt"))
    combine_files_in_folder_recursive(
        folder_path=folder,
        output_file_name=output_file,
        exclude_file=config_data.get("EXCLUDE_FILE_PATH"),
        formatted_output=True,
    )


if __name__ == "__main__":
    main()

