from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from flask import Blueprint, jsonify, request

from server.config import SERVER_DIR, clean_path, get_config, is_allowed_path
from server.services.metrics import compute_size, human_readable_size

names_bp = Blueprint("names", __name__)

NAMES_EXTRACTOR_SCRIPT = Path(SERVER_DIR / "extractors" / "NamesExtractor.py")


@names_bp.route("/run_nameextractor", methods=["POST"])
def run_nameextractor_legacy():
    try:
        payload = request.get_json(silent=True) or {}
        include_files = payload.get("include_files", True)
        include_size = payload.get("include_size", False)

        subprocess.run(
            [
                sys.executable,
                str(NAMES_EXTRACTOR_SCRIPT),
                "--include-files",
                str(include_files),
                "--include-size",
                str(include_size),
                "--format",
                "text",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )

        config = get_config()
        output_path = Path(config.get("NAME_OUTPUT_FILE"))
        content = output_path.read_text(encoding="utf-8", errors="ignore")
        return jsonify({"success": True, "output": content})
    except subprocess.CalledProcessError as exc:
        return jsonify({"success": False, "error": exc.stderr}), 500
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@names_bp.route("/run_nameextractor_json", methods=["POST"])
def run_nameextractor_json():
    try:
        payload = request.get_json(silent=True) or {}
        include_files = payload.get("include_files", True)
        include_size = payload.get("include_size", False)
        override_path = payload.get("path")

        env = os.environ.copy()
        if override_path:
            env["VT_FOLDER"] = clean_path(override_path)

        process = subprocess.run(
            [
                sys.executable,
                str(NAMES_EXTRACTOR_SCRIPT),
                "--include-files",
                str(include_files),
                "--include-size",
                str(include_size),
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
            timeout=600,
            env=env,
        )
        items = json.loads(process.stdout or "[]")
        return jsonify({"success": True, "items": items})
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "Proses terlalu lama dan dihentikan."}), 504
    except subprocess.CalledProcessError as exc:
        return jsonify({"success": False, "error": exc.stderr}), 500
    except json.JSONDecodeError:
        return jsonify({"success": False, "error": "Output JSON tidak valid dari NamesExtractor."}), 500
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@names_bp.route("/size")
def size_endpoint():
    path = clean_path(request.args.get("path", ""))
    if not path or not os.path.exists(path):
        return jsonify({"success": False, "error": "Path tidak ditemukan."}), 400
    if not is_allowed_path(path):
        return jsonify({"success": False, "error": "Path tidak diizinkan."}), 403
    size_bytes = compute_size(path)
    return jsonify(
        {"success": True, "size_bytes": size_bytes, "formatted_size": human_readable_size(size_bytes)}
    )

