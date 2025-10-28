"""
Task Routes untuk Async Processing
"""

from __future__ import annotations

import threading
import time
from flask import Blueprint, jsonify, request

from server.config import clean_path, get_config
from server.services.task_manager import task_manager, TaskInfo
from server.extractors.EnhancedTextExtractor import enhanced_combine_files_in_folder_recursive

task_bp = Blueprint("tasks", __name__)


def run_text_extraction_task(task_info: TaskInfo):
    """Background task untuk text extraction"""
    try:
        task_info.start()
        
        # Get configuration
        config = get_config()
        folder_path = clean_path(task_info.params.get("folder_path", ""))
        output_file = task_info.params.get("output_file", "Output.txt")
        exclude_file = config.get("EXCLUDE_FILE_PATH")
        formatted_output = task_info.params.get("formatted_output", True)
        
        # Update initial progress
        task_info.update_progress(1, "Initializing...")
        
        # Run extraction
        result = enhanced_combine_files_in_folder_recursive(
            folder_path=folder_path,
            output_file_name=output_file,
            exclude_file=exclude_file,
            formatted_output=formatted_output,
            task_info=task_info
        )
        
        if result["success"]:
            task_info.complete({
                "result": result,
                "message": f"Successfully processed {result['stats']['processed_files']} files"
            })
        else:
            task_info.fail(f"Extraction failed: {result['error']}")
            
    except Exception as exc:
        task_info.fail(f"Task failed with exception: {str(exc)}")


@task_bp.route("/start_extraction", methods=["POST"])
def start_extraction():
    """Start async text extraction task"""
    try:
        data = request.get_json(silent=True) or {}
        
        # Validate input
        folder_path = clean_path(data.get("folder_path", ""))
        if not folder_path:
            return jsonify({
                "success": False, 
                "error": "folder_path is required"
            }), 400
        
        output_file = data.get("output_file", "Output.txt")
        formatted_output = data.get("formatted_output", True)
        
        # Create task
        task_info = task_manager.create_task(
            task_type="text_extraction",
            params={
                "folder_path": folder_path,
                "output_file": output_file,
                "formatted_output": formatted_output
            }
        )
        
        # Start background task
        thread = threading.Thread(
            target=run_text_extraction_task,
            args=(task_info,),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            "success": True,
            "task_id": task_info.task_id,
            "message": "Text extraction started",
            "task_info": task_info.to_dict()
        })
        
    except Exception as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500


@task_bp.route("/task_status/<task_id>", methods=["GET"])
def get_task_status(task_id):
    """Get task status and progress"""
    try:
        task_info = task_manager.get_task(task_id)
        if not task_info:
            return jsonify({
                "success": False,
                "error": "Task not found"
            }), 404
        
        return jsonify({
            "success": True,
            "task_info": task_info.to_dict()
        })
        
    except Exception as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500


@task_bp.route("/all_tasks", methods=["GET"])
def get_all_tasks():
    """Get all tasks"""
    try:
        tasks = task_manager.get_all_tasks()
        stats = task_manager.get_task_statistics()
        
        return jsonify({
            "success": True,
            "tasks": tasks,
            "statistics": stats
        })
        
    except Exception as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500


@task_bp.route("/cancel_task/<task_id>", methods=["POST"])
def cancel_task(task_id):
    """Cancel a running task"""
    try:
        task_info = task_manager.get_task(task_id)
        if not task_info:
            return jsonify({
                "success": False,
                "error": "Task not found"
            }), 404
        
        # For now, we can only cancel pending tasks
        # In a full implementation, you'd need to send cancellation signal to the worker thread
        if task_info.status == "pending":
            task_info.status = "cancelled"
            task_info.end_time = time.time()
            return jsonify({
                "success": True,
                "message": "Task cancelled"
            })
        elif task_info.status == "running":
            return jsonify({
                "success": False,
                "error": "Cannot cancel running task (not implemented)"
            }), 400
        else:
            return jsonify({
                "success": False,
                "error": f"Cannot cancel {task_info.status} task"
            }), 400
            
    except Exception as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500


@task_bp.route("/cleanup_tasks", methods=["POST"])
def cleanup_tasks():
    """Clean up old completed tasks"""
    try:
        max_age_hours = request.get_json(silent=True) or {}
        max_age = max_age_hours.get("max_age_hours", 24)
        
        removed_count = task_manager.cleanup_old_tasks(max_age_hours=max_age)
        
        return jsonify({
            "success": True,
            "message": f"Cleaned up {removed_count} old tasks",
            "removed_count": removed_count
        })
        
    except Exception as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500


@task_bp.route("/task_result/<task_id>", methods=["GET"])
def get_task_result(task_id):
    """Get task result (for completed tasks)"""
    try:
        task_info = task_manager.get_task(task_id)
        if not task_info:
            return jsonify({
                "success": False,
                "error": "Task not found"
            }), 404
        
        if task_info.status != "completed":
            return jsonify({
                "success": False,
                "error": f"Task not completed yet, status: {task_info.status}"
            }), 400
        
        # Read output file if it exists
        output_file = task_info.params.get("output_file", "Output.txt")
        output_content = ""
        
        try:
            with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                output_content = f.read()
        except Exception:
            # File might not exist or couldn't be read
            pass
        
        return jsonify({
            "success": True,
            "result": {
                "task_info": task_info.to_dict(),
                "output_content": output_content,
                "output_file": output_file
            }
        })
        
    except Exception as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500
