# Enhanced TextEXtractor.py dengan Progress Tracking
from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path
from typing import Callable, Optional

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.config import clean_path, get_config
from server.services.task_manager import TaskInfo

# Encoding aman
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Enhanced configuration filter konten
WHITELIST_EXT = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".md", ".txt", ".html", 
    ".css", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".sql", ".sh", ".bat", 
    ".ps1", ".c", ".cpp", ".h", ".hpp", ".java", ".kt", ".go", ".rs", ".vue", ".xml"
}

# Memory management settings
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10MB
MEMORY_WARNING_THRESHOLD = 80  # 80% of available memory
PROGRESS_UPDATE_INTERVAL = 0.1  # Update progress every 0.1 seconds


def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_memory_usage() -> float:
    """Get current memory usage as percentage"""
    try:
        import psutil
        return psutil.virtual_memory().percent
    except ImportError:
        # Fallback for systems without psutil
        return 0.0


def looks_binary(sample: bytes) -> bool:
    """Enhanced binary detection"""
    if not sample:
        return False
    if b"\x00" in sample:
        return True
    non_text = sum(1 for byte in sample if byte < 9 or (13 < byte < 32) or byte > 126)
    return non_text > len(sample) * 0.30


def read_exclude_file(file_path: str) -> list[str]:
    """Read exclusion patterns from file"""
    path = Path(file_path)
    if not path.exists():
        return []
    entries = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                entries.append(stripped)
    return entries


def is_excluded(root: str, filename: str, exclude_set: set[str], base_folder: str = "") -> bool:
    """Enhanced exclusion checking"""
    full_path = os.path.join(root, filename)
    normalized_full = full_path.replace("\\", "/")
    
    if base_folder:
        try:
            rel_path = os.path.relpath(full_path, base_folder).replace("\\", "/")
        except ValueError:
            rel_path = normalized_full
    else:
        rel_path = normalized_full
    
    for pattern in exclude_set:
        if not pattern:
            continue
            
        pattern_norm = pattern.replace("\\", "/")
        
        if pattern == filename:
            return True
        if pattern_norm == rel_path:
            return True
        if pattern_norm in rel_path:
            return True
        if pattern in filename:
            return True
    
    return False


def read_list_file(file_path: str) -> list[str]:
    """Read inclusion patterns from file"""
    path = Path(file_path)
    if not path.exists():
        return []
    entries = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                entries.append(stripped)
    return entries


def match_any_token(path_or_name: str, tokens_set: set[str]) -> bool:
    """Enhanced token matching"""
    if not tokens_set:
        return True
    normalized = path_or_name.replace("\\", "/")
    for token in tokens_set:
        if token and token in normalized:
            return True
    return False


def dir_should_keep(root_path: str, just_set: set[str], exclude_set: set[str], base_folder: str = "") -> bool:
    """Enhanced directory filtering"""
    if not just_set:
        return True
    
    if base_folder:
        try:
            rel_path = os.path.relpath(root_path, base_folder).replace("\\", "/")
        except ValueError:
            rel_path = root_path.replace("\\", "/")
    else:
        rel_path = root_path.replace("\\", "/")
    
    for pattern in just_set:
        if not pattern:
            continue
        
        pattern_norm = pattern.replace("\\", "/")
        
        if pattern_norm == rel_path:
            return True
        if pattern_norm in rel_path or rel_path in pattern_norm:
            return True
        if pattern == os.path.basename(root_path):
            return True
        if "/" not in pattern and "\\" not in pattern:
            return True  # Filename pattern, keep directory
    
    return False


class ProgressTracker:
    """Enhanced progress tracking for large projects"""
    
    def __init__(self, task_info: TaskInfo, total_files: int):
        self.task_info = task_info
        self.total_files = total_files
        self.processed_files = 0
        self.last_progress_update = time.time()
        self.current_file = ""
        self.start_time = time.time()
    
    def update(self, processed_files: int, current_file: str = ""):
        """Update progress with current file info"""
        self.processed_files = processed_files
        self.current_file = current_file
        
        if self.total_files > 0:
            progress = (processed_files / self.total_files) * 100
            self.task_info.update_progress(
                progress=int(progress),
                current_file=current_file,
                processed_files=processed_files
            )
    
    def get_estimated_remaining(self) -> Optional[float]:
        """Get estimated time remaining"""
        if self.processed_files == 0:
            return None
        
        elapsed = time.time() - self.start_time
        rate = self.processed_files / elapsed
        remaining_files = self.total_files - self.processed_files
        
        return remaining_files / rate if rate > 0 else None


