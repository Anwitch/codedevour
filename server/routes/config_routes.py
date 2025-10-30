from __future__ import annotations

import os
from tkinter import TclError, filedialog, Tk

from flask import Blueprint, jsonify, render_template, request

from server.config import (
    clean_path,
    get_config,
    is_allowed_path,
    save_config,
)
from server.services.gitignore_sync import sync_gitignore_to_exclude

config_bp = Blueprint("config_routes", __name__)


@config_bp.route("/")
def index():
    return render_template("Tree.html")


@config_bp.route("/set_path", methods=["POST"])
def set_project_path():
    try:
        payload = request.get_json(silent=True) or {}
        new_path = clean_path(payload.get("path", "")).strip()

        if not new_path or not os.path.isdir(new_path):
            return jsonify({"success": False, "error": "Path tidak valid atau tidak ditemukan."}), 400
        if not is_allowed_path(new_path):
            return jsonify({"success": False, "error": "Path tersebut tidak diizinkan."}), 403

        config = get_config()
        config["TARGET_FOLDER"] = new_path
        save_config(config)

        exclude_path = config.get("EXCLUDE_FILE_PATH", "")
        if sync_gitignore_to_exclude(new_path, exclude_path):
            message = "Path berhasil diatur dan pola .gitignore digabungkan."
        else:
            message = "Path berhasil diatur dan disimpan ke config.json."

        return jsonify({"success": True, "message": message})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


def _open_folder_dialog(title: str, initial_dir: str) -> str:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        chosen = filedialog.askdirectory(initialdir=initial_dir, title=title)
        return clean_path(chosen)
    finally:
        root.destroy()


@config_bp.route("/pick_folder", methods=["GET"])
def pick_folder():
    try:
        config = get_config()
        initial_dir = config.get("TARGET_FOLDER") or os.path.expanduser("~")
        chosen = _open_folder_dialog("Pilih folder proyek", initial_dir)

        if not chosen:
            return jsonify({"success": False, "error": "Pemilihan dibatalkan."}), 400
        if not is_allowed_path(chosen):
            return jsonify({"success": False, "error": "Path tersebut tidak diizinkan."}), 403

        config["TARGET_FOLDER"] = chosen
        save_config(config)

        exclude_path = config.get("EXCLUDE_FILE_PATH", "")
        if sync_gitignore_to_exclude(chosen, exclude_path):
            message = "Path diperbarui dari dialog dan pola .gitignore digabungkan."
        else:
            message = "Path diperbarui dari dialog."

        return jsonify({"success": True, "path": chosen, "message": message})
    except TclError as exc:
        return jsonify({"success": False, "error": f"Tidak bisa membuka dialog folder (no display?): {exc}"}), 500
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@config_bp.route("/pick_output_folder", methods=["GET"])
def pick_output_folder():
    try:
        config = get_config()
        output_file = config.get("OUTPUT_FILE") or ""
        initial_dir = os.path.dirname(output_file) if output_file else config.get("TARGET_FOLDER") or os.path.expanduser("~")
        chosen = _open_folder_dialog("Pilih folder output TextExtractor", initial_dir)

        if not chosen:
            return jsonify({"success": False, "error": "Pemilihan dibatalkan."}), 400
        if not os.path.isdir(chosen):
            return jsonify({"success": False, "error": "Folder tidak valid."}), 400

        return jsonify({"success": True, "path": chosen})
    except TclError as exc:
        return jsonify({"success": False, "error": f"Tidak bisa membuka dialog folder (no display?): {exc}"}), 500
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@config_bp.route("/config_summary", methods=["GET"])
def config_summary():
    try:
        config = get_config()
        output_path = (config.get("OUTPUT_FILE") or "").strip()
        target_folder = (config.get("TARGET_FOLDER") or "").strip()
        exclude_file = (config.get("EXCLUDE_FILE_PATH") or "").strip()
        just_me_file = (config.get("JUST_ME_FILE_PATH") or "").strip()
        
        return jsonify(
            {
                "success": True,
                "target_folder": target_folder,
                "output_file": output_path,
                "output_dir": os.path.dirname(output_path) if output_path else "",
                "output_name": os.path.basename(output_path) if output_path else "",
                "exclude_file": exclude_file,
                "just_me_file": just_me_file
            }
        )
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500

