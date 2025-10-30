from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple

from flask import Blueprint, Response, jsonify, request

from server.config import (
    OUTPUT_DIR,
    ROOT_DIR,
    SERVER_DIR,
    clean_path,
    get_config,
    save_config,
)
from server.services.cleaners import remove_blank_lines_inplace
from server.services.metrics import summarize_output_file
from server.services.task_manager import task_manager

text_bp = Blueprint("text", __name__)

TEXT_EXTRACTOR_SCRIPT = Path(SERVER_DIR / "extractors" / "TextEXtractor.py")


def _needs_output_destination(cfg: dict, override_dir: str | None = None, override_name: str | None = None) -> Tuple[bool, str, str]:
    if override_dir or override_name:
        return False, "", ""

    out_file = (cfg.get("OUTPUT_FILE") or "").strip()
    if not out_file:
        return True, "OUTPUT_FILE kosong", "Output.txt"

    out_path = Path(out_file)
    out_dir = out_path.parent
    if out_dir == Path("."):
        out_dir = OUTPUT_DIR
    if not out_dir.exists():
        return True, f"Folder output belum ada: {out_dir}", out_path.name or "Output.txt"

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        probe = out_dir / ".cd_probe_write"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except Exception:
        return True, f"Folder output tidak dapat ditulis: {out_dir}", out_path.name or "Output.txt"

    return False, "", ""


