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
# Increased from 2MB to 10MB for larger source files
# Can be overridden in config.json with MAX_FILE_SIZE_MB
MAX_FILE_BYTES = config_data.get("MAX_FILE_SIZE_MB", 10) * 1024 * 1024


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


def is_excluded(root: str, filename: str, exclude_set: set[str], base_folder: str = "") -> bool:
    """
    Cek apakah file/folder harus di-exclude.
    Sekarang mendukung:
    - Nama file saja: page.html
    - Path relatif: src/pages/page.html
    - Pattern: **/node_modules/**, *.log
    """
    # Buat full path dan relative path
    full_path = os.path.join(root, filename)
    normalized_full = full_path.replace("\\", "/")
    
    # Buat relative path dari base folder jika ada
    if base_folder:
        try:
            rel_path = os.path.relpath(full_path, base_folder).replace("\\", "/")
        except ValueError:
            rel_path = normalized_full
    else:
        rel_path = normalized_full
    
    # Cek setiap pattern di exclude_set
    for pattern in exclude_set:
        if not pattern:
            continue
            
        pattern_norm = pattern.replace("\\", "/")
        
        # Exact match dengan nama file
        if pattern == filename:
            return True
        
        # Exact match dengan relative path
        if pattern_norm == rel_path:
            return True
        
        # Substring match untuk path
        if pattern_norm in rel_path:
            return True
        
        # Substring match untuk nama file (backward compatibility)
        if pattern in filename:
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


def dir_should_keep(root_path: str, just_set: set[str], exclude_set: set[str], base_folder: str = "") -> bool:
    """
    Tentukan apakah direktori harus di-keep berdasarkan just_me list.
    Sekarang mendukung path lengkap.
    
    **IMPORTANT:** Jika just_set hanya berisi filenames (bukan folder paths),
    maka SEMUA directories harus di-keep agar bisa scan nested files.
    """
    if not just_set:
        return True
    
    # Buat relative path jika base folder ada
    if base_folder:
        try:
            rel_path = os.path.relpath(root_path, base_folder).replace("\\", "/")
        except ValueError:
            rel_path = root_path.replace("\\", "/")
    else:
        rel_path = root_path.replace("\\", "/")
    
    # Cek apakah ada pattern yang match
    for pattern in just_set:
        if not pattern:
            continue
        
        pattern_norm = pattern.replace("\\", "/")
        
        # Exact match
        if pattern_norm == rel_path:
            return True
        
        # Substring match (untuk folder parent)
        if pattern_norm in rel_path or rel_path in pattern_norm:
            return True
        
        # Basename match (backward compatibility)
        if pattern == os.path.basename(root_path):
            return True
        
        # **NEW:** Jika pattern adalah filename (tidak ada / atau \), 
        # keep directory untuk scan nested files
        if "/" not in pattern and "\\" not in pattern:
            # Pattern adalah filename, bukan path
            # Keep directory agar bisa scan files di dalamnya
            return True
    
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

    # Simpan base folder untuk relative path calculation
    base_folder = os.path.abspath(folder_path)

    header_note = "BA denotes the top border and WA denotes the bottom border used to separate files.\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # List untuk track extracted files
    extracted_files: list[str] = []
    
    # Progress tracking
    file_count = 0
    total_size = 0
    skipped_count = 0
    
    # Summary info
    log(f"[*] Memulai scanning folder: {folder_path}")
    if just_set:
        log(f"[*] Filter: Hanya {len(just_set)} file/folder → {just_set}")
    else:
        log(f"[*] Filter: ALL FILES (exclude {len(exclude_set)} patterns)")
    log(f"[*] Max file size: {MAX_FILE_BYTES / 1024 / 1024:.1f} MB")
    
    with output_path.open("w", encoding="utf-8", errors="ignore") as out:
        if formatted_output:
            out.write(header_note)

        for root, dirs, files in os.walk(folder_path):
            pruned_dirs: list[str] = []
            for directory in list(dirs):
                full_path = os.path.join(root, directory)
                
                # Cek exclude dengan base folder
                if is_excluded(root, directory, exclude_set, base_folder):
                    continue
                
                # Cek just_me dengan base folder
                if not dir_should_keep(full_path, just_set, exclude_set, base_folder):
                    continue
                    
                pruned_dirs.append(directory)
            dirs[:] = pruned_dirs

            for filename in files:
                file_path = os.path.join(root, filename)
                
                # Cek exclude dengan base folder
                if is_excluded(root, filename, exclude_set, base_folder):
                    skipped_count += 1
                    continue

                # Cek just_me dengan path lengkap
                if just_set:
                    file_path = os.path.join(root, filename)
                    try:
                        rel_path = os.path.relpath(file_path, base_folder).replace("\\", "/")
                    except ValueError:
                        rel_path = file_path.replace("\\", "/")
                    
                    # Cek apakah file match dengan pattern di just_set
                    matched = False
                    for pattern in just_set:
                        if not pattern:
                            continue
                        pattern_norm = pattern.replace("\\", "/")
                        
                        # Exact match
                        if pattern_norm == rel_path:
                            matched = True
                            break
                        
                        # Substring match
                        if pattern_norm in rel_path:
                            matched = True
                            break
                        
                        # Filename match (backward compatibility)
                        if pattern == filename:
                            matched = True
                            break
                    
                    if not matched:
                        skipped_count += 1
                        continue

                ext = os.path.splitext(filename)[1].lower()
                if WHITELIST_EXT is not None and ext and ext not in WHITELIST_EXT:
                    skipped_count += 1
                    continue

                file_path = os.path.join(root, filename)

                try:
                    size = os.path.getsize(file_path)
                except Exception:
                    skipped_count += 1
                    continue

                if size > MAX_FILE_BYTES:
                    skipped_count += 1
                    continue

                try:
                    with open(file_path, "rb") as binary_file:
                        sample = binary_file.read(4096)
                        if looks_binary(sample):
                            skipped_count += 1
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
                    
                    file_count += 1
                    total_size += size
                    
                    # Track extracted file
                    extracted_files.append(file_path)
                    
                    # Progress log setiap 100 files
                    if file_count % 100 == 0:
                        log(f"[+] Diproses: {file_count} files ({total_size / 1024 / 1024:.1f} MB)")
                    
                except Exception as exc:
                    log(f"[!] Melewatkan file '{file_path}' karena kesalahan: {exc}")
                    skipped_count += 1

    # Save extracted files list to project directory
    project_output_dir = ROOT_DIR / "data" / "output"
    project_output_dir.mkdir(parents=True, exist_ok=True)
    extracted_list_path = project_output_dir / "OutputExtractedFiles.txt"
    
    try:
        with extracted_list_path.open("w", encoding="utf-8") as f:
            # Write target folder as root
            f.write(f"{base_folder}; [FOLDER]\n")
            
            # Write all extracted files
            for file_path in extracted_files:
                # Normalize path separators
                normalized_path = file_path.replace("\\", "/")
                f.write(f"{normalized_path}; [FILE]\n")
        
        log(f"-> File list saved: '{extracted_list_path}'")
    except Exception as exc:
        log(f"[!] Warning: Gagal menyimpan file list: {exc}")

    log(f"\n-> Berhasil! {file_count} files digabungkan ({total_size / 1024 / 1024:.1f} MB)")
    log(f"-> Skipped: {skipped_count} files (binary/too large/errors)")
    log(f"-> Output: '{output_path}'.")


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

