from __future__ import annotations

import json
import os
from pathlib import Path
from threading import Lock
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parent.parent
SERVER_DIR = ROOT_DIR / "server"
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
LISTS_DIR = ROOT_DIR / "lists"
CONFIG_FILE_PATH = DATA_DIR / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "TARGET_FOLDER": "",
    "NAME_OUTPUT_FILE": str(OUTPUT_DIR / "OutputAllNames.txt"),
    "OUTPUT_FILE": "",
    "EXCLUDE_FILE_PATH": str(LISTS_DIR / "exclude_me.txt"),
    "JUST_ME_FILE_PATH": str(LISTS_DIR / "just_me.txt"),
}

ALLOWED_ROOTS: list[str] = []

_config_cache: Dict[str, Any] | None = None
_config_mtime: float = 0.0  # Track config file modification time
_lock = Lock()


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LISTS_DIR.mkdir(parents=True, exist_ok=True)


def clean_path(value: str) -> str:
    if not value:
        return value
    path = value.strip()
    smart_quotes = {("\u201c", "\u201d"), ("\u2018", "\u2019")}
    while len(path) >= 2 and (
        (path[0] == path[-1] and path[0] in {'"', "'"})
        or (path[0], path[-1]) in smart_quotes
    ):
        path = path[1:-1].strip()

    path = path.replace("\\", "/")

    if path.startswith("//"):
        head, rest = "//", path[2:]
        while "//" in rest:
            rest = rest.replace("//", "/")
        return head + rest

    if len(path) >= 3 and path[1:3] == ":/":
        drive, rest = path[:3], path[3:]
        while "//" in rest:
            rest = rest.replace("//", "/")
        return drive + rest

    while "//" in path:
        path = path.replace("//", "/")

    return path


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}


def is_allowed_path(path: str) -> bool:
    if not ALLOWED_ROOTS:
        return True
    target = Path(path).resolve()
    for root in ALLOWED_ROOTS:
        root_path = Path(root).resolve()
        try:
            if root_path in target.parents or target == root_path:
                return True
        except ValueError:
            continue
    return False


def _resolve_default(value: str | None, default_path: Path) -> str:
    if not value:
        return str(default_path)

    cleaned = clean_path(value)
    candidate = Path(cleaned)

    if not candidate.is_absolute():
        candidate = (ROOT_DIR / candidate).resolve()

    if candidate.exists():
        return str(candidate)

    if candidate.name == default_path.name:
        return str(default_path)

    return str(candidate)


def load_config() -> Dict[str, Any]:
    global _config_cache, _config_mtime

    with _lock:
        ensure_directories()

        if not CONFIG_FILE_PATH.exists():
            _config_cache = DEFAULT_CONFIG.copy()
            _config_mtime = 0.0
            with CONFIG_FILE_PATH.open("w", encoding="utf-8") as fp:
                json.dump(_config_cache, fp, indent=4)
            return _config_cache

        # PERFORMANCE: Track file modification time for smart reload
        _config_mtime = CONFIG_FILE_PATH.stat().st_mtime

        with CONFIG_FILE_PATH.open("r", encoding="utf-8") as fp:
            loaded = json.load(fp)

        config: Dict[str, Any] = DEFAULT_CONFIG.copy()
        config.update(loaded)

        config["NAME_OUTPUT_FILE"] = _resolve_default(
            config.get("NAME_OUTPUT_FILE"), OUTPUT_DIR / "OutputAllNames.txt"
        )
        config["EXCLUDE_FILE_PATH"] = _resolve_default(
            config.get("EXCLUDE_FILE_PATH"), LISTS_DIR / "exclude_me.txt"
        )
        config["JUST_ME_FILE_PATH"] = _resolve_default(
            config.get("JUST_ME_FILE_PATH"), LISTS_DIR / "just_me.txt"
        )

        output_file = config.get("OUTPUT_FILE")
        if isinstance(output_file, str) and output_file.strip():
            config["OUTPUT_FILE"] = clean_path(output_file)

        target = config.get("TARGET_FOLDER")
        if isinstance(target, str) and target.strip():
            config["TARGET_FOLDER"] = clean_path(target)

        _config_cache = config
        return config


def get_config() -> Dict[str, Any]:
    """
    Get config with smart reload on file modification.
    
    PERFORMANCE: Only reloads if config.json has been modified since last load.
    Prevents stale data while avoiding unnecessary I/O.
    """
    global _config_cache, _config_mtime
    
    # Check if config file has been modified
    if _config_cache is not None and CONFIG_FILE_PATH.exists():
        current_mtime = CONFIG_FILE_PATH.stat().st_mtime
        if current_mtime > _config_mtime:
            # Config file changed, reload
            return load_config()
    
    if _config_cache is None:
        return load_config()
    
    return _config_cache


def save_config(data: Dict[str, Any]) -> None:
    global _config_cache, _config_mtime
    with _lock:
        ensure_directories()
        with CONFIG_FILE_PATH.open("w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=4)
        _config_cache = data
        # Update mtime after saving
        _config_mtime = CONFIG_FILE_PATH.stat().st_mtime


def get_config_value(key: str, default: Any = None) -> Any:
    return get_config().get(key, default)


# Load once so the config file is ready for use.
load_config()
