"""
Task Manager untuk Async File Processing
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional
import json


class TaskStatus:
    """Enum-like class untuk task status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskInfo:
    """Information tentang task yang sedang berjalan"""
    
    def __init__(self, task_id: str, task_type: str, params: Dict[str, Any]):
        self.task_id = task_id
        self.task_type = task_type
        self.params = params
        self.status = TaskStatus.PENDING
        self.progress = 0
        self.current_file = ""
        self.total_files = 0
        self.processed_files = 0
        self.start_time = None
        self.end_time = None
        self.error_message = ""
        self.result = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task info to dictionary for JSON serialization"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status,
            "progress": self.progress,
            "current_file": self.current_file,
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.get_duration(),
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    def get_duration(self) -> Optional[float]:
        """Get task duration in seconds"""
        if self.start_time:
            end_time = self.end_time or datetime.now()
            return (end_time - self.start_time).total_seconds()
        return None
    
    def update_progress(self, progress: int, current_file: str = "", processed_files: int = 0):
        """Update task progress"""
        self.progress = min(100, max(0, progress))
        self.current_file = current_file
        self.processed_files = processed_files
        self.updated_at = datetime.now()
    
    def start(self):
        """Mark task as started"""
        self.status = TaskStatus.RUNNING
        self.start_time = datetime.now()
        self.updated_at = self.start_time
    
    def complete(self, result: Any = None):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.end_time = datetime.now()
        self.result = result
        self.updated_at = self.end_time
    
    def fail(self, error_message: str):
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.end_time = datetime.now()
        self.error_message = error_message
        self.updated_at = self.end_time


class TaskManager:
    """
    Task Manager untuk mengelola async file processing tasks
    """
    
    def __init__(self, max_tasks: int = 10, cleanup_interval: int = 3600):
        self.tasks: Dict[str, TaskInfo] = {}
        self.max_tasks = max_tasks
        self.cleanup_interval = cleanup_interval
        self._lock = threading.Lock()
        self._start_cleanup_thread()
    
    def create_task(self, task_type: str, params: Dict[str, Any]) -> TaskInfo:
        """Create a new task"""
        with self._lock:
            # Clean up old tasks if at max capacity
            if len(self.tasks) >= self.max_tasks:
                self._cleanup_old_tasks()
            
            task_id = str(uuid.uuid4())
            task = TaskInfo(task_id, task_type, params)
            self.tasks[task_id] = task
            return task
    
    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update task properties"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.updated_at = datetime.now()
        return True
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all tasks as dictionary"""
        return {task_id: task.to_dict() for task_id, task in self.tasks.items()}
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Remove old completed/failed tasks"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        with self._lock:
            tasks_to_remove = []
            for task_id, task in self.tasks.items():
                if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] 
                    and task.updated_at < cutoff_time):
                    tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                del self.tasks[task_id]
        
        return len(tasks_to_remove)
    
    def _cleanup_old_tasks(self):
        """Internal cleanup method"""
        self.cleanup_old_tasks()
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_worker():
            while True:
                time.sleep(self.cleanup_interval)
                try:
                    removed_count = self.cleanup_old_tasks()
                    if removed_count > 0:
                        print(f"Cleaned up {removed_count} old tasks")
                except Exception as e:
                    print(f"Error during task cleanup: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def get_task_statistics(self) -> Dict[str, int]:
        """Get task statistics"""
        stats = {
            "total": len(self.tasks),
            TaskStatus.PENDING: 0,
            TaskStatus.RUNNING: 0,
            TaskStatus.COMPLETED: 0,
            TaskStatus.FAILED: 0,
            TaskStatus.CANCELLED: 0,
        }
        
        for task in self.tasks.values():
            if task.status in stats:
                stats[task.status] += 1
        
        return stats


# Global task manager instance
task_manager = TaskManager(max_tasks=20, cleanup_interval=1800)  # 30 minutes cleanup