@text_bp.route("/run_textextractor", methods=["POST"])
def run_extractor():
    try:
        payload = request.get_json(silent=True) or {}
        override_path = payload.get("path")
        output_dir = payload.get("output_dir")
        output_name = (payload.get("output_name") or "").strip()
        remove_blank = bool(payload.get("remove_blank_lines"))

        config = get_config()
        needs_pick, reason, suggested = _needs_output_destination(config, output_dir, output_name)
        if needs_pick:
            return (
                jsonify(
                    {
                        "success": False,
                        "need_output_path": True,
                        "reason": reason,
                        "suggested_name": suggested,
                    }
                ),
                428,
            )

        env = os.environ.copy()
        if override_path:
            env["VT_FOLDER"] = clean_path(override_path)

        original_output_file = config.get("OUTPUT_FILE")
        if output_dir or output_name:
            base_name = output_name or (Path(original_output_file).name if original_output_file else "Output.txt")
            if output_dir:
                base_dir = Path(clean_path(output_dir))
            elif original_output_file:
                base_dir = Path(original_output_file).parent
            else:
                base_dir = OUTPUT_DIR

            new_output_full = base_dir / base_name
            new_output_full.parent.mkdir(parents=True, exist_ok=True)
            config["OUTPUT_FILE"] = str(new_output_full)
            save_config(config)

        # Increased timeout from 30 min to 2 hours for large projects
        process = subprocess.run(
            [sys.executable, str(TEXT_EXTRACTOR_SCRIPT)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
            timeout=7200,  # 2 hours instead of 30 minutes
            env=env,
        )

        out_path = Path(config.get("OUTPUT_FILE") or (OUTPUT_DIR / "Output.txt"))

        header_notes: list[str] = []
        if remove_blank:
            success, info = remove_blank_lines_inplace(str(out_path))
            if success:
                removed = info if isinstance(info, int) else 0
                header_notes.append(f"Blank-line cleaner: {removed} baris kosong dihapus.")
            else:
                header_notes.append(f"Blank-line cleaner gagal: {info}")
        
        # Add info about OutputExtractedFiles.txt
        extracted_list_path = ROOT_DIR / "data" / "output" / "OutputExtractedFiles.txt"
        if extracted_list_path.exists():
            header_notes.append(f"📋 File list disimpan: {extracted_list_path}")

        def generate():
            header = "\n".join(part for part in [process.stdout, process.stderr] if part).strip()
            note_text = "\n".join(header_notes).strip()
            prelude_parts = [text for text in [header, note_text] if text]
            if prelude_parts:
                yield ("\n".join(prelude_parts)).strip() + "\n\n"

            # PERFORMANCE: Increased chunk size to 128KB for much better I/O efficiency
            # This reduces syscalls and speeds up large file processing significantly
            with out_path.open("r", encoding="utf-8", errors="ignore") as handle:
                for chunk in iter(lambda: handle.read(131072), ""):  # 128KB chunks (was 16KB)
                    yield chunk

        return Response(generate(), mimetype="text/plain; charset=utf-8")
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "TextEXtractor berjalan terlalu lama."}), 504
    except subprocess.CalledProcessError as exc:
        return jsonify({"success": False, "error": exc.stderr}), 500
    except FileNotFoundError:
        return jsonify({"success": False, "error": "File output tidak ditemukan."}), 500
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@text_bp.route("/run_textextractor_async", methods=["POST"])
def run_extractor_async():
    """
    NEW: Async version of text extractor untuk large projects
    Prevent browser timeout dengan background processing
    """
    try:
        payload = request.get_json(silent=True) or {}
        override_path = payload.get("path")
        output_dir = payload.get("output_dir")
        output_name = (payload.get("output_name") or "").strip()
        remove_blank = bool(payload.get("remove_blank_lines"))

        config = get_config()
        needs_pick, reason, suggested = _needs_output_destination(config, output_dir, output_name)
        if needs_pick:
            return (
                jsonify(
                    {
                        "success": False,
                        "need_output_path": True,
                        "reason": reason,
                        "suggested_name": suggested,
                    }
                ),
                428,
            )

        # Setup output file
        original_output_file = config.get("OUTPUT_FILE")
        if output_dir or output_name:
            base_name = output_name or (Path(original_output_file).name if original_output_file else "Output.txt")
            if output_dir:
                base_dir = Path(clean_path(output_dir))
            elif original_output_file:
                base_dir = Path(original_output_file).parent
            else:
                base_dir = OUTPUT_DIR

            new_output_full = base_dir / base_name
            new_output_full.parent.mkdir(parents=True, exist_ok=True)
            config["OUTPUT_FILE"] = str(new_output_full)
            save_config(config)
        else:
            new_output_full = Path(config.get("OUTPUT_FILE") or (OUTPUT_DIR / "Output.txt"))

        # Create async task
        task_info = task_manager.create_task(
            task_type="text_extraction_async",
            params={
                "folder_path": clean_path(override_path) if override_path else config.get("TARGET_FOLDER", ""),
                "output_file": str(new_output_full),
                "formatted_output": True,
                "remove_blank_lines": remove_blank
            }
        )

        return jsonify({
            "success": True,
            "task_id": task_info.task_id,
            "message": "Async text extraction started",
            "status_endpoint": f"/task_status/{task_info.task_id}",
            "result_endpoint": f"/task_result/{task_info.task_id}",
            "download_endpoint": f"/task_result/{task_info.task_id}?download=true"
        })

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500


@text_bp.route("/output_metrics", methods=["GET"])
def output_metrics():
    try:
        config = get_config()
        output_path = config.get("OUTPUT_FILE") or str(OUTPUT_DIR / "Output.txt")
        metrics = summarize_output_file(output_path)
        metrics.update({"success": True})
        return jsonify(metrics)
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@text_bp.route("/open_output_folder", methods=["GET"])
def open_output_folder():
    """Open the data/output folder in file explorer"""
    try:
        output_dir = ROOT_DIR / "data" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        import platform
        import subprocess
        
        if platform.system() == "Windows":
            subprocess.run(["explorer", str(output_dir)])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", str(output_dir)])
        else:  # Linux
            subprocess.run(["xdg-open", str(output_dir)])
        
        return jsonify({
            "success": True,
            "message": f"Folder dibuka: {output_dir}"
        })
    except Exception as exc:
        return jsonify({
            "success": False,
            "error": f"Gagal membuka folder: {str(exc)}"
        }), 500