def enhanced_combine_files_in_folder_recursive(
    folder_path: str,
    output_file_name: str = "Output.txt",
    exclude_file: Optional[str] = None,
    formatted_output: bool = True,
    task_info: Optional[TaskInfo] = None,
    progress_callback: Optional[Callable] = None
) -> dict:
    """
    Enhanced file bundling dengan progress tracking dan memory management
    """
    output_path = Path(output_file_name)
    
    # Cleanup output file
    if output_path.exists():
        try:
            output_path.unlink()
        except Exception:
            log(f"[!] Error: Gagal menghapus file output '{output_path}'. Tutup file jika sedang dibuka.")
            return {"success": False, "error": "Output file locked"}
    
    if not os.path.isdir(folder_path):
        log(f"[!] Error: Folder '{folder_path}' tidak ditemukan atau bukan direktori.")
        return {"success": False, "error": "Invalid folder path"}
    
    # Load filters
    exclude_set = set(read_exclude_file(exclude_file) if exclude_file else [])
    just_me_path = get_config().get("JUST_ME_FILE_PATH")
    just_set = set(read_list_file(just_me_path) if just_me_path else [])
    
    # Base folder for relative path calculation
    base_folder = os.path.abspath(folder_path)
    
    # Statistics tracking
    stats = {
        "total_files": 0,
        "processed_files": 0,
        "skipped_files": 0,
        "total_size": 0,
        "start_time": time.time(),
        "memory_peak": 0
    }
    
    # First pass: Count total files untuk progress tracking
    log(f"[*] Scanning for files to process...")
    for root, dirs, files in os.walk(folder_path):
        # Filter directories
        dirs[:] = [d for d in dirs if not is_excluded(root, d, exclude_set, base_folder)]
        
        if just_set:
            dirs[:] = [d for d in dirs if dir_should_keep(os.path.join(root, d), just_set, exclude_set, base_folder)]
        
        for filename in files:
            # Check exclusions
            if is_excluded(root, filename, exclude_set, base_folder):
                continue
            
            # Check inclusion
            if just_set:
                file_path = os.path.join(root, filename)
                if not match_any_token(file_path, just_set):
                    continue
            
            # Check file type and size
            ext = os.path.splitext(filename)[1].lower()
            if WHITELIST_EXT and ext and ext not in WHITELIST_EXT:
                continue
            
            try:
                size = os.path.getsize(os.path.join(root, filename))
                if size > MAX_FILE_BYTES:
                    continue
                stats["total_files"] += 1
            except Exception:
                continue
    
    log(f"[*] Found {stats['total_files']} files to process")
    
    if task_info:
        task_info.total_files = stats["total_files"]
    
    # Initialize progress tracker
    progress_tracker = ProgressTracker(task_info, stats["total_files"]) if task_info else None
    
    header_note = "BA denotes the top border and WA denotes the bottom border used to separate files.\n"
    
    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Track extracted files
    extracted_files = []
    
    # Memory monitoring
    def check_memory_usage():
        memory_usage = get_memory_usage()
        stats["memory_peak"] = max(stats["memory_peak"], memory_usage)
        
        if memory_usage > MEMORY_WARNING_THRESHOLD:
            log(f"[!] Memory usage tinggi: {memory_usage:.1f}%")
            # Trigger garbage collection
            import gc
            gc.collect()
    
    try:
        with output_path.open("w", encoding="utf-8", errors="ignore") as out:
            if formatted_output:
                out.write(header_note)
            
            # Second pass: Process files
            for root, dirs, files in os.walk(folder_path):
                # Memory check
                check_memory_usage()
                
                # Filter directories
                dirs[:] = [d for d in dirs if not is_excluded(root, d, exclude_set, base_folder)]
                
                if just_set:
                    dirs[:] = [d for d in dirs if dir_should_keep(os.path.join(root, d), just_set, exclude_set, base_folder)]
                
                for filename in files:
                    file_path = os.path.join(root, filename)
                    
                    # Check exclusions
                    if is_excluded(root, filename, exclude_set, base_folder):
                        stats["skipped_files"] += 1
                        continue
                    
                    # Check inclusion
                    if just_set and not match_any_token(file_path, just_set):
                        stats["skipped_files"] += 1
                        continue
                    
                    # Check file type
                    ext = os.path.splitext(filename)[1].lower()
                    if WHITELIST_EXT and ext and ext not in WHITELIST_EXT:
                        stats["skipped_files"] += 1
                        continue
                    
                    try:
                        size = os.path.getsize(file_path)
                        if size > MAX_FILE_BYTES:
                            stats["skipped_files"] += 1
                            continue
                    except Exception:
                        stats["skipped_files"] += 1
                        continue
                    
                    # Process file
                    try:
                        # Binary detection
                        with open(file_path, "rb") as binary_file:
                            sample = binary_file.read(4096)
                            if looks_binary(sample):
                                stats["skipped_files"] += 1
                                continue
                        
                        # Read content
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
                            content = handle.read()
                        
                        # Write to output
                        if formatted_output:
                            out.write("BA\n")
                            out.write(f"'{file_path}'\n")
                            out.write(content)
                            out.write("\nWA\n")
                        else:
                            out.write(f"----- {file_path} -----\n")
                            out.write(content)
                            out.write("\n\n")
                        
                        # Update stats
                        stats["processed_files"] += 1
                        stats["total_size"] += size
                        extracted_files.append(file_path)
                        
                        # Update progress
                        if progress_tracker:
                            progress_tracker.update(stats["processed_files"], file_path)
                        
                        # Progress logging setiap 100 files
                        if stats["processed_files"] % 100 == 0:
                            elapsed = time.time() - stats["start_time"]
                            rate = stats["processed_files"] / elapsed
                            eta = (stats["total_files"] - stats["processed_files"]) / rate if rate > 0 else 0
                            log(f"[+] Processed: {stats['processed_files']}/{stats['total_files']} files ({stats['total_size'] / 1024 / 1024:.1f} MB) - ETA: {eta/60:.1f} min")
                        
                        # Memory check
                        check_memory_usage()
                        
                    except Exception as exc:
                        log(f"[!] Error processing '{file_path}': {exc}")
                        stats["skipped_files"] += 1
    
    except Exception as exc:
        log(f"[!] Fatal error: {exc}")
        return {"success": False, "error": str(exc)}
    
    # Save extracted files list
    try:
        project_output_dir = ROOT_DIR / "data" / "output"
        project_output_dir.mkdir(parents=True, exist_ok=True)
        extracted_list_path = project_output_dir / "OutputExtractedFiles.txt"
        
        with extracted_list_path.open("w", encoding="utf-8") as f:
            f.write(f"{base_folder}; [FOLDER]\n")
            for file_path in extracted_files:
                normalized_path = file_path.replace("\\", "/")
                f.write(f"{normalized_path}; [FILE]\n")
        
        log(f"-> File list saved: '{extracted_list_path}'")
    except Exception as exc:
        log(f"[!] Warning: Gagal menyimpan file list: {exc}")
    
    # Final stats
    elapsed_time = time.time() - stats["start_time"]
    rate = stats["processed_files"] / elapsed_time if elapsed_time > 0 else 0
    
    log(f"\n✅ SUCCESS!")
    log(f"   Processed: {stats['processed_files']} files ({stats['total_size'] / 1024 / 1024:.1f} MB)")
    log(f"   Skipped: {stats['skipped_files']} files")
    log(f"   Time: {elapsed_time/60:.1f} min ({rate:.1f} files/sec)")
    log(f"   Memory peak: {stats['memory_peak']:.1f}%")
    log(f"   Output: '{output_path}'")
    
    if task_info:
        task_info.complete({
            "processed_files": stats["processed_files"],
            "total_size": stats["total_size"],
            "skipped_files": stats["skipped_files"],
            "elapsed_time": elapsed_time,
            "memory_peak": stats["memory_peak"],
            "output_file": str(output_path)
        })
    
    return {
        "success": True,
        "stats": stats,
        "output_file": str(output_path),
        "extracted_files_count": len(extracted_files)
    }


def main() -> None:
    """Main function untuk standalone execution"""
    config_data = get_config()
    
    folder = clean_path(os.environ.get("VT_FOLDER") or config_data.get("TARGET_FOLDER") or "")
    if not folder:
        log("[!] TARGET_FOLDER belum diset di config.json")
        return
    
    output_file = config_data.get("OUTPUT_FILE") or str(Path("Output.txt"))
    
    result = enhanced_combine_files_in_folder_recursive(
        folder_path=folder,
        output_file_name=output_file,
        exclude_file=config_data.get("EXCLUDE_FILE_PATH"),
        formatted_output=True,
    )
    
    if not result["success"]:
        log(f"[!] Extraction failed: {result['error']}")


if __name__ == "__main__":
    main()
