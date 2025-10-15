from __future__ import annotations

from pathlib import Path

from flask import Blueprint, jsonify, request

from server.config import clean_path, get_config

lists_bp = Blueprint("lists", __name__)


def _normalize_content(raw: str) -> str:
    lines = (line.rstrip() for line in raw.splitlines())
    normalized = "\n".join(lines)
    return normalized + ("\n" if normalized and not normalized.endswith("\n") else "")


def _ensure_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch()


@lists_bp.route("/manage_exclude_file", methods=["GET", "POST"])
def manage_exclude_file():
    try:
        config = get_config()
        exclude_path = config.get("EXCLUDE_FILE_PATH")
        if not exclude_path:
            return jsonify({"success": False, "error": "EXCLUDE_FILE_PATH tidak diset di config.json"}), 500

        file_path = Path(clean_path(exclude_path))

        if request.method == "GET":
            _ensure_file(file_path)
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            return jsonify({"success": True, "content": content})

        data = request.get_json(silent=True) or {}
        new_content = data.get("content", "")

        if len(new_content) > 200_000:
            return jsonify({"success": False, "error": "Konten terlalu besar."}), 400

        normalized = _normalize_content(new_content)
        _ensure_file(file_path)
        file_path.write_text(normalized, encoding="utf-8")
        return jsonify({"success": True, "message": "Daftar pengecualian berhasil disimpan."})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@lists_bp.route("/manage_just_me", methods=["GET", "POST"])
def manage_just_me():
    try:
        config = get_config()
        just_me_path = config.get("JUST_ME_FILE_PATH")
        if not just_me_path:
            return jsonify({"success": False, "error": "JUST_ME_FILE_PATH tidak diset di config.json"}), 500

        file_path = Path(clean_path(just_me_path))

        if request.method == "GET":
            _ensure_file(file_path)
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            return jsonify({"success": True, "content": content})

        data = request.get_json(silent=True) or {}
        new_content = data.get("content", "")

        if len(new_content) > 200_000:
            return jsonify({"success": False, "error": "Konten terlalu besar."}), 400

        normalized = _normalize_content(new_content)
        _ensure_file(file_path)
        file_path.write_text(normalized, encoding="utf-8")
        return jsonify({"success": True, "message": "Daftar just_me berhasil disimpan."})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500

